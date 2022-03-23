import logging
from django.db.models.aggregates import Sum
from django.http.response import HttpResponse
import folium
import random
import math

from django.http import JsonResponse
from core.decorators import is_admin
from django.contrib.auth import get_user_model
from core.models import CarbureLot, Entity, UserRights, ProductionSite
from django.db.models import Q, Count
from django.core.mail import send_mail
from django.conf import settings

from core.models import UserRightsRequests
from core.common import get_transaction_distance
from doublecount.models import DoubleCountingAgreement
from api.v4.helpers import filter_lots

# Get an instance of a logger
logger = logging.getLogger(__name__)

@is_admin
def get_users(request):
    q = request.GET.get('q', False)
    entity_id = request.GET.get('entity_id', False)
    user_model = get_user_model()
    users = user_model.objects.all()

    if q:
        users = users.filter(Q(email__icontains=q) | Q(name__icontains=q))
    if entity_id:
        users = users.filter(userrights__entity__id=entity_id)

    users_sez = [{'email': u.email, 'name': u.name, 'id': u.id} for u in users]
    return JsonResponse({"status": "success", "data": users_sez})


@is_admin
def get_entity_details(request):
    entity_id = request.GET.get('entity_id', False)

    try:
        e = Entity.objects.get(pk=entity_id)
        return JsonResponse({"status": "success", "data": e.natural_key()})
    except Exception:
        return JsonResponse({"status": "error", "message": "Could not find entity" }, status=400)

@is_admin
def get_entity_production_sites(request):
    entity_id = request.GET.get('entity_id', False)

    try:
        psites = ProductionSite.objects.filter(producer__id=entity_id)
        psitesbyid = {p.id: p for p in psites}
        for k, v in psitesbyid.items():
            v.inputs = []
            v.outputs = []

        data = []

        for ps in psites:
            psite_data = ps.natural_key()
            psite_data['inputs'] = [i.natural_key() for i in ps.productionsiteinput_set.all()]
            psite_data['outputs'] = [o.natural_key() for o in ps.productionsiteoutput_set.all()]
            certificates = []
            for pc in ps.productionsitecertificate_set.all():
                certificates.append(pc.natural_key())
            psite_data['certificates'] = certificates
            data.append(psite_data)

        return JsonResponse({'status': 'success', 'data': data})
    except Exception:
        return JsonResponse({"status": "error", "message": "Could not find production sites" }, status=400)

@is_admin
def get_entity_depots(request):
    entity_id = request.GET.get('entity_id', False)

    try:
        e = Entity.objects.get(pk=entity_id)
        data = [ps.natural_key() for ps in e.entitydepot_set.all()]
        return JsonResponse({"status": "success", "data": data})
    except Exception:
        return JsonResponse({"status": "error", "message": "Could not find Entity Depots" }, status=400)

@is_admin
def get_entity_certificates(request):
    entity_id = request.GET.get('entity_id', False)

    try:
        e = Entity.objects.get(pk=entity_id)
        iscc = [ps.natural_key() for ps in e.entityiscctradingcertificate_set.all()]
        dbs = [ps.natural_key() for ps in e.entitydbstradingcertificate_set.all()]
        return JsonResponse({"status": "success", "data": iscc + dbs})
    except Exception:
        return JsonResponse({"status": "error", "message": "Could not find entity certificates" }, status=400)

@is_admin
def get_entities(request):
    q = request.GET.get('q', False)
    has_requests = request.GET.get('has_requests', None)

    entities = Entity.objects.all().order_by('name').prefetch_related('userrights_set', 'userrightsrequests_set', 'entitydepot_set', 'productionsite_set').annotate(
        users=Count('userrights', distinct=True),
        requests=Count('userrightsrequests', filter=Q(userrightsrequests__status='PENDING'), distinct=True),
        depots=Count('entitydepot', distinct=True),
        production_sites=Count('productionsite', distinct=True),
        certificates=Count('entitycertificate', distinct=True),
        double_counting=Count('doublecountingagreement', filter=Q(doublecountingagreement__status=DoubleCountingAgreement.ACCEPTED), distinct=True),
        double_counting_requests=Count('doublecountingagreement', filter=Q(doublecountingagreement__status=DoubleCountingAgreement.PENDING), distinct=True),
    )

    if q:
        entities = entities.filter(name__icontains=q)
    if has_requests == "true":
        entities = entities.filter(requests__gt=0)

    entities_sez = []
    for e in entities.iterator():
        entities_sez.append({
            'entity': e.natural_key(),
            'users': e.users,
            'requests': e.requests,
            'depots': e.depots,
            'production_sites': e.production_sites,
            'certificates': e.certificates,
            'double_counting': e.double_counting,
            'double_counting_requests': e.double_counting_requests
        })
    return JsonResponse({"status": "success", "data": entities_sez})


