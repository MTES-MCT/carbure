from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from core.models import LotTransaction
from core.models import Entity, UserRights, MatierePremiere, Biocarburant, Pays, LotV2, Depot
from core.decorators import check_rights
from core.common import get_prefetched_data, load_mb_lot, bulk_insert
from core.xlsx_v3 import template_stock, template_stock_bcghg

sort_key_to_django_field = {'period': 'lot__period',
                            'biocarburant': 'lot__biocarburant__name',
                            'matiere_premiere': 'lot__matiere_premiere__name',
                            'ghg_reduction': 'lot__ghg_reduction',
                            'volume': 'lot__volume',
                            'pays_origine': 'lot__pays_origine__name'}


def get_stocks(request):
    status = request.GET.get('status', False)
    entity = request.GET.get('entity_id', False)
    production_sites = request.GET.getlist('production_sites')
    matieres_premieres = request.GET.getlist('matieres_premieres')
    countries_of_origin = request.GET.getlist('countries_of_origin')
    biocarburants = request.GET.getlist('biocarburants')
    delivery_sites = request.GET.getlist('delivery_sites')
    limit = request.GET.get('limit', None)
    from_idx = request.GET.get('from_idx', "0")
    query = request.GET.get('query', False)
    sort_by = request.GET.get('sort_by', False)
    order = request.GET.get('order', False)

    if not status:
        return JsonResponse({'status': 'error', 'message': 'Missing status'}, status=400)
    if entity is None:
        return JsonResponse({'status': 'error', 'message': "Missing entity_id"}, status=400)
    try:
        entity = Entity.objects.get(id=entity, entity_type__in=['Producteur', 'Opérateur', 'Trader'])
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': "Unknown producer %s" % (entity), 'extra': str(e)},
                            status=400)

    rights = [r.entity for r in UserRights.objects.filter(user=request.user)]
    if entity not in rights:
        return JsonResponse({'status': 'forbidden', 'message': "User not allowed"}, status=403)

    if entity.entity_type in ['Producteur', 'Trader']:
        if status == "tosend":
            txs = LotTransaction.objects.filter(lot__added_by=entity, lot__status='Draft').exclude(lot__parent_lot=None)
        elif status == "in":
            txs = LotTransaction.objects.filter(carbure_client=entity, lot__status='Validated', delivery_status__in=['N', 'AC', 'AA'])
        elif status == "stock":
            txs = LotTransaction.objects.filter(carbure_client=entity, lot__status="Validated", delivery_status='A', lot__fused_with=None, lot__volume__gt=0)
        else:
            return JsonResponse({'status': 'error', 'message': "Unknown status"}, status=400)
    else:
        return JsonResponse({'status': 'error', 'message': "Unknown entity_type"}, status=400)

    # apply filters
    if production_sites:
        txs = txs.filter(Q(lot__carbure_production_site__name__in=production_sites) |
                         Q(lot__unknown_production_site__in=production_sites))
    if matieres_premieres:
        txs = txs.filter(lot__matiere_premiere__code__in=matieres_premieres)
    if biocarburants:
        txs = txs.filter(lot__biocarburant__code__in=biocarburants)
    if countries_of_origin:
        txs = txs.filter(lot__pays_origine__code_pays__in=countries_of_origin)
    if delivery_sites:
        txs = txs.filter(Q(carbure_delivery_site__name__in=delivery_sites)
                         | Q(unknown_delivery_site__in=delivery_sites))

    if query:
        txs = txs.filter(Q(lot__matiere_premiere__name__icontains=query) |
                         Q(lot__biocarburant__name__icontains=query) |
                         Q(lot__carbure_producer__name__icontains=query) |
                         Q(lot__unknown_producer__icontains=query) |
                         Q(lot__carbure_id__icontains=query) |
                         Q(lot__pays_origine__name__icontains=query) |
                         Q(carbure_delivery_site__name__icontains=query) |
                         Q(unknown_delivery_site__icontains=query)
                         )

    if sort_by:
        if sort_by in sort_key_to_django_field:
            key = sort_key_to_django_field[sort_by]
            if order == 'desc':
                txs = txs.order_by('-%s' % key)
            else:
                txs = txs.order_by(key)
        else:
            return JsonResponse({'status': 'error', 'message': 'Unknown sort_by key'}, status=400)

    from_idx = int(from_idx)
    returned = txs[from_idx:]

    if limit is not None:
        limit = int(limit)
        returned = returned[:limit]

    data = {}
    data['lots'] = [t.natural_key() for t in returned]
    data['total'] = len(txs)
    data['returned'] = len(returned)
    data['from'] = from_idx
    data['tx_errors'] = []
    data['lots_errors'] = []
    return JsonResponse({'status': 'success', 'data': data})


