import datetime
import calendar
from dateutil.relativedelta import *
from django.db.models import Q, F, Case, When, Count
from django.db.models.functions import TruncMonth
from django.db.models.functions import Extract
from django.db.models.fields import NOT_PROVIDED
from django.http import JsonResponse, HttpResponse
from core.models import LotV2, LotTransaction, LotV2Error, TransactionError
from core.models import Entity, UserRights, MatierePremiere, Biocarburant, Pays, TransactionComment
from core.xlsx_v3 import template_producers_simple, template_producers_advanced, template_stock, template_operators, template_traders
from core.xlsx_v3 import export_transactions
from core.common import validate_lots, load_excel_file, load_lot, bulk_insert, get_prefetched_data
from api.v3.sanity_checks import bulk_sanity_checks


sort_key_to_django_field = {'period': 'lot__period',
                            'biocarburant': 'lot__biocarburant__name',
                            'matiere_premiere': 'lot__matiere_premiere__name',
                            'ghg_reduction': 'lot__ghg_reduction',
                            'volume': 'lot__volume',
                            'pays_origine': 'lot__pays_origine__name'}

def get_errors(tx):
    grouped_errors = {}
    tx_errors = [err.natural_key() for err in tx.transactionerror_set.all()]
    lots_errors = [err.natural_key() for err in tx.lot.lotv2error_set.all()]
    validation_errors = [err.natural_key() for err in tx.lot.lotvalidationerror_set.all()]

    if len(tx_errors) > 0:
        grouped_errors['tx_errors'] = tx_errors
    if len(lots_errors) > 0:
        grouped_errors['lots_errors'] = lots_errors
    if len(validation_errors) > 0:
        grouped_errors['validation_errors'] = validation_errors

    return grouped_errors