@is_admin
def add_entity(request):
    name = request.POST.get('name', False)
    entity_type = request.POST.get('category', False)

    if not name:
        return JsonResponse({'status': 'error', 'message': "Please provide a value in field name"}, status=400)
    if not entity_type:
        return JsonResponse({'status': 'error', 'message': "Please provide a value in field Category"}, status=400)

    if entity_type not in [c[0] for c in Entity.ENTITY_TYPES]:
        return JsonResponse({'status': 'error', 'message': "Unknown Category"}, status=400)

    try:
        obj, created = Entity.objects.update_or_create(name=name, entity_type=entity_type)
    except Exception:
        return JsonResponse({'status': 'error', 'message': "Unknown error. Please contact an administrator"}, status=400)
    return JsonResponse({'status': 'success', 'data': 'Entity created'})


@is_admin
def delete_entity(request):
    entity_id = request.POST.get('entity_id', False)

    if not entity_id:
        return JsonResponse({'status': 'error', 'message': "Please provide an entity_id"}, status=400)
    try:
        entity = Entity.objects.get(id=entity_id)
    except Exception:
        return JsonResponse({'status': 'error', 'message': "Could not find entity"}, status=400)

    entity.delete()
    return JsonResponse({"status": "success", "data": "success"})


@is_admin
def get_rights_requests(request):
    q = request.GET.get('q', False)
    statuses = request.GET.getlist('statuses', False)
    entity_id = request.GET.get('entity_id', False)
    requests = UserRightsRequests.objects.all()

    if entity_id:
        requests = requests.filter(entity__id=entity_id)
    if statuses:
        requests = requests.filter(status__in=statuses)
    if q:
        requests = requests.filter(Q(user__email__icontains=q) | Q(entity__name__icontains=q))

    requests_sez = [r.natural_key() for r in requests]
    return JsonResponse({"status": "success", "data": requests_sez})

@is_admin
def update_right_request(request):
    urr_id = request.POST.get('id', False)
    status = request.POST.get('status', False)
    if not urr_id:
        return JsonResponse({'status': 'error', 'message': "Please provide an id"}, status=400)
    if not status:
        return JsonResponse({'status': 'error', 'message': "Please provide a status"}, status=400)

    try:
        right_request = UserRightsRequests.objects.get(id=urr_id)
    except:
        return JsonResponse({'status': 'error', 'message': "Could not find request"}, status=400)

    right_request.status = status
    right_request.save()

    if status == 'ACCEPTED':
        UserRights.objects.update_or_create(entity=right_request.entity, user=right_request.user, defaults={'role': right_request.role, 'expiration_date': right_request.expiration_date})
        # send_mail
        email_subject = "Carbure - Demande acceptée"
        message = """
        Bonjour,

        Votre demande d'accès à la Société %s vient d'être validée par l'administration.

        """ % (right_request.entity.name)

        send_mail(
            subject=email_subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[right_request.user.email],
            fail_silently=False,
        )
    else:
        UserRights.objects.filter(entity=right_request.entity, user=request.user).delete()
    return JsonResponse({"status": "success"})


# def init_declaration(entity, declarations):
#     if entity in declarations:
#         return declarations[entity]
#     else:
#         declarations[entity] = {'drafts': 0, 'output': 0, 'input': 0, 'corrections': 0}
#         return declarations[entity]


# def get_period_declarations(period):
#     txs = LotTransaction.objects.filter(lot__period=period).select_related('carbure_vendor', 'carbure_client', 'lot__added_by').values(
#         'carbure_vendor__id', 'carbure_client__id', 'lot__added_by__id', 'delivery_status', 'lot__status')

#     entities = set()
#     declarations = {}

#     for tx in txs.iterator():
#         author = tx['lot__added_by__id']
#         vendor = tx['carbure_vendor__id'] if tx['carbure_vendor__id'] else None
#         client = tx['carbure_client__id'] if tx['carbure_client__id'] else None

