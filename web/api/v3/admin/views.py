import datetime
import pytz
import calendar
from dateutil.rrule import rrule, MONTHLY

from django.http import JsonResponse
from core.decorators import is_admin
from django.contrib.auth import get_user_model
from core.models import Entity, UserRights
from django.db.models import Q, Count
from django.contrib.auth.forms import PasswordResetForm

from core.models import LotTransaction, UserRightsRequests, SustainabilityDeclaration, Control
from api.v3.lots.helpers import get_lots_with_metadata, get_lots_with_errors, get_snapshot_filters, get_errors


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
        entity = Entity.objects.get(pk=entity_id)
        return JsonResponse({"status": "success", "data": entity.natural_key()})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e) }, status=400)

@is_admin
def get_entities(request):
    q = request.GET.get('q', False)
    entities = Entity.objects.all()
    
    if q:
        entities = entities.filter(name__icontains=q)

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
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': "Unknown error. Please contact an administrator", 'extra': str(e)}, status=400)
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
def get_lots(request):
    status = request.GET.get('status', False)

    if not status:
        return JsonResponse({'status': 'error', 'message': "Please provide a status"}, status=400)

    try:
        txs = LotTransaction.objects.select_related(
            'lot', 'lot__carbure_producer', 'lot__carbure_production_site', 'lot__carbure_production_site__country',
            'lot__unknown_production_country', 'lot__matiere_premiere', 'lot__biocarburant', 'lot__pays_origine', 'lot__added_by', 'lot__data_origin_entity',
            'carbure_vendor', 'carbure_client', 'carbure_delivery_site', 'unknown_delivery_site_country', 'carbure_delivery_site__country'
        )

        txs = txs.filter(lot__status='Validated')

        if status == 'alert':
            txs, _ = get_lots_with_errors(txs)
        elif status == 'correction':
            txs = txs.filter(delivery_status__in=['AC', 'R', 'AA'])
        elif status == 'declaration':
            txs = txs.filter(delivery_status='A')

        return get_lots_with_metadata(txs, None, request.GET)

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


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
    data['transaction'] = tx.natural_key()
    data['errors'] = get_errors(tx)
    data['deadline'] = deadline_date.strftime("%Y-%m-%d")
    data['comments'] = [c.natural_key() for c in tx.transactioncomment_set.all()]

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
        txs = LotTransaction.objects.all().filter(lot__status='Validated')
        data['years'] = [t.year for t in txs.dates('delivery_date', 'year', order='DESC')]
        txs = txs.filter(delivery_date__gte=date_from).filter(delivery_date__lte=date_until)
        _, total_errors = get_lots_with_errors(txs)
        correction = len(txs.filter(delivery_status__in=['AC', 'R', 'AA']))
        declaration= len(txs.filter(delivery_status='A'))
        data['lots'] = {'alert': total_errors, 'correction': correction, 'declaration': declaration}

        filters = get_snapshot_filters(txs)
        producers = Entity.objects.filter(entity_type='Producteur')
        operators = Entity.objects.filter(entity_type='Opérateur')
        traders = Entity.objects.filter(entity_type='Trader')

        filters['producers'] = [p.name for p in producers]
        filters['traders'] = [p.name for p in traders]
        filters['operators'] = [p.name for p in operators]

        data['filters'] = filters

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    return JsonResponse({"status": "success", "data": data})


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
        request = UserRightsRequests.objects.get(id=urr_id)
    except:
        return JsonResponse({'status': 'error', 'message': "Could not find request"}, status=400)

    request.status = status
    request.save()

    if status == 'ACCEPTED':
        UserRights.objects.update_or_create(entity=request.entity, user=request.user)
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


@is_admin
def get_declarations(request):
    year = request.GET.get('year', False)

    if not year:
        year = 2021
    else:
        year = int(year)

    # calculate the periods window
    today = pytz.utc.localize(datetime.datetime.now())
    start = today - datetime.timedelta(days=130)
    nb_periods = 6
    periods = [(d.month, d.year) for d in rrule(MONTHLY, dtstart=start, count=nb_periods)]

    # get entities that have posted at least one lot since the beginning of the period
    entities_alive = [f['lot__added_by'] for f in LotTransaction.objects.filter(lot__added_time__gt=start).values('lot__added_by').annotate(count=Count('lot')).filter(count__gt=1)]
    entities = Entity.objects.filter(id__in=entities_alive)
    print('entities alive')
    print(entities)
    
    # create the SustainabilityDeclaration objects in database
    # 1) get existing objects
    existing = {'%d.%d.%d' % (sd.entity.id, sd.year, sd.period): sd for sd in SustainabilityDeclaration.objects.filter(entity__in=entities, year__gt=start.year, month__gt=start.month)}
    # 2) create target objects
    targets = {'%d.%d.%d' % (e.id, year, month): SustainabilityDeclaration(entity=e, year=year, month=month) for e in entities for month, year in periods}
    # 3) remove existing objects from targets
    for key, sd in existing:
        if key in targets:
            del targets[key]
    # 4) if any, bulk create the targets
    if len(targets):
        to_create = list(targets.values())
        print('will create %d declarations' % (len(to_create)))
        for t in to_create:
            print(t.natural_key())
        SustainabilityDeclaration.objects.bulk_create(to_create)
    else:
        print('no new declaration objects to create')
        print(len(existing))

    # get the declarations objects from db
    declarations = SustainabilityDeclaration.objects.filter(entity__in=entities, year__gte=start.year, month__gte=start.month)
        

    # query lots to enrich declarations on the frontend
    # expected return ['client1': [{'period': '2020-01', 'drafts': 200, 'validated': 100, 'checked': True}, {'period': '2020-02', 'drafts': 50, 'validated': 10, 'checked': False}]]
    # 1) get the lots grouped by added_by
    drafts = Count('id', filter=Q(lot__status='Draft'))
    validated = Count('id', filter=Q(lot__status='Validated'))
    received = Count('id', filter=Q(delivery_status__in=['N', 'AA']))
    corrections = Count('id', filter=Q(delivery_status__in=['R', 'AC']))
    batches = {'%s.%s' % (batch['lot__added_by__id'], batch['lot__period']): batch for batch in LotTransaction.objects.values('lot__added_by__id', 'lot__added_by__name', 'lot__period').annotate(num_drafts=drafts, num_valid=validated, num_received=received, num_corrections=corrections)}
    # 2) add batch info to each declarations
    declarations_sez = []
    for d in declarations:
        key = '%d.%d-%d' % (d.entity.id, d.year, d.month)
        if key in batches:
            d.lots = batches[key]
        else:
            d.lots = {'drafts': 0, 'validated': 0, 'received': 0, 'corrections': 0}
        sez_data = d.natural_key()
        sez_data['lots'] = d.lots
        declarations_sez.append(sez_data)
    return JsonResponse({"status": "success", "data": declarations_sez})


@is_admin
def send_declaration_reminder(request):
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