def get_lots(request):
    status = request.GET.get('status', False)
    entity = request.GET.get('entity_id', False)
    year = request.GET.get('year', False)
    periods = request.GET.getlist('periods')
    production_sites = request.GET.getlist('production_sites')
    delivery_sites = request.GET.getlist('delivery_sites')
    matieres_premieres = request.GET.getlist('matieres_premieres')
    countries_of_origin = request.GET.getlist('countries_of_origin')
    biocarburants = request.GET.getlist('biocarburants')
    clients = request.GET.getlist('clients')
    limit = request.GET.get('limit', None)
    from_idx = request.GET.get('from_idx', "0")
    export = request.GET.get('export', False)
    query = request.GET.get('query', False)
    sort_by = request.GET.get('sort_by', False)
    order = request.GET.get('order', False)
    invalid = request.GET.get('invalid', False)
    deadline = request.GET.get('deadline', False)
    vendors = request.GET.getlist('vendors')


    if not status:
        return JsonResponse({'status': 'error', 'message': 'Missing status'}, status=400)
    if entity is None:
        return JsonResponse({'status': 'error', 'message': "Missing entity_id"}, status=400)
    try:
        entity = Entity.objects.get(id=entity)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': "Unknown entity %s" % (entity), 'extra': str(e)},
                            status=400)

    rights = [r.entity for r in UserRights.objects.filter(user=request.user)]
    if entity not in rights:
        return JsonResponse({'status': 'forbidden', 'message': "User not allowed"}, status=403)

    if entity.entity_type == 'Producteur' or entity.entity_type == 'Trader':
        txs = LotTransaction.objects.select_related('lot', 'lot__carbure_producer', 'lot__carbure_production_site', 'lot__carbure_production_site__country',
                                                             'lot__unknown_production_country', 'lot__matiere_premiere', 'lot__biocarburant',
                                                             'lot__pays_origine', 'lot__added_by', 'lot__data_origin_entity',
                                                             'carbure_vendor', 'carbure_client', 'carbure_delivery_site', 'unknown_delivery_site_country', 'carbure_delivery_site__country')
        txs = txs.filter(lot__added_by=entity)                                                         
        # filter by status
        if status == 'draft':
            txs = txs.filter(lot__status='Draft')
        elif status == 'validated':
            txs = txs.filter(lot__status='Validated', delivery_status__in=['N', 'AA'])
        elif status == 'tofix':
            txs = txs.filter(lot__status='Validated', delivery_status__in=['AC', 'R'])
        elif status == 'accepted':
            txs = txs.filter(lot__status='Validated', delivery_status='A')
        else:
            return JsonResponse({'status': 'error', 'message': 'Unknown status'}, status=400)
    elif entity.entity_type == 'Opérateur':
        txs = LotTransaction.objects.select_related('lot', 'lot__carbure_producer', 'lot__carbure_production_site', 'lot__carbure_production_site__country',
                                                             'lot__unknown_production_country', 'lot__matiere_premiere', 'lot__biocarburant',
                                                             'lot__pays_origine', 'lot__added_by', 'lot__data_origin_entity',
                                                             'carbure_vendor', 'carbure_client', 'carbure_delivery_site', 'unknown_delivery_site_country', 'carbure_delivery_site__country')
        txs = txs.filter(carbure_client=entity)
        # filter by status
        if status == 'draft':
            txs = txs.filter(lot__added_by=entity, lot__status='Draft')
        elif status == 'in':
            txs = txs.filter(delivery_status__in=['N', 'AC', 'AA'], lot__status="Validated")
        elif status == 'accepted':
            txs = txs.filter(lot__status='Validated', delivery_status='A')
        else:
            return JsonResponse({'status': 'error', 'message': 'Unknown status'}, status=400)        
    else:
        return JsonResponse({'status': 'error', 'message': 'Unknown entity_type'}, status=400)        

    # apply filters
    date_from = datetime.date.today().replace(month=1, day=1)
    date_until = datetime.date.today().replace(month=12, day=31)
    if year:
        try:
            year = int(year)
            date_from = datetime.date(year=year, month=1, day=1)
            date_until = datetime.date(year=year, month=12, day=31)
        except Exception:
            return JsonResponse({'status': 'error', 'message': 'Incorrect format for year. Expected YYYY'}, status=400)
    txs = txs.filter(delivery_date__gte=date_from).filter(delivery_date__lte=date_until)

    if periods:
        txs = txs.filter(lot__period__in=periods)
    if production_sites:
        txs = txs.filter(Q(lot__carbure_production_site__name__in=production_sites) |
                         Q(lot__unknown_production_site__in=production_sites))
    if matieres_premieres:
        txs = txs.filter(lot__matiere_premiere__code__in=matieres_premieres)
    if biocarburants:
        txs = txs.filter(lot__biocarburant__code__in=biocarburants)
    if countries_of_origin:
        txs = txs.filter(lot__pays_origine__code_pays__in=countries_of_origin)
    if clients:
        txs = txs.filter(Q(carbure_client__name__in=clients) | Q(unknown_client__in=clients))
    if delivery_sites:
        txs = txs.filter(Q(carbure_delivery_site__name__in=delivery_sites)
                         | Q(unknown_delivery_site__in=delivery_sites))
    if vendors:
        txs = txs.filter(Q(carbure_vendor__name__in=vendors) | Q(unknown_vendor__in=vendors))

    if query:
        txs = txs.filter(Q(lot__matiere_premiere__name__icontains=query) |
                         Q(lot__biocarburant__name__icontains=query) |
                         Q(lot__carbure_producer__name__icontains=query) |
                         Q(lot__unknown_producer__icontains=query) |
                         Q(lot__carbure_id__icontains=query) |
                         Q(lot__pays_origine__name__icontains=query) |
                         Q(carbure_client__name__icontains=query) |
                         Q(unknown_client__icontains=query) |
                         Q(carbure_delivery_site__name__icontains=query) |
                         Q(unknown_delivery_site__icontains=query)
                         )

    tx_with_errors = txs.annotate(Count('transactionerror'), Count('lot__lotv2error'), Count('lot__lotvalidationerror')).filter(
        Q(transactionerror__count__gt=0) | Q(lot__lotv2error__count__gt=0) | Q(lot__lotvalidationerror__count__gt=0))

    now = datetime.datetime.now()
    (_, last_day) = calendar.monthrange(now.year, now.month)
    deadline_date = now.replace(day=last_day)
    affected_date = deadline_date - relativedelta(months=1)
    txs_with_deadline = txs.filter(lot__status='Draft', delivery_date__year=affected_date.year, delivery_date__month=affected_date.month)
    deadline_str = deadline_date.strftime("%Y-%m-%d")
    deadline_total = txs_with_deadline.count()

    if invalid == 'true':
        txs = tx_with_errors
    elif deadline == 'true':
        txs = txs_with_deadline
    else:
        pass

    if sort_by:
        if sort_by in sort_key_to_django_field:
            key = sort_key_to_django_field[sort_by]
            if order == 'desc':
                txs = txs.order_by('-%s' % key)
            else:
                txs = txs.order_by(key)
        elif sort_by == 'client':
            txs = txs.annotate(client=Case(When(client_is_in_carbure=True, then=F(
                'carbure_client__name')), default=F('unknown_client')))
            if order == 'desc':
                txs = txs.order_by('-client')
            else:
                txs = txs.order_by('client')
        else:
            return JsonResponse({'status': 'error', 'message': 'Unknown sort_by key'}, status=400)
    else:
        txs = txs.order_by('-id')

    from_idx = int(from_idx)
    returned = txs[from_idx:]

    if limit is not None:
        limit = int(limit)
        returned = returned[:limit]

    errors = {}

    for tx in returned:
        grouped_errors = get_errors(tx)
        if len(grouped_errors) > 0:
            errors[tx.id] = grouped_errors

    data = {}
    data['lots'] = [t.natural_key() for t in returned]
    data['total'] = len(txs)
    data['total_errors'] = tx_with_errors.count()
    data['returned'] = len(returned)
    data['from'] = from_idx
    data['errors'] = errors
    data['deadlines'] = {'date': deadline_str, 'total': deadline_total}

    if not export:
        return JsonResponse({'status': 'success', 'data': data})
    else:
        file_location = export_transactions(entity, returned)
        with open(file_location, "rb") as excel:
            data = excel.read()
            ctype = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            response = HttpResponse(content=data, content_type=ctype)
            response['Content-Disposition'] = 'attachment; filename="%s"' % (file_location)
        return response