#         if author and tx['lot__status'] == 'Draft':
#             entities.add(author)
#             declaration = init_declaration(author, declarations)
#             declaration['drafts'] += 1
#         else:
#             if client:
#                 entities.add(client)
#                 declaration = init_declaration(client, declarations)
#                 declaration['input'] += 1
#             if vendor:
#                 entities.add(vendor)
#                 declaration = init_declaration(vendor, declarations)
#                 declaration['output'] += 1
#             if author and tx['delivery_status'] in (LotTransaction.TOFIX, LotTransaction.REJECTED, LotTransaction.FIXED):
#                 entities.add(author)
#                 declaration = init_declaration(author, declarations)
#                 declaration['corrections'] += 1

#     return declarations

# @is_admin
# def get_declarations(request):
#     year = request.GET.get('year', False)
#     month = request.GET.get('month', False)
#     now = datetime.datetime.now()

#     if not month:
#         month = now.month
#     else:
#         month = int(month)

#     if not year:
#         year = now.year
#     else:
#         year = int(year)

#     #### CREATE DECLARATIONS IF MISSING
#     # we are in month N, we want to see period N-2, N-1 and N
#     ref_period = datetime.datetime(year=year, month=month, day=1)
#     periods = [ref_period, ref_period - relativedelta(months=1), ref_period - relativedelta(months=2)]
#     entities = Entity.objects.all()
#     to_create = []
#     for p in periods:
#         # calculate deadline date
#         nextmonth = p + datetime.timedelta(days=31)
#         (weekday, lastday) = calendar.monthrange(nextmonth.year, nextmonth.month)
#         deadline = datetime.date(year=nextmonth.year, month=nextmonth.month, day=lastday)
#         # 1) get existing objects
#         sds = SustainabilityDeclaration.objects.filter(period=p)
#         existing = {s.entity.id: s for s in sds}

#         # 2) check if all entities have a declaration
#         for e in entities:
#             if e.id not in existing:
#                 to_create.append(SustainabilityDeclaration(entity=e, period=p, deadline=deadline))

#     # 3) create objects if missing
#     SustainabilityDeclaration.objects.bulk_create(to_create)


#     #### FETCH DECLARATIONS FROM DB
#     declarations = SustainabilityDeclaration.objects.filter(entity__in=entities, period__in=periods).select_related('entity')
#     tx_counts = {}
#     for p in periods:
#         period = "%d-%02d" % (p.year, p.month)
#         tx_counts[period] = get_period_declarations(period)

#     declarations_sez = []
#     for d in declarations:
#         period = "%d-%02d" % (d.period.year, d.period.month)
#         if d.entity.id in tx_counts[period]:
#             d.lots = tx_counts[period][d.entity.id]
#         else:
#             d.lots = {'drafts': 0, 'output': 0, 'input': 0, 'corrections': 0}
#         sez_data = d.natural_key()
#         sez_data['lots'] = d.lots
#         declarations_sez.append(sez_data)
#     return JsonResponse({"status": "success", "data": declarations_sez})


# @is_admin
# def send_declaration_reminder(request):
#     entity_id = request.POST.get('entity_id', False)
#     year = request.POST.get('year', False)
#     month = request.POST.get('month', False)

#     if not entity_id:
#         return JsonResponse({'status': 'error', 'message': "Missing entity_id"}, status=400)

#     if not year:
#         return JsonResponse({'status': 'error', 'message': "Missing year"}, status=400)

#     if not month:
#         return JsonResponse({'status': 'error', 'message': "Missing month"}, status=400)


#     try:
#         period = datetime.date(year=int(year), month=int(month), day=1)
#         declaration = SustainabilityDeclaration.objects.get(entity__id=entity_id, period=period, declared=False)
#     except Exception:
#         return JsonResponse({'status': 'error', 'message': "Could not find declaration"}, status=400)

#     declaration.reminder_count += 1
#     declaration.save()

#     context = {}
#     context['entity_id'] = entity_id
#     context['lots_validated'] = LotV2.objects.filter(added_by=declaration.entity, status='Validated').count()
#     period = declaration.period.strftime('%Y-%m')
#     context['PERIOD'] = period
#     email_subject = 'Carbure - Déclaration %s' % (period)
#     html_message = render_to_string('emails/relance_manuelle_fr.html', context)
#     text_message = render_to_string('emails/relance_manuelle_fr.txt', context)
#     rights = UserRights.objects.filter(entity__id=entity_id)
#     recipients = [r.user.email for r in rights]

#     send_mail(
#         subject=email_subject,
#         message=text_message,
#         from_email=settings.DEFAULT_FROM_EMAIL,
#         html_message=html_message,
#         recipient_list=recipients,
#         fail_silently=False,
#     )