def get_snapshot(request):
    data = {}
    entity = request.GET.get('entity_id', False)
    if entity is None:
        return JsonResponse({'status': 'error', 'message': "Missing entity_id"}, status=400)
    try:
        entity = Entity.objects.get(id=entity, entity_type__in=['Producteur', 'Trader', 'Opérateur'])
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': "Unknown entity %s" % (entity), 'extra': str(e)},
                            status=400)

    rights = [r.entity for r in UserRights.objects.filter(user=request.user)]
    if entity not in rights:
        return JsonResponse({'status': 'forbidden', 'message': "User not allowed"}, status=403)

    if entity.entity_type in ['Producteur', 'Trader']:
        # drafts are lot that will be extracted from mass balance and sent to a client
        tx_drafts = LotTransaction.objects.filter(lot__added_by=entity, lot__status='Draft').exclude(lot__parent_lot=None)
        draft = len(tx_drafts)
        tx_inbox = LotTransaction.objects.filter(carbure_client=entity, lot__status='Validated', delivery_status__in=['N', 'AC', 'AA'])
        inbox = len(tx_inbox)
        tx_stock = LotTransaction.objects.filter(carbure_client=entity, lot__status="Validated", delivery_status='A', lot__fused_with=None, lot__volume__gt=0)
        stock = len(tx_stock)
        data['lots'] = {'in': inbox,  'stock': stock, 'tosend': draft}
    else:
        return JsonResponse({'status': 'error', 'message': "Unknown entity_type"}, status=400)

    # create union of querysets just to create filters 
    # txs = tx_drafts.union(tx_inbox, tx_stock)
    # txids = txs.values('id').distinct()
    # problem with using above code calling union, doing it manually
    txids = []
    txids += [t['id'] for t in tx_drafts.values('id').distinct()]
    txids += [t['id'] for t in tx_inbox.values('id').distinct()]
    txids += [t['id'] for t in tx_stock.values('id').distinct()]
    txs = LotTransaction.objects.filter(id__in=txids)
    mps = [{'value': m.code, 'label': m.name}
           for m in MatierePremiere.objects.filter(id__in=txs.values('lot__matiere_premiere').distinct())]

    bcs = [{'value': b.code, 'label': b.name}
           for b in Biocarburant.objects.filter(id__in=txs.values('lot__biocarburant').distinct())]

    countries = [{'value': c.code_pays, 'label': c.name}
                 for c in Pays.objects.filter(id__in=txs.values('lot__pays_origine').distinct())]

    ds1 = [c['carbure_delivery_site__name'] for c in txs.values('carbure_delivery_site__name').distinct()]
    ds2 = [c['unknown_delivery_site'] for c in txs.values('unknown_delivery_site').distinct()]
    delivery_sites = list(set([s for s in ds1 + ds2 if s]))

    ps1 = [p['lot__carbure_production_site__name'] for p in txs.values('lot__carbure_production_site__name').distinct()]
    ps2 = [p['lot__unknown_production_site'] for p in txs.values('lot__unknown_production_site').distinct()]
    psites = list(set([p for p in ps1 + ps2 if p]))

    data['filters'] = {'matieres_premieres': mps, 'biocarburants': bcs,
                       'production_sites': psites, 'countries_of_origin': countries, 'delivery_sites': delivery_sites}

    return JsonResponse({'status': 'success', 'data': data})

@check_rights('entity_id')
def send_lot(request, *args, **kwargs):

    context = kwargs['context']
    tx_id = request.POST.get('tx_id', False)
    entity_id = request.POST.get('entity_id', False)
    volume = request.POST.get('volume', False)
    client = request.POST.get('client', False)
    delivery_site = request.POST.get('delivery_site', False)
    delivery_date = request.POST.get('delivery_date', False)
    dae = request.POST.get('dae', False)

    if not tx_id:
        return JsonResponse({'status': 'forbidden', 'message': "Missing tx_id"}, status=400)
    if not entity_id:
        return JsonResponse({'status': 'forbidden', 'message': "Missing entity_id"}, status=400)
    if not volume:
        return JsonResponse({'status': 'forbidden', 'message': "Missing volume"}, status=400)
    if not client:
        return JsonResponse({'status': 'forbidden', 'message': "Missing client"}, status=400)
    if not delivery_site:
        return JsonResponse({'status': 'forbidden', 'message': "Missing delivery_site"}, status=400)
    if not delivery_date:
        return JsonResponse({'status': 'forbidden', 'message': "Missing delivery_date"}, status=400)
    if not dae:
        return JsonResponse({'status': 'forbidden', 'message': "Missing dae"}, status=400)                                    

    # found the stock line
    # prefetch some data
    d = get_prefetched_data(context['entity'])
    # create sub-transaction
    lot, tx, lot_errors, tx_errors = load_mb_lot(d, context['entity'], request.user, request.POST.dict(), 'MANUAL')
    if not tx:
        return JsonResponse({'status': 'error', 'message': 'Could not add lot to database: %s' % (lot_errors)}, status=400)
    new_lots, new_txs = bulk_insert(context['entity'], [lot], [tx], [lot_errors], [tx_errors])
    return JsonResponse({'status': 'success'})


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


def get_template_mass_balance_bcghg(request):
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

    file_location = template_stock_bcghg(entity)
    try:
        with open(file_location, 'rb') as f:
            file_data = f.read()
            # sending response
            response = HttpResponse(file_data, content_type='application/vnd.ms-excel')
            response['Content-Disposition'] = 'attachment; filename="carbure_template_mass_balance.xlsx"'
            return response
    except Exception as e:
        return JsonResponse({'status': "error", 'message': "Error creating template file", 'error': str(e)}, status=500)