def get_details(request):
    tx_id = request.GET.get('tx_id', False)
    entity_id = request.GET.get('entity_id', False)

    if not tx_id:
        return JsonResponse({'status': 'error', 'message': 'Missing tx_id'}, status=400)
    if not entity_id:
        return JsonResponse({'status': 'error', 'message': "Missing entity_id"}, status=400)
    
    try:
        entity = Entity.objects.get(id=entity_id)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': "Unknown entity %s" % (entity), 'extra': str(e)}, status=400)

    rights = [r.entity for r in UserRights.objects.filter(user=request.user)]

    if entity not in rights:
        return JsonResponse({'status': 'forbidden', 'message': "User not allowed"}, status=403)

    tx = LotTransaction.objects.get(pk=tx_id)

    if tx.carbure_client != entity and tx.carbure_vendor != entity:
        return JsonResponse({'status': 'forbidden', 'message': "User not allowed"}, status=403)

    now = datetime.datetime.now()
    (_, last_day) = calendar.monthrange(now.year, now.month)
    deadline_date = now.replace(day=last_day)

    data = {}
    data['transaction'] = tx.natural_key()
    data['errors'] = get_errors(tx)
    data['deadline'] = deadline_date.strftime("%Y-%m-%d")
    data['comments'] = [c.natural_key() for c in tx.transactioncomment_set.all()]

    return JsonResponse({'status': 'success', 'data': data})


def get_snapshot(request):
    data = {}
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
    entity = request.GET.get('entity_id', False)
    if entity is None:
        return JsonResponse({'status': 'error', 'message': "Missing entity_id"}, status=400)
    try:
        entity = Entity.objects.get(id=entity)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': "Unknown entity %s" % (entity), 'extra': str(e)},
                            status=400)

    rights = [r.entity for r in UserRights.objects.filter(user=request.user)]
    if entity not in rights:
        return JsonResponse({'status': 'forbidden', 'message': "User not allowed"}, status=403)

    if entity.entity_type == 'Producteur' or entity.entity_type == 'Trader':
        txs = LotTransaction.objects.filter(lot__added_by=entity)
        data['years'] = [t.year for t in txs.dates('delivery_date', 'year', order='DESC')]
        txs = txs.filter(delivery_date__gte=date_from).filter(delivery_date__lte=date_until)
        draft = len(txs.filter(lot__status='Draft'))
        validated = len(txs.filter(lot__status='Validated', delivery_status__in=['N', 'AA']))
        tofix = len(txs.filter(lot__status='Validated', delivery_status__in=['AC', 'R']))
        accepted = len(txs.filter(lot__status='Validated', delivery_status='A'))
        data['lots'] = {'draft': draft, 'validated': validated, 'tofix': tofix, 'accepted': accepted}
    elif entity.entity_type == 'Opérateur':
        txs = LotTransaction.objects.filter(carbure_client=entity)
        data['years'] = [t.year for t in txs.dates('delivery_date', 'year', order='DESC')]
        txs = txs.filter(delivery_date__gte=date_from).filter(delivery_date__lte=date_until)
        draft = len(txs.filter(lot__added_by=entity, lot__status='Draft'))
        ins = len(txs.filter(lot__status='Validated', delivery_status__in=['N', 'AA', 'AC']))
        accepted = len(txs.filter(lot__status='Validated', delivery_status='A'))
        data['lots'] = {'draft': draft, 'accepted': accepted, 'in': ins}
    else:
        return JsonResponse({'status': 'error', 'message': "Unknown entity_type"}, status=400)

    mps = [{'value': m.code, 'label': m.name}
           for m in MatierePremiere.objects.filter(id__in=txs.values('lot__matiere_premiere').distinct())]

    bcs = [{'value': b.code, 'label': b.name}
           for b in Biocarburant.objects.filter(id__in=txs.values('lot__biocarburant').distinct())]

    countries = [{'value': c.code_pays, 'label': c.name}
                 for c in Pays.objects.filter(id__in=txs.values('lot__pays_origine').distinct())]

    periods = [p['lot__period'] for p in txs.values('lot__period').distinct() if p['lot__period']]


    ps1 = [p['lot__carbure_production_site__name'] for p in txs.values('lot__carbure_production_site__name').distinct()]
    ps2 = [p['lot__unknown_production_site'] for p in txs.values('lot__unknown_production_site').distinct()]
    psites = list(set([p for p in ps1 + ps2 if p]))

    ds1 = [p['carbure_delivery_site__name'] for p in txs.values('carbure_delivery_site__name').distinct()]
    ds2 = [p['unknown_delivery_site'] for p in txs.values('unknown_delivery_site').distinct()]
    dsites = list(set([d for d in ds1 + ds2 if d]))

    filters = {'matieres_premieres': mps, 'biocarburants': bcs, 'periods': periods,
                       'production_sites': psites, 'countries_of_origin': countries, 'delivery_sites': dsites}

    if entity.entity_type == 'Producteur':
        c1 = [c['carbure_client__name'] for c in txs.values('carbure_client__name').distinct()]
        c2 = [c['unknown_client'] for c in txs.values('unknown_client').distinct()]
        clients = [c for c in c1 + c2 if c]
        filters['clients'] = clients
    elif entity.entity_type == 'Opérateur':
        v1 = [v['carbure_vendor__name'] for v in txs.values('carbure_vendor__name').distinct()]
        v2 = [v['unknown_vendor'] for v in txs.values('unknown_vendor').distinct()]
        vendors = [v for v in v1 + v2 if v]
        filters['vendors'] = vendors

    data['filters'] = filters

    return JsonResponse({'status': 'success', 'data': data})