#     return JsonResponse({"status": "success"})


# @is_admin
# def check_declaration(request):
#     id = request.POST.get('id', False)
#     if not id:
#         return JsonResponse({'status': 'error', 'message': "Please provide the declaration id"}, status=400)

#     try:
#         dec = SustainabilityDeclaration.objects.get(id=id)
#     except:
#         return JsonResponse({'status': 'error', 'message': "Could not find declaration"}, status=400)

#     dec.checked = True
#     dec.save()
#     return JsonResponse({"status": "success"})


# @is_admin
# def uncheck_declaration(request):
#     id = request.POST.get('id', False)
#     if not id:
#         return JsonResponse({'status': 'error', 'message': "Please provide the declaration id"}, status=400)

#     try:
#         dec = SustainabilityDeclaration.objects.get(id=id)
#     except:
#         return JsonResponse({'status': 'error', 'message': "Could not find declaration"}, status=400)

#     dec.checked = False
#     dec.save()
#     return JsonResponse({"status": "success"})


# @is_admin
# def ack_alerts(request):
#     alert_ids = request.POST.getlist('alert_ids', False)
#     if not alert_ids:
#         return JsonResponse({'status': 'forbidden', 'message': "Missing alert_ids"}, status=400)

#     GenericError.objects.filter(id__in=alert_ids).update(acked_by_admin=True)
#     return JsonResponse({'status': 'success'})



# @is_admin
# def highlight_alerts(request):
#     alert_ids = request.POST.getlist('alert_ids', False)
#     if not alert_ids:
#         return JsonResponse({'status': 'forbidden', 'message': "Missing alert_ids"}, status=400)

#     GenericError.objects.filter(id__in=alert_ids).update(highlighted_by_admin=True)
#     return JsonResponse({'status': 'success'})


# @is_admin
# def highlight_transactions(request):
#     tx_ids = request.POST.getlist('tx_ids', False)
#     notify_auditor = request.POST.get('notify_auditor', False)

#     if not tx_ids:
#         return JsonResponse({'status': 'forbidden', 'message': "Missing tx_ids"}, status=400)

#     txs = LotTransaction.objects.filter(id__in=tx_ids)

#     for tx in txs.iterator():
#         tx.highlighted_by_admin = not tx.highlighted_by_admin
#         if tx.highlighted_by_admin:
#             tx.hidden_by_admin = False
#         if notify_auditor == 'true':
#             tx.highlighted_by_auditor = True
#         tx.save()

#     return JsonResponse({'status': 'success'})

# @is_admin
# def hide_transactions(request):
#     tx_ids = request.POST.getlist('tx_ids', False)

#     if not tx_ids:
#         return JsonResponse({'status': 'forbidden', 'message': "Missing tx_ids"}, status=400)

#     txs = LotTransaction.objects.filter(id__in=tx_ids)

#     for tx in txs.iterator():
#         tx.hidden_by_admin = not tx.hidden_by_admin
#         if tx.hidden_by_admin:
#             tx.highlighted_by_admin = False
#         tx.save()
#         tx.genericerror_set.all().update(acked_by_admin=True)
#     return JsonResponse({'status': 'success'})


# @is_admin
# def admin_comment_transaction(request):
#     entity_id = request.POST.get('entity_id', False)
#     tx_ids = request.POST.getlist('tx_ids', False)
#     comment = request.POST.get('comment', False)
#     is_visible_by_auditor = request.POST.get('is_visible_by_auditor', False)
#     if is_visible_by_auditor == 'true':
#         is_visible_by_auditor = True
#     else:
#         is_visible_by_auditor = False

#     if not entity_id:
#         return JsonResponse({'status': 'error', 'message': "Missing entity_id"}, status=400)
#     if not tx_ids:
#         return JsonResponse({'status': 'error', 'message': "Missing tx_ids"}, status=400)
#     if not comment:
#         return JsonResponse({'status': 'error', 'message': "Missing comment"}, status=400)

#     for tx_id in tx_ids:
#         tx = LotTransaction.objects.get(id=tx_id)
#         c = AdminTransactionComment()
#         c.tx = tx
#         c.comment = comment
#         c.entity_id = entity_id
#         c.is_visible_by_admin = True
#         c.is_visible_by_auditor = is_visible_by_auditor
#         c.save()
#     return JsonResponse({'status': 'success'})


# @is_admin
# def admin_delete_transactions(request):
#     tx_ids = request.POST.getlist('tx_ids', False)

#     if not tx_ids:
#         return JsonResponse({'status': 'error', 'message': "Missing tx_ids"}, status=400)

