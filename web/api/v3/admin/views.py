import logging
import datetime
from django.db.models.aggregates import Sum
from django.http.response import HttpResponse
import pytz
import calendar
from dateutil.rrule import rrule, MONTHLY
from dateutil.relativedelta import relativedelta
import folium
import random
import math

from django.http import JsonResponse
from core.decorators import is_admin
from django.contrib.auth import get_user_model
from core.models import Entity, UserRights, Control, ControlMessages, ProductionSite, LotV2, GenericError
from django.db.models import Q, Count, Subquery, OuterRef, Value, IntegerField
from django.contrib.auth.forms import PasswordResetForm
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string

from core.models import LotTransaction, UserRightsRequests, SustainabilityDeclaration, Control
from api.v3.lots.helpers import get_lots_with_metadata, get_lots_with_errors, get_snapshot_filters, get_errors, filter_lots, get_general_summary, sort_lots
from core.common import check_certificates, get_transaction_distance


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
                c = pc.certificate_iscc.certificate if pc.type == 'ISCC' else pc.certificate_2bs.certificate
                certificates.append({'certificate_id': c.certificate_id, 'holder': c.certificate_holder, 'type': pc.type})
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

    entities = Entity.objects.all().order_by('name')

    if q:
        entities = entities.filter(name__icontains=q)
    if has_requests == "true":
        requests = Count('userrightsrequests', filter=Q(userrightsrequests__status='PENDING'))
        entities = entities.annotate(requests=requests)
        entities = entities.filter(requests__gt=0)

    entities_sez = []
    for e in entities:
        entities_sez.append({
            'entity': e.natural_key(),
            'users': e.userrights_set.count(),
            'requests': e.userrightsrequests_set.filter(status='PENDING').count(),
            'depots': e.entitydepot_set.count(),
            'production_sites': e.productionsite_set.count(),
            'certificates_iscc': e.entityiscctradingcertificate_set.count(),
            'certificates_2bs': e.entitydbstradingcertificate_set.count(),
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


def get_lots_by_status(txs, querySet):
    status = querySet.get('status', False)
    hidden = querySet.get('is_hidden_by_admin', None)

    if status == 'alert':
        txs = get_lots_with_errors(txs)
    elif status == 'correction':
        txs = txs.filter(delivery_status__in=[LotTransaction.TOFIX, LotTransaction.REJECTED, LotTransaction.FIXED])
    elif status == 'declaration':
        txs = txs.filter(delivery_status__in=[LotTransaction.ACCEPTED, LotTransaction.PENDING, LotTransaction.FROZEN])
    elif status == 'highlight':
        txs = txs.filter(highlighted_by_admin=True)

    if hidden is None:
        txs = txs.filter(hidden_by_admin=False)

    return txs


@is_admin
def get_lots(request):
    status = request.GET.get('status', False)

    if not status:
        return JsonResponse({'status': 'error', 'message': "Please provide a status"}, status=400)

    try:
        txs = LotTransaction.objects.select_related(
            'lot', 'lot__carbure_producer', 'lot__carbure_production_site', 'lot__carbure_production_site__country',
            'lot__unknown_production_country', 'lot__matiere_premiere', 'lot__biocarburant', 'lot__pays_origine', 'lot__added_by', 'lot__data_origin_entity',
            'carbure_vendor', 'carbure_client', 'carbure_delivery_site', 'unknown_delivery_site_country', 'carbure_delivery_site__country'
        ).prefetch_related('genericerror_set', 'lot__carbure_production_site__productionsitecertificate_set')

        txs = txs.filter(lot__status=LotV2.VALIDATED)
        txs = get_lots_by_status(txs, request.GET)
        return get_lots_with_metadata(txs, None, request.GET, admin=True)

    except Exception:
        import traceback
        traceback.print_exc()
        return JsonResponse({'status': 'error', 'message': "Something went wrong"}, status=400)


@is_admin
def get_lots_summary(request, *args, **kwargs):
    try:
        txs = LotTransaction.objects.filter(lot__status=LotV2.VALIDATED)
        txs = get_lots_by_status(txs, request.GET)
        txs = filter_lots(txs, request.GET)[0]
        txs = sort_lots(txs, request.GET)
        data = get_general_summary(txs)
        return JsonResponse({'status': 'success', 'data': data})
    except Exception:
        return JsonResponse({'status': 'error', 'message': "Could not get lots summary"}, status=400)


@is_admin
def get_details(request, *args, **kwargs):
    tx_id = request.GET.get('tx_id', False)

    if not tx_id:
        return JsonResponse({'status': 'error', 'message': 'Missing tx_id'}, status=400)

    tx = LotTransaction.objects.get(pk=tx_id)

    now = datetime.datetime.now()
    (_, last_day) = calendar.monthrange(now.year, now.month)
    deadline_date = now.replace(day=last_day)

    data = {}
    data['transaction'] = tx.natural_key(admin=True)
    data['certificates'] = check_certificates(tx)
    try:
        data['distance'] = get_transaction_distance(tx)
    except:
        data['distance'] = {'distance': 0, 'link': ''}
    data['errors'] = get_errors(tx)
    data['deadline'] = deadline_date.strftime("%Y-%m-%d")
    data['comments'] = [c.natural_key() for c in tx.transactioncomment_set.all()]
    data['updates'] = [c.natural_key() for c in tx.transactionupdatehistory_set.all().order_by('-datetime')]
    return JsonResponse({'status': 'success', 'data': data})


@is_admin
def get_snapshot(request):
    year = request.GET.get('year', False)

    today = datetime.date.today()
    date_from = today.replace(month=1, day=1)
    date_until = today.replace(month=12, day=31)

    if year:
        try:
            year = int(year)
            date_from = datetime.date(year=year, month=1, day=1)
            date_until = datetime.date(year=year, month=12, day=31)
        except Exception:
            return JsonResponse({'status': 'error', 'message': 'Incorrect format for year. Expected YYYY'}, status=400)

    try:
        data = {}
        txs = LotTransaction.objects.all()
        data['years'] = [t.year for t in txs.dates('delivery_date', 'year')]
        txs = txs.filter(lot__status='Validated', delivery_date__gte=date_from, delivery_date__lte=date_until)

        alerts = txs.annotate(Count('genericerror')).filter(genericerror__count__gt=0).count()
        correction = txs.filter(delivery_status__in=[LotTransaction.TOFIX, LotTransaction.REJECTED, LotTransaction.FIXED]).count()
        declaration = txs.filter(delivery_status__in=[LotTransaction.ACCEPTED, LotTransaction.PENDING, LotTransaction.FROZEN]).count()
        highlight = txs.filter(highlighted_by_admin=True).count()
        data['lots'] = {'alert': alerts, 'correction': correction, 'declaration': declaration, 'highlight': highlight}
        data['filters'] = [
            'delivery_status',
            'periods',
            'biocarburants',
            'matieres_premieres',
            'countries_of_origin',
            'vendors',
            'clients',
            'production_sites',
            'delivery_sites',
            'added_by',
            'errors',
            'is_forwarded',
            'is_mac',
            'is_hidden_by_admin',
            'client_types'
        ]
    except Exception:
        return JsonResponse({'status': 'error', 'message': "Exception"}, status=400)
    return JsonResponse({"status": "success", "data": data})


@is_admin
def get_filters(request, *args, **kwargs):
    field = request.GET.get('field', False)
    if not field:
        return JsonResponse({'status': 'error', 'message': "Missing field"}, status=400)

    txs = LotTransaction.objects.filter(lot__status=LotV2.VALIDATED)
    txs = get_lots_by_status(txs, request.GET)
    txs = filter_lots(txs, request.GET, [field])[0]
    d = get_snapshot_filters(txs, None, [field])
    if field in d:
        values = d[field]
    else:
        return JsonResponse({'status': 'error', 'message': "Something went wrong"}, status=400)
    return JsonResponse({'status': 'success', 'data': values})


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

        """ % (request.entity.name)

        send_mail(
            subject=email_subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[request.user.email],
            fail_silently=False,
        )
    else:
        UserRights.objects.filter(entity=request.entity, user=request.user).delete()
    return JsonResponse({"status": "success"})


@is_admin
def get_certificates(request):
    return JsonResponse({"status": "success"})


@is_admin
def update_certificate(request):
    return JsonResponse({"status": "success"})


@is_admin
def get_controls(request):
    q = request.GET.get('q', False)
    status = request.GET.get('status', False)

    controls = Control.objects.all()
    if q:
        controls = controls.filter(Q(tx__lot__carbure_producer__name__icontains=q) |
                                   Q(tx__carbure_client__name__icontains=q))
    if status:
        controls = controls.filter(status=status)
    controls_sez = [r.natural_key() for r in controls]
    return JsonResponse({"status": "success", "data": controls_sez})


@is_admin
def open_control(request):
    tx_id = request.POST.get('tx_id', False)
    if not tx_id:
        return JsonResponse({'status': 'error', 'message': "Please provide a source tx_id"}, status=400)

    try:
        tx = LotTransaction.objects.get(id=tx_id)
    except:
        return JsonResponse({'status': 'error', 'message': "Could not find tx associated with tx_id"}, status=400)

    ctrl = Control()
    ctrl.tx = tx
    ctrl.status = 'OPEN'
    ctrl.save()
    return JsonResponse({"status": "success"})


@is_admin
def close_control(request):
    ctrl_id = request.POST.get('id', False)
    if not ctrl_id:
        return JsonResponse({'status': 'error', 'message': "Please provide a control id"}, status=400)

    try:
        ctrl = Control.objects.get(id=ctrl_id)
    except:
        return JsonResponse({'status': 'error', 'message': "Could not find control"}, status=400)

    ctrl.status = 'CLOSED'
    ctrl.save()
    return JsonResponse({"status": "success"})

def get_period_declarations(period):
    txs = LotTransaction.objects.filter(lot__period=period)

    txs_drafts = txs.filter(lot__added_by=OuterRef('pk'), lot__status='Draft').values('lot__added_by').annotate(total=Count(Value(1)))
    txs_output = txs.filter(carbure_vendor=OuterRef('pk'), lot__status='Validated').values('carbure_vendor').annotate(total=Count(Value(1)))
    txs_input = txs.filter(carbure_client=OuterRef('pk'), lot__status='Validated').values('carbure_client').annotate(total=Count(Value(1)))
    txs_corrections = txs.filter(lot__added_by=OuterRef('pk'), lot__status='Validated', delivery_status__in=['AC', 'R', 'AA']).values('lot__added_by').annotate(total=Count(Value(1)))

    # for each entity, run a subquery to count the number of tx depending on their status
    tx_counts = Entity.objects.annotate(
            drafts=Subquery(txs_drafts.values('total')),
            output=Subquery(txs_output.values('total')),
            input=Subquery(txs_input.values('total')),
            corrections=Subquery(txs_corrections.values('total'))
        ).values('id', 'drafts', 'output', 'input', 'corrections')

    by_entity = {}

    for c in tx_counts:
        by_entity[c['id']] = {
            'drafts': c['drafts'] if c['drafts'] else 0,
            'output': c['output'] if c['output'] else 0,
            'input': c['input'] if c['input'] else 0,
            'corrections': c['corrections'] if c['corrections'] else 0
        }

    return by_entity

@is_admin
def get_declarations(request):
    year = request.GET.get('year', False)
    month = request.GET.get('month', False)
    now = datetime.datetime.now()

    if not month:
        month = now.month
    else:
        month = int(month)

    if not year:
        year = now.year
    else:
        year = int(year)

    # we are in month N, we want to see period N-2, N-1 and N
    ref_period = datetime.datetime(year=year, month=month, day=1)
    nb_periods = 3
    declaration_periods = []
    for i in range(nb_periods):
        declaration_periods.append(ref_period - relativedelta(months=1 * i))
    periods = [(d.month, d.year) for d in declaration_periods]
    periods.reverse()
    start = declaration_periods[-1]
    end = ref_period + relativedelta(months=1) - relativedelta(days=1)

    start = pytz.utc.localize(start)
    end = pytz.utc.localize(end)

    # get entities that have posted at least one lot since the beginning of the period
    operators = [e.id for e in Entity.objects.filter(entity_type=Entity.OPERATOR)]
    entities_alive = [f['lot__added_by'] for f in LotTransaction.objects.filter(lot__added_time__gt=start).values('lot__added_by').annotate(count=Count('lot')).filter(count__gt=1)]
    to_display = list(set(operators + entities_alive))
    entities = Entity.objects.filter(id__in=to_display)

    # create the SustainabilityDeclaration objects in database
    # 0) cleanup
    # SustainabilityDeclaration.objects.filter(checked=False).delete()
    # 1) get existing objects
    sds = SustainabilityDeclaration.objects.filter(entity__in=entities, period__gte=start, period__lte=end)
    existing = {}
    for sd in sds:
        key = '%d.%d.%d' % (sd.entity.id, sd.period.year, sd.period.month)
        existing[key] = sd
    # 2) create target objects
    targets = {}
    for month, year in periods:
        period = datetime.date(year=year, month=month, day=1)
        nextmonth = period + relativedelta(months=1)
        (_, last_day) = calendar.monthrange(nextmonth.year, nextmonth.month)
        deadline_date = nextmonth.replace(day=last_day)
        for e in entities:
            key = '%d.%d.%d' % (e.id, year, month)
            targets[key] =  SustainabilityDeclaration(entity=e, period=period, deadline=deadline_date)
    # 3) remove existing objects from targets
    for key, sd in existing.items():
        if key in targets:
            del targets[key]
    # 4) if any, bulk create the targets
    if len(targets):
        to_create = list(targets.values())
        logging.debug('will create {} declarations'.format(len(to_create)))

        for t in to_create:
            logging.debug(t.natural_key())
        SustainabilityDeclaration.objects.bulk_create(to_create)
        sds = SustainabilityDeclaration.objects.filter(entity__in=entities, period__gte=start, period__lte=end)
    else:
        logging.debug('no new declaration objects to create. Existing {}'.format(len(existing)))

    # get the declarations objects from db
    declarations = SustainabilityDeclaration.objects.filter(entity__in=entities, period__gte=start, period__lte=end)

    tx_counts = {}

    for month, year in periods:
        period = "%d-%02d" % (year, month)
        tx_counts[period] = get_period_declarations(period)

    # query lots to enrich declarations on the frontend
    # expected return ['client1': [{'period': '2020-01', 'drafts': 200, 'validated': 100, 'checked': True}, {'period': '2020-02', 'drafts': 50, 'validated': 10, 'checked': False}]]
    # 1) get the lots grouped by added_by
    # drafts = Count('id', filter=Q(lot__status='Draft'))
    # validated = Count('id', filter=Q(lot__status='Validated', delivery_status__in=['N'] ))
    # received = Count('id', filter=Q(lot__status='Validated', delivery_status__in=['A']))
    # corrections = Count('id', filter=Q(lot__status='Validated', delivery_status__in=['R', 'AC', 'AA']))
    # lots = LotTransaction.objects.values('lot__added_by__id', 'lot__added_by__name', 'lot__period').annotate(drafts=drafts, validated=validated, received=received, corrections=corrections)
    # batches = {'%s.%s' % (batch['lot__added_by__id'], batch['lot__period']): batch for batch in lots }

    # 2) add batch info to each declarations
    declarations_sez = []
    for d in declarations:
        period = "%d-%02d" % (d.period.year, d.period.month)

        if d.entity.id in tx_counts[period]:
            d.lots = tx_counts[period][d.entity.id]
        else:
            d.lots = {'drafts': 0, 'output': 0, 'input': 0, 'corrections': 0}
        sez_data = d.natural_key()
        sez_data['lots'] = d.lots
        declarations_sez.append(sez_data)
    return JsonResponse({"status": "success", "data": declarations_sez})


@is_admin
def send_declaration_reminder(request):
    entity_id = request.POST.get('entity_id', False)
    year = request.POST.get('year', False)
    month = request.POST.get('month', False)

    if not entity_id:
        return JsonResponse({'status': 'error', 'message': "Missing entity_id"}, status=400)

    if not year:
        return JsonResponse({'status': 'error', 'message': "Missing year"}, status=400)

    if not month:
        return JsonResponse({'status': 'error', 'message': "Missing month"}, status=400)


    try:
        period = datetime.date(year=int(year), month=int(month), day=1)
        declaration = SustainabilityDeclaration.objects.get(entity__id=entity_id, period=period, declared=False)
    except Exception:
        return JsonResponse({'status': 'error', 'message': "Could not find declaration"}, status=400)

    declaration.reminder_count += 1
    declaration.save()

    context = {}
    context['entity_id'] = entity_id
    context['lots_validated'] = LotV2.objects.filter(added_by=declaration.entity, status='Validated').count()
    period = declaration.period.strftime('%Y-%m')
    context['PERIOD'] = period
    email_subject = 'Carbure - Déclaration %s' % (period)
    html_message = render_to_string('emails/relance_manuelle_fr.html', context)
    text_message = render_to_string('emails/relance_manuelle_fr.txt', context)
    rights = UserRights.objects.filter(entity__id=entity_id)
    recipients = [r.user.email for r in rights]

    send_mail(
        subject=email_subject,
        message=text_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        html_message=html_message,
        recipient_list=recipients,
        fail_silently=False,
    )

    return JsonResponse({"status": "success"})


@is_admin
def check_declaration(request):
    id = request.POST.get('id', False)
    if not id:
        return JsonResponse({'status': 'error', 'message': "Please provide the declaration id"}, status=400)

    try:
        dec = SustainabilityDeclaration.objects.get(id=id)
    except:
        return JsonResponse({'status': 'error', 'message': "Could not find declaration"}, status=400)

    dec.checked = True
    dec.save()
    return JsonResponse({"status": "success"})


@is_admin
def uncheck_declaration(request):
    id = request.POST.get('id', False)
    if not id:
        return JsonResponse({'status': 'error', 'message': "Please provide the declaration id"}, status=400)

    try:
        dec = SustainabilityDeclaration.objects.get(id=id)
    except:
        return JsonResponse({'status': 'error', 'message': "Could not find declaration"}, status=400)

    dec.checked = False
    dec.save()
    return JsonResponse({"status": "success"})

@is_admin
def controls_add_message(request):
    control_id = request.POST.get('control_id', False)
    message = request.POST.get('message', False)

    if not control_id:
        return JsonResponse({'status': 'error', 'message': 'Please submit a control_id'}, status=400)
    if not message:
        return JsonResponse({'status': 'error', 'message': 'Please submit a message'}, status=400)

    try:
        control = Control.objects.get(id=control_id)
    except:
        return JsonResponse({'status': 'error', 'message': 'Could not find control'}, status=400)

    # all good
    msg = ControlMessages()
    msg.control = control
    msg.user = request.user
    msg.entity = Entity.objects.filter(entity_type='Administrateur')[0]
    msg.message = message
    msg.save()
    return JsonResponse({'status': 'success'})



@is_admin
def ack_alerts(request):
    alert_ids = request.POST.getlist('alert_ids', False)
    if not alert_ids:
        return JsonResponse({'status': 'forbidden', 'message': "Missing alert_ids"}, status=400)

    GenericError.objects.filter(id__in=alert_ids).update(acked_by_admin=True)
    return JsonResponse({'status': 'success'})



@is_admin
def highlight_alerts(request):
    alert_ids = request.POST.getlist('alert_ids', False)
    if not alert_ids:
        return JsonResponse({'status': 'forbidden', 'message': "Missing alert_ids"}, status=400)

    GenericError.objects.filter(id__in=alert_ids).update(highlighted_by_admin=True)
    return JsonResponse({'status': 'success'})


@is_admin
def highlight_transactions(request):
    tx_ids = request.POST.getlist('tx_ids', False)
    notify_auditor = request.POST.get('notify_auditor', False)

    if not tx_ids:
        return JsonResponse({'status': 'forbidden', 'message': "Missing tx_ids"}, status=400)

    txs = LotTransaction.objects.filter(id__in=tx_ids)

    for tx in txs.iterator():
        tx.highlighted_by_admin = not tx.highlighted_by_admin
        if tx.highlighted_by_admin:
            tx.hidden_by_admin = False
        if notify_auditor == 'true':
            tx.highlighted_by_auditor = True
        tx.save()

    return JsonResponse({'status': 'success'})

@is_admin
def hide_transactions(request):
    tx_ids = request.POST.getlist('tx_ids', False)

    if not tx_ids:
        return JsonResponse({'status': 'forbidden', 'message': "Missing tx_ids"}, status=400)

    txs = LotTransaction.objects.filter(id__in=tx_ids)

    for tx in txs.iterator():
        tx.hidden_by_admin = not tx.hidden_by_admin
        if tx.hidden_by_admin:
            tx.highlighted_by_admin = False
        tx.save()
        tx.genericerror_set.all().update(acked_by_admin=True)
    return JsonResponse({'status': 'success'})


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
    txs = LotTransaction.objects.select_related(
        'lot', 'lot__carbure_producer', 'lot__carbure_production_site', 'lot__carbure_production_site__country',
        'lot__unknown_production_country', 'lot__matiere_premiere', 'lot__biocarburant', 'lot__pays_origine', 'lot__added_by', 'lot__data_origin_entity',
        'carbure_vendor', 'carbure_client', 'carbure_delivery_site', 'unknown_delivery_site_country', 'carbure_delivery_site__country'
    ).prefetch_related('genericerror_set', 'lot__carbure_production_site__productionsitecertificate_set')
    txs = txs.filter(lot__status=LotV2.VALIDATED, delivery_status__in=[LotTransaction.ACCEPTED, LotTransaction.PENDING, LotTransaction.FROZEN])
    txs, _, _, _ = filter_lots(txs, request.GET)
    
    # on veut: nom site de depart, gps depart, nom site arrivee, gps arrivee, volume
    txs = txs.filter(lot__carbure_production_site__isnull=False, carbure_delivery_site__isnull=False)
    values = txs.values('lot__carbure_production_site__name', 'lot__carbure_production_site__gps_coordinates', 'carbure_delivery_site__name', 'carbure_delivery_site__gps_coordinates').annotate(volume=Sum('lot__volume'))

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
            slat, slon = v['lot__carbure_production_site__gps_coordinates'].split(',')
            # end coordinates
            elat, elon = v['carbure_delivery_site__gps_coordinates'].split(',')
        except:
            print('Missing start or end gps coordinates')
            print('Start %s : %s' % (v['lot__carbure_production_site__name'], v['lot__carbure_production_site__gps_coordinates']))
            print('End %s : %s' % (v['carbure_delivery_site__name'], v['carbure_delivery_site__gps_coordinates']))
            continue

        if v['lot__carbure_production_site__gps_coordinates'] not in known_prod_sites:
            known_prod_sites.append(v['lot__carbure_production_site__gps_coordinates'])
            c = couleur()
            folium.Circle(
                radius=50e2,
                location=[slat, slon],
                popup=v['lot__carbure_production_site__name'],
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
        folium.PolyLine([(float(slat),float(slon)),(float(elat),float(elon))], color=c, weight=grade(volume, volume_min, volume_max), line_cap='round', opacity=0.7, popup=v['lot__carbure_production_site__name']+' vers '+v['carbure_delivery_site__name']+' : \n'+str(volume)+' litres').add_to(m)
    return HttpResponse(m._repr_html_())