def get_summary_in(request):
    entity = request.GET.get('entity_id', False)
    if entity is None:
        return JsonResponse({'status': 'error', 'message': "Missing entity_id"}, status=400)
    try:
        entity = Entity.objects.get(id=entity)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': "Unknown entity %s" % (entity), 'extra': str(e)},
                            status=400)

    rights = [r.entity for r in UserRights.objects.filter(user=request.user)]
    if entity not in rights:
        return JsonResponse({'status': 'forbidden', 'message': "User not allowed"}, status=403)

    # get my pending incoming lots
    txs = LotTransaction.objects.filter(carbure_client=entity, lot__status='Validated', delivery_status__in=['N', 'AA', 'AC'])

    # group / summary
    data = {}
    for t in txs:
        delivery_site = t.carbure_delivery_site.name if t.delivery_site_is_in_carbure and t.carbure_delivery_site else t.unknown_delivery_site
        if delivery_site not in data:
            data[delivery_site] = {}
        if t.carbure_vendor.name not in data[delivery_site]:
            data[delivery_site][t.carbure_vendor.name] = {}
        if t.lot.biocarburant.name not in data[delivery_site][t.carbure_vendor.name]:
            data[delivery_site][t.carbure_vendor.name][t.lot.biocarburant.name] = {'volume': 0, 'avg_ghg_reduction': 0}
        line = data[delivery_site][t.carbure_vendor.name][t.lot.biocarburant.name]
        line['avg_ghg_reduction'] = (line['volume'] * line['avg_ghg_reduction'] +
                                     t.lot.volume * t.lot.ghg_reduction) / (line['volume'] + t.lot.volume)
        line['volume'] += t.lot.volume
    return JsonResponse({'status': 'success', 'data': data})


def get_summary_out(request):
    entity = request.GET.get('entity_id', False)
    if entity is None:
        return JsonResponse({'status': 'error', 'message': "Missing entity_id"}, status=400)
    try:
        entity = Entity.objects.get(id=entity)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': "Unknown entity %s" % (entity), 'extra': str(e)},
                            status=400)

    rights = [r.entity for r in UserRights.objects.filter(user=request.user)]
    if entity not in rights:
        return JsonResponse({'status': 'forbidden', 'message': "User not allowed"}, status=403)

    # get my pending sent lots
    txs = LotTransaction.objects.filter(carbure_vendor=entity, lot__status='Validated', delivery_status='N')

    # group / summary
    data = {}
    for t in txs:
        client_name = t.carbure_client.name if t.client_is_in_carbure and t.carbure_client else t.unknown_client
        if client_name not in data:
            data[client_name] = {}
        delivery_site = t.carbure_delivery_site.name if t.delivery_site_is_in_carbure and t.carbure_delivery_site else t.unknown_delivery_site
        if delivery_site not in data[client_name]:
            data[client_name][delivery_site] = {}
        if t.lot.biocarburant.name not in data[client_name][delivery_site]:
            data[client_name][delivery_site][t.lot.biocarburant.name] = {'volume': 0, 'avg_ghg_reduction': 0}
        line = data[client_name][delivery_site][t.lot.biocarburant.name]
        line['avg_ghg_reduction'] = (line['volume'] * line['avg_ghg_reduction'] +
                                     t.lot.volume * t.lot.ghg_reduction) / (line['volume'] + t.lot.volume)
        line['volume'] += t.lot.volume
    return JsonResponse({'status': 'success', 'data': data})


def add_lot(request):
    entity_id = request.POST.get('entity_id', False)
    if not entity_id:
        return JsonResponse({'status': 'forbidden', 'message': "Missing entity_id"}, status=400)

    try:
        entity = Entity.objects.get(id=entity_id)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': "Unknown entity %s" % (entity_id), 'extra': str(e)},
                            status=400)

    rights = [r.entity for r in UserRights.objects.filter(user=request.user)]
    if entity not in rights:
        return JsonResponse({'status': 'forbidden', 'message': "User not allowed"}, status=403)

    # prefetch some data
    d = get_prefetched_data(entity)
    lot, tx, lot_errors, tx_errors = load_lot(d, entity, request.user, request.POST.dict(), 'MANUAL')
    if not tx:
        return JsonResponse({'status': 'error', 'message': 'Could not add lot to database'}, status=400)
    new_lots, new_txs = bulk_insert(entity, [lot], [tx], [lot_errors], [tx_errors])
    return JsonResponse({'status': 'success', 'data': new_txs[0].natural_key()})