#     for tx_id in tx_ids:
#         tx = LotTransaction.objects.get(id=tx_id)
#         lot_id = tx.lot.id
#         tx.delete()
#         lot = LotV2.objects.get(id=lot_id)
#         remaining_tx = LotTransaction.objects.filter(lot=lot).count()
#         if remaining_tx == 0:
#             lot.delete()
#     return JsonResponse({'status': 'success'})


# not an api endpoint
def couleur():
    liste = ["#FF0040","#DF01A5","#BF00FF","#4000FF","#0040FF","#00BFFF",
              "#00FFBF","#00FF40","#40FF00","#BFFF00","#FFBF00","#FF4000",
              "#FA5858","#FAAC58","#F4FA58","#ACFA58","#58FA58","#58FAAC",
              "#58FAF4","#58ACFA","#5858FA","#AC58FA","#FA58F4","#FA58AC",
              "#B40404","#B45F04","#AEB404","#5FB404","#04B45F","#04B4AE",
              "#045FB4","#0404B4","#5F04B4","#B404AE","#B4045F","#8A0829"]
    return random.choice(liste)

# not an api endpoint
def grade(volume, min, max):
    #print(volume, min, max)
    weight = math.log(volume) / 5
    #print(weight)
    # 2 < x < 4
    # min < volume < max
    return weight

@is_admin
def map(request):
    admin_entities_rights = UserRights.objects.filter(user=request.user, entity__entity_type=Entity.ADMIN)
    entity = admin_entities_rights[0].entity
    lots = CarbureLot.objects.select_related(
        'carbure_producer', 'carbure_production_site', 'production_country',
        'feedstock', 'biofuel', 'country_of_origin', 'added_by',
        'carbure_supplier', 'carbure_client', 'carbure_delivery_site', 'delivery_site_country',
    ).filter(lot_status__in=[CarbureLot.ACCEPTED, CarbureLot.FROZEN, CarbureLot.PENDING])
    lots = filter_lots(lots, request.GET, entity)

    # on veut: nom site de depart, gps depart, nom site arrivee, gps arrivee, volume
    lots = lots.filter(carbure_production_site__isnull=False, carbure_delivery_site__isnull=False)
    values = lots.values('carbure_production_site__name', 'carbure_production_site__gps_coordinates', 'carbure_delivery_site__name', 'carbure_delivery_site__gps_coordinates').annotate(volume=Sum('volume'))

    volume_min = 999999
    volume_max = 0
    for v in values:
        volume = v['volume']
        if volume < volume_min:
            volume_min = volume
        if volume > volume_max:
            volume_max = volume

    m = folium.Map(location=[46.227638, 2.213749], zoom_start=5)
    known_prod_sites = []
    known_depots = []
    for v in values:
        try:
            # start coordinates
            slat, slon = v['carbure_production_site__gps_coordinates'].split(',')
            # end coordinates
            elat, elon = v['carbure_delivery_site__gps_coordinates'].split(',')
        except:
            print('Missing start or end gps coordinates')
            print('Start %s : %s' % (v['carbure_production_site__name'].encode('utf-8'), v['carbure_production_site__gps_coordinates']))
            print('End %s : %s' % (v['carbure_delivery_site__name'].encode('utf-8'), v['carbure_delivery_site__gps_coordinates']))
            continue

        if v['carbure_production_site__gps_coordinates'] not in known_prod_sites:
            known_prod_sites.append(v['carbure_production_site__gps_coordinates'])
            c = couleur()
            folium.Circle(
                radius=50e2,
                location=[slat, slon],
                popup=v['carbure_production_site__name'],
                color= c,
                fill=True,
                fill_opacity=1,
            ).add_to(m)
        if v['carbure_delivery_site__gps_coordinates'] not in known_depots:
            known_depots.append(v['carbure_delivery_site__gps_coordinates'])
            folium.Circle(
                radius=50e2,
                location=[elat, elon],
                popup=v['carbure_delivery_site__name'],
                color="white",
                fill=True,
                fill_opacity=1,
            ).add_to(m)
        volume = v['volume']
        folium.PolyLine([(float(slat),float(slon)),(float(elat),float(elon))], color=c, weight=grade(volume, volume_min, volume_max), line_cap='round', opacity=0.7, popup=v['carbure_production_site__name']+' vers '+v['carbure_delivery_site__name']+' : \n'+str(volume)+' litres').add_to(m)
    return HttpResponse(m._repr_html_())