def update_lot(request):
    entity_id = request.POST.get('entity_id', False)
    if not entity_id:
        return JsonResponse({'status': 'forbidden', 'message': "Missing entity_id"}, status=400)

    try:
        entity = Entity.objects.get(id=entity_id)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': "Unknown entity %s" % (entity_id), 'extra': str(e)},
                            status=400)

    rights = [r.entity for r in UserRights.objects.filter(user=request.user)]
    if entity not in rights:
        return JsonResponse({'status': 'forbidden', 'message': "User not allowed"}, status=403)

    tx_id = request.POST.get('tx_id', False)
    if not tx_id:
        return JsonResponse({'status': 'forbidden', 'message': "Missing tx_id"}, status=400)

    try:
        tx = LotTransaction.objects.get(id=tx_id)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': "Unknown transaction %s" % (tx_id), 'extra': str(e)},
                            status=400)
    if tx.delivery_status == 'A':
        return JsonResponse({'status': 'forbidden', 'message': "Tx already validated and accepted %d" % (tx.id)}, status=400)
    LotV2Error.objects.filter(lot_id=tx.lot.id).delete()
    TransactionError.objects.filter(tx_id=tx.id).delete()
    d = get_prefetched_data(entity)
    lot, tx, lot_errors, tx_errors = load_lot(d, entity, request.user, request.POST.dict(), 'MANUAL', tx)
    if lot:
        lot.save()
        tx.save()
        LotV2Error.objects.bulk_create(lot_errors)
        TransactionError.objects.bulk_create(tx_errors)       
        bulk_sanity_checks([tx.lot], background=False)
        return JsonResponse({'status': 'success'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Could not save lot: %s' % (lot_errors)})


def duplicate_lot(request):
    tx_id = request.POST.get('tx_id', None)

    try:
        tx = LotTransaction.objects.get(id=tx_id)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': "Unknown Transaction %s" % (tx_id), 'extra': str(e)},
                            status=400)

    rights = [r.entity for r in UserRights.objects.filter(user=request.user)]
    if tx.lot.added_by not in rights:
        return JsonResponse({'status': 'forbidden', 'message': "User not allowed"}, status=403)

    lot_fields_to_remove = ['carbure_id', 'status']
    lot_meta_fields = {f.name: f for f in LotV2._meta.get_fields()}
    lot = tx.lot
    lot.pk = None
    for f in lot_fields_to_remove:
        if f in lot_meta_fields:
            meta_field = lot_meta_fields[f]
            if meta_field.default != NOT_PROVIDED:
                setattr(lot, f, meta_field.default)
            else:
                setattr(lot, f, '')
    lot.save()
    tx_fields_to_remove = ['dae', 'delivery_status']
    tx_meta_fields = {f.name: f for f in LotTransaction._meta.get_fields()}
    tx.pk = None
    tx.lot = lot
    for f in tx_fields_to_remove:
        if f in tx_meta_fields:
            meta_field = tx_meta_fields[f]
            if meta_field.default != NOT_PROVIDED:
                setattr(tx, f, meta_field.default)
            else:
                setattr(tx, f, '')
    tx.save()
    return JsonResponse({'status': 'success'})


def delete_lot(request):
    tx_ids = request.POST.getlist('tx_ids', False)

    if not tx_ids:
        return JsonResponse({'status': 'forbidden', 'message': "Missing tx_ids"}, status=403)

    for tx_id in tx_ids:
        try:
            tx = LotTransaction.objects.get(id=tx_id)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': "Unknown Transaction %s" % (tx_id), 'extra': str(e)},
                                status=400)

        rights = [r.entity for r in UserRights.objects.filter(user=request.user)]
        if tx.lot.added_by not in rights:
            return JsonResponse({'status': 'forbidden', 'message': "User not allowed to delete this tx"}, status=403)

        # only allow to delete pending or rejected transactions
        if tx.delivery_status not in ['N', 'R']:
            return JsonResponse({'status': 'forbidden', 'message': "Transaction already accepted by client"},
                                status=403)
        tx.lot.delete()
    return JsonResponse({'status': 'success'})


def validate_lot(request):
    tx_ids = request.POST.getlist('tx_ids', None)
    if not tx_ids:
        return JsonResponse({'status': 'forbidden', 'message': "Missing tx_ids"}, status=403)
    return validate_lots(request.user, tx_ids)


def accept_lot(request):
    tx_ids = request.POST.getlist('tx_ids', None)
    if not tx_ids:
        return JsonResponse({'status': 'forbidden', 'message': "Missing tx_ids"}, status=403)
    for tx_id in tx_ids:
        try:
            tx = LotTransaction.objects.get(delivery_status__in=['N', 'AC', 'AA'], id=tx_id)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': "TX not found", 'extra': str(e)}, status=400)

        rights = [r.entity for r in UserRights.objects.filter(user=request.user)]
        if tx.carbure_client not in rights:
            return JsonResponse({'status': 'forbidden', 'message': "User not allowed"}, status=403)
        tx.delivery_status = 'A'
        tx.save()
    return JsonResponse({'status': 'success'})


def accept_with_reserves(request):
    tx_ids = request.POST.getlist('tx_ids', None)
    if not tx_ids:
        return JsonResponse({'status': 'forbidden', 'message': "Missing tx_ids"}, status=403)
    for tx_id in tx_ids:
        try:
            tx = LotTransaction.objects.get(delivery_status__in=['N', 'AC', 'AA'], id=tx_id)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': "TX not found", 'extra': str(e)}, status=400)

        rights = [r.entity for r in UserRights.objects.filter(user=request.user)]
        if tx.carbure_client not in rights:
            return JsonResponse({'status': 'forbidden', 'message': "User not allowed"}, status=403)
        tx.delivery_status = 'AC'
        tx.save()
    return JsonResponse({'status': 'success'})


def reject_lot(request):
    tx_ids = request.POST.getlist('tx_ids', None)
    tx_comment = request.POST.get('comment', None)
    if not tx_ids:
        return JsonResponse({'status': 'error', 'message': "Missing tx_ids"}, status=400)
    if not tx_comment:
        return JsonResponse({'status': 'error', 'message': "Missing comment"}, status=400)

    for tx_id in tx_ids:
        if tx_id is None:
            return JsonResponse({'status': 'error', 'message': "Missing TX ID from POST data"}, status=400)

        try:
            tx = LotTransaction.objects.get(delivery_status__in=['N', 'AC', 'AA'], id=tx_id)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': "TX not found", 'extra': str(e)}, status=400)

        rights = [r.entity for r in UserRights.objects.filter(user=request.user)]
        if tx.carbure_client not in rights:
            return JsonResponse({'status': 'forbidden', 'message': "User not allowed"}, status=403)
        tx.delivery_status = 'R'
        tx.save()
        txerr = TransactionComment()
        txerr.entity = tx.carbure_client
        txerr.tx = tx
        txerr.comment = tx_comment
        txerr.save()
    return JsonResponse({'status': 'success'})


def comment_lot(request):
    tx_id = request.POST.get('tx_id', None)
    entity_id = request.POST.get('entity_id', None)
    comment = request.POST.get('comment', None)
    comment_type = request.POST.get('comment_type', None)
    if tx_id is None:
        return JsonResponse({'status': 'error', 'message': "Missing TX ID"}, status=400)
    if entity_id is None:
        return JsonResponse({'status': 'error', 'message': "Missing entity_id"}, status=400)
    if comment is None:
        return JsonResponse({'status': 'error', 'message': "Missing comment"}, status=400)
    if comment_type is None:
        return JsonResponse({'status': 'error', 'message': "Missing comment_type"}, status=400)

    try:
        entity = Entity.objects.get(id=entity_id)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': "Entity not found", 'extra': str(e)}, status=400)

    try:
        tx = LotTransaction.objects.get(id=tx_id)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': "TX not found", 'extra': str(e)}, status=400)

    rights = [r.entity for r in UserRights.objects.filter(user=request.user)]

    # only the client, vendor and producer can comment
    if tx.carbure_client not in rights and tx.carbure_vendor not in rights and tx.lot.carbure_producer not in rights:
        return JsonResponse({'status': 'forbidden', 'message': "User not allowed to comment on this transaction"},
                            status=403)

    if entity not in rights:
        return JsonResponse({'status': 'forbidden', 'message': "User not allowed to comment on behalf of this entity"},
                            status=403)

    txc = TransactionComment()
    txc.entity = entity
    txc.tx = tx
    txc.topic = comment_type
    txc.comment = comment
    txc.save()
    return JsonResponse({'status': 'success'})


def accept_all(request):
    entity_id = request.POST.get('entity_id', False)
    if not entity_id:
        return JsonResponse({'status': 'forbidden', 'message': "Missing entity_id"}, status=400)

    try:
        entity = Entity.objects.get(id=entity_id)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': "Unknown entity %s" % (entity_id), 'extra': str(e)},
                            status=400)

    rights = [r.entity for r in UserRights.objects.filter(user=request.user)]
    if entity not in rights:
        return JsonResponse({'status': 'forbidden', 'message': "User not allowed"}, status=403)

    lots = LotTransaction.objects.filter(carbure_client=entity, delivery_status__in=[
        'N', 'AC', 'AA'])
    year = request.POST.get('year', False)
    date_from = datetime.date.today().replace(month=1, day=1)
    date_until = datetime.date.today().replace(month=12, day=31)
    if year:
        try:
            year = int(year)
            date_from = datetime.date(year=year, month=1, day=1)
            date_until = datetime.date(year=year, month=12, day=31)
        except Exception:
            return JsonResponse({'status': 'error', 'message': 'Incorrect format for year. Expected YYYY'}, status=400)
    lots.filter(delivery_date__gte=date_from).filter(delivery_date__lte=date_until).update(delivery_status='A')
    return JsonResponse({'status': 'success'})


def reject_all(request):
    entity_id = request.POST.get('entity_id', False)
    if not entity_id:
        return JsonResponse({'status': 'error', 'message': "Missing entity_id"}, status=400)
    tx_comment = request.POST.get('comment', None)
    if not tx_comment:
        return JsonResponse({'status': 'error', 'message': "Missing comment"}, status=400)
    try:
        entity = Entity.objects.get(id=entity_id)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': "Unknown entity %s" % (entity_id), 'extra': str(e)},
                            status=400)

    rights = [r.entity for r in UserRights.objects.filter(user=request.user)]
    if entity not in rights:
        return JsonResponse({'status': 'forbidden', 'message': "User not allowed"}, status=403)

    txs = LotTransaction.objects.filter(carbure_client=entity, delivery_status__in=[
        'N', 'AC', 'AA'])
    year = request.POST.get('year', False)
    date_from = datetime.date.today().replace(month=1, day=1)
    date_until = datetime.date.today().replace(month=12, day=31)
    if year:
        try:
            year = int(year)
            date_from = datetime.date(year=year, month=1, day=1)
            date_until = datetime.date(year=year, month=12, day=31)
        except Exception:
            return JsonResponse({'status': 'error', 'message': 'Incorrect format for year. Expected YYYY'}, status=400)
    txs = txs.filter(delivery_date__gte=date_from).filter(delivery_date__lte=date_until)
    txs.update(delivery_status='R')
    for tx in txs:
        txerr = TransactionComment()
        txerr.entity = tx.carbure_client
        txerr.tx = tx
        txerr.comment = tx_comment
        txerr.save()
    return JsonResponse({'status': 'success'})


def delete_all_drafts(request):
    entity_id = request.POST.get('entity_id', False)
    if not entity_id:
        return JsonResponse({'status': 'forbidden', 'message': "Missing entity_id"}, status=400)

    try:
        entity = Entity.objects.get(id=entity_id)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': "Unknown entity %s" % (entity_id), 'extra': str(e)},
                            status=400)

    rights = [r.entity for r in UserRights.objects.filter(user=request.user)]
    if entity not in rights:
        return JsonResponse({'status': 'forbidden', 'message': "User not allowed"}, status=403)

    drafts = LotTransaction.objects.filter(lot__added_by=entity, lot__status='Draft')
    year = request.POST.get('year', False)
    date_from = datetime.date.today().replace(month=1, day=1)
    date_until = datetime.date.today().replace(month=12, day=31)
    if year:
        try:
            year = int(year)
            date_from = datetime.date(year=year, month=1, day=1)
            date_until = datetime.date(year=year, month=12, day=31)
        except Exception:
            return JsonResponse({'status': 'error', 'message': 'Incorrect format for year. Expected YYYY'}, status=400)
    drafts.filter(delivery_date__gte=date_from).filter(delivery_date__lte=date_until).delete()
    return JsonResponse({'status': 'success'})


def validate_all_drafts(request):
    entity_id = request.POST.get('entity_id', False)
    if not entity_id:
        return JsonResponse({'status': 'forbidden', 'message': "Missing entity_id"}, status=400)

    try:
        entity = Entity.objects.get(id=entity_id)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': "Unknown entity %s" % (entity_id), 'extra': str(e)},
                            status=400)

    rights = [r.entity for r in UserRights.objects.filter(user=request.user)]
    if entity not in rights:
        return JsonResponse({'status': 'forbidden', 'message': "User not allowed"}, status=403)

    drafts = LotTransaction.objects.filter(lot__added_by=entity, lot__status='Draft')
    year = request.POST.get('year', False)
    date_from = datetime.date.today().replace(month=1, day=1)
    date_until = datetime.date.today().replace(month=12, day=31)
    if year:
        try:
            year = int(year)
            date_from = datetime.date(year=year, month=1, day=1)
            date_until = datetime.date(year=year, month=12, day=31)
        except Exception:
            return JsonResponse({'status': 'error', 'message': 'Incorrect format for year. Expected YYYY'}, status=400)
    drafts = drafts.filter(delivery_date__gte=date_from).filter(delivery_date__lte=date_until)

    tx_ids = [d.id for d in drafts]
    return validate_lots(request.user, tx_ids)


def get_template_producers_simple(request):
    entity_id = request.GET.get('entity_id', False)
    if not entity_id:
        return JsonResponse({'status': 'forbidden', 'message': "Missing entity_id"}, status=400)

    try:
        entity = Entity.objects.get(id=entity_id)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': "Unknown entity %s" % (entity_id), 'extra': str(e)},
                            status=400)

    rights = [r.entity for r in UserRights.objects.filter(user=request.user)]
    if entity not in rights:
        return JsonResponse({'status': 'forbidden', 'message': "User not allowed"}, status=403)

    file_location = template_producers_simple(entity)
    try:
        with open(file_location, 'rb') as f:
            file_data = f.read()
            # sending response
            response = HttpResponse(file_data, content_type='application/vnd.ms-excel')
            response['Content-Disposition'] = 'attachment; filename="carbure_template_simple.xlsx"'
            return response
    except Exception as e:
        return JsonResponse({'status': "error", 'message': "Error creating template file", 'error': str(e)}, status=500)


def get_template_producers_advanced(request):
    entity_id = request.GET.get('entity_id', False)
    if not entity_id:
        return JsonResponse({'status': 'forbidden', 'message': "Missing entity_id"}, status=400)

    try:
        entity = Entity.objects.get(id=entity_id)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': "Unknown entity %s" % (entity_id), 'extra': str(e)},
                            status=400)

    rights = [r.entity for r in UserRights.objects.filter(user=request.user)]
    if entity not in rights:
        return JsonResponse({'status': 'forbidden', 'message': "User not allowed"}, status=403)

    file_location = template_producers_advanced(entity)
    try:
        with open(file_location, 'rb') as f:
            file_data = f.read()
            # sending response
            response = HttpResponse(file_data, content_type='application/vnd.ms-excel')
            response['Content-Disposition'] = 'attachment; filename="carbure_template_advanced.xlsx"'
            return response
    except Exception as e:
        return JsonResponse({'status': "error", 'message': "Error creating template file", 'error': str(e)}, status=500)


def get_template_mass_balance(request):
    entity_id = request.GET.get('entity_id', False)
    if not entity_id:
        return JsonResponse({'status': 'forbidden', 'message': "Missing entity_id"}, status=400)

    try:
        entity = Entity.objects.get(id=entity_id)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': "Unknown entity %s" % (entity_id), 'extra': str(e)},
                            status=400)

    rights = [r.entity for r in UserRights.objects.filter(user=request.user)]
    if entity not in rights:
        return JsonResponse({'status': 'forbidden', 'message': "User not allowed"}, status=403)

    file_location = template_stock(entity)
    try:
        with open(file_location, 'rb') as f:
            file_data = f.read()
            # sending response
            response = HttpResponse(file_data, content_type='application/vnd.ms-excel')
            response['Content-Disposition'] = 'attachment; filename="carbure_template_mass_balance.xlsx"'
            return response
    except Exception as e:
        return JsonResponse({'status': "error", 'message': "Error creating template file", 'error': str(e)}, status=500)


def get_template_blend(request):
    entity_id = request.GET.get('entity_id', False)
    if not entity_id:
        return JsonResponse({'status': 'forbidden', 'message': "Missing entity_id"}, status=400)

    try:
        entity = Entity.objects.get(id=entity_id)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': "Unknown entity %s" % (entity_id), 'extra': str(e)},
                            status=400)

    rights = [r.entity for r in UserRights.objects.filter(user=request.user)]
    if entity not in rights:
        return JsonResponse({'status': 'forbidden', 'message': "User not allowed"}, status=403)

    file_location = template_operators(entity)
    try:
        with open(file_location, 'rb') as f:
            file_data = f.read()
            # sending response
            response = HttpResponse(file_data, content_type='application/vnd.ms-excel')
            response['Content-Disposition'] = 'attachment; filename="carbure_template_operator.xlsx"'
            return response
    except Exception as e:
        return JsonResponse({'status': "error", 'message': "Error creating template file", 'error': str(e)}, status=500)


def get_template_trader(request):
    entity_id = request.GET.get('entity_id', False)
    if not entity_id:
        return JsonResponse({'status': 'forbidden', 'message': "Missing entity_id"}, status=400)

    try:
        entity = Entity.objects.get(id=entity_id)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': "Unknown entity %s" % (entity_id), 'extra': str(e)},
                            status=400)

    rights = [r.entity for r in UserRights.objects.filter(user=request.user)]
    if entity not in rights:
        return JsonResponse({'status': 'forbidden', 'message': "User not allowed"}, status=403)

    file_location = template_traders(entity)
    try:
        with open(file_location, 'rb') as f:
            file_data = f.read()
            # sending response
            response = HttpResponse(file_data, content_type='application/vnd.ms-excel')
            response['Content-Disposition'] = 'attachment; filename="carbure_template_trader.xlsx"'
            return response
    except Exception as e:
        return JsonResponse({'status': "error", 'message': "Error creating template file", 'error': str(e)}, status=500)


def upload(request):
    file = request.FILES.get('file')
    entity_id = request.POST.get('entity_id', False)
    if not entity_id:
        return JsonResponse({'status': 'forbidden', 'message': "Missing entity_id"}, status=400)
    if file is None:
        return JsonResponse({'status': "error", 'message': "Missing File"}, status=400)

    try:
        entity = Entity.objects.get(id=entity_id)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': "Unknown entity %s" % (entity_id), 'extra': str(e)},
                            status=400)

    rights = [r.entity for r in UserRights.objects.filter(user=request.user)]
    if entity not in rights:
        return JsonResponse({'status': 'forbidden', 'message': "User not allowed"}, status=403)

    nb_loaded, nb_total = load_excel_file(entity, request.user, file)
    if nb_loaded is False:
        return JsonResponse({'status': 'error', 'message': 'Could not load Excel file'})
    return JsonResponse({'status': 'success', 'loaded': nb_loaded, 'total': nb_total})


def upload_mass_balance(request):
    file = request.FILES.get('file')
    entity_id = request.POST.get('entity_id', False)
    if not entity_id:
        return JsonResponse({'status': 'forbidden', 'message': "Missing entity_id"}, status=400)
    if file is None:
        return JsonResponse({'status': "error", 'message': "Missing File"}, status=400)

    try:
        entity = Entity.objects.get(id=entity_id)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': "Unknown entity %s" % (entity_id), 'extra': str(e)},
                            status=400)

    rights = [r.entity for r in UserRights.objects.filter(user=request.user)]
    if entity not in rights:
        return JsonResponse({'status': 'forbidden', 'message': "User not allowed"}, status=403)

    nb_loaded, nb_total = load_excel_file(entity, request.user, file, mass_balance=True)
    if nb_loaded is False:
        return JsonResponse({'status': 'error', 'message': 'Could not load Excel file'})
    return JsonResponse({'status': 'success', 'loaded': nb_loaded, 'total': nb_total})


def upload_blend(request):
    file = request.FILES.get('file')
    entity_id = request.POST.get('entity_id', False)
    if not entity_id:
        return JsonResponse({'status': 'forbidden', 'message': "Missing entity_id"}, status=400)
    if file is None:
        return JsonResponse({'status': "error", 'message': "Missing File"}, status=400)

    try:
        entity = Entity.objects.get(id=entity_id)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': "Unknown entity %s" % (entity_id), 'extra': str(e)},
                            status=400)

    rights = [r.entity for r in UserRights.objects.filter(user=request.user)]
    if entity not in rights:
        return JsonResponse({'status': 'forbidden', 'message': "User not allowed"}, status=403)

    nb_loaded, nb_total = load_excel_file(entity, request.user, file)
    if nb_loaded is False:
        return JsonResponse({'status': 'error', 'message': 'Could not load Excel file'})
    return JsonResponse({'status': 'success', 'loaded': nb_loaded, 'total': nb_total})


