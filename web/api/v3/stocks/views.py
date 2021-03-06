import json
import datetime
from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from core.models import LotV2, LotTransaction, ETBETransformation
from core.models import Entity, UserRights, MatierePremiere, Biocarburant, Pays, LotV2, Depot
from core.decorators import check_rights
from core.common import get_prefetched_data, load_mb_lot, bulk_insert
from core.common import load_excel_file, send_lot_from_stock, generate_carbure_id
from core.xlsx_v3 import template_stock, template_stock_bcghg
from core.xlsx_v3 import export_stocks
from django_otp.decorators import otp_required

sort_key_to_django_field = {'period': 'lot__period',
                            'biocarburant': 'lot__biocarburant__name',
                            'matiere_premiere': 'lot__matiere_premiere__name',
                            'ghg_reduction': 'lot__ghg_reduction',
                            'volume': 'lot__volume',
                            'pays_origine': 'lot__pays_origine__name'}

@check_rights('entity_id')
def get_stocks(request, *args, **kwargs):
    context = kwargs['context']
    entity = context['entity']

    status = request.GET.get('status', False)
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
    export = request.GET.get('export', False)

    if not status:
        return JsonResponse({'status': 'error', 'message': 'Missing status'}, status=400)
    
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
    data['total'] = txs.count()
    data['returned'] = returned.count()
    data['from'] = from_idx
    data['tx_errors'] = []
    data['lots_errors'] = []

    if not export:
        return JsonResponse({'status': 'success', 'data': data})
    else:
        file_location = export_stocks(entity, returned)
        with open(file_location, "rb") as excel:
            data = excel.read()
            ctype = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            response = HttpResponse(content=data, content_type=ctype)
            response['Content-Disposition'] = 'attachment; filename="%s"' % (file_location)
        return response

@check_rights('entity_id')
def get_snapshot(request, *args, **kwargs):
    context = kwargs['context']
    entity = context['entity']

    data = {}
    if entity.entity_type in ['Producteur', 'Trader']:
        # drafts are lot that will be extracted from mass balance and sent to a client
        tx_drafts = LotTransaction.objects.filter(lot__added_by=entity, lot__status='Draft').exclude(lot__parent_lot=None)
        draft = tx_drafts.count()
        tx_inbox = LotTransaction.objects.filter(carbure_client=entity, lot__status='Validated', delivery_status__in=['N', 'AC', 'AA'])
        inbox = tx_inbox.count()
        tx_stock = LotTransaction.objects.filter(carbure_client=entity, lot__status="Validated", delivery_status='A', lot__fused_with=None, lot__volume__gt=0)
        stock = tx_stock.count()
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
def get_depots(request, *args, **kwargs):
    context = kwargs['context']
    entity = context['entity']
    biocarburant_code = request.GET.get('biocarburant_code', False)

    # return list of depots that have a stock
    stock = LotTransaction.objects.filter(carbure_client=entity, lot__status="Validated", delivery_status='A', lot__fused_with=None, lot__volume__gt=0)
    if biocarburant_code:
        stock = stock.filter(lot__biocarburant__code=biocarburant_code)

    depots = sorted(list(set([s.carbure_delivery_site.name if s.carbure_delivery_site else s.unknown_delivery_site for s in stock])))
    return JsonResponse({'status': 'success', 'data': depots})


@check_rights('entity_id')
def create_drafts(request, *args, **kwargs):
    context = kwargs['context']
    entity_id = request.POST.get('entity_id', False)
    drafts = request.POST.get('drafts', False)
    if not entity_id:
        return JsonResponse({'status': 'error', 'message': "Missing entity_id"}, status=400)
    if not drafts:
        return JsonResponse({'status': 'error', 'message': "Missing drafts"}, status=400)

    # prefetch some data
    d = get_prefetched_data(context['entity'])
    lots = []
    txs = []
    lot_errors = []
    tx_errors = []
    try:
        print(drafts)
        drafts = json.loads(drafts)
    except Exception as e:
        print(e)
        return JsonResponse({'status': 'error', 'message': "Drafts is invalid json"}, status=400)

    for i, draft in enumerate(drafts):
        lot_dict = {}
        if not 'tx_id' in draft:
            return JsonResponse({'status': 'error', 'message': "Missing tx_id in draft %d" % (i)}, status=400)
        lot_dict['tx_id'] = draft['tx_id']
        if not 'volume' in draft:
            return JsonResponse({'status': 'error', 'message': "Missing volume in draft %d" % (i)}, status=400)
        lot_dict['volume'] = draft['volume']
        if 'client' not in draft:
            return JsonResponse({'status': 'error', 'message': "Missing client in draft %d" % (i)}, status=400)
        lot_dict['client'] = draft['client']
        if 'delivery_site' not in draft:
            return JsonResponse({'status': 'error', 'message': "Missing delivery_site in draft %d" % (i)}, status=400)
        lot_dict['delivery_site'] = draft['delivery_site']
        if 'delivery_date' not in draft:
            return JsonResponse({'status': 'error', 'message': "Missing delivery_date in draft %d" % (i)}, status=400)
        lot_dict['delivery_date'] = draft['delivery_date']
        if 'dae' not in draft:
            return JsonResponse({'status': 'error', 'message': "Missing dae in draft %d" % (i)}, status=400)
        lot_dict['dae'] = draft['dae']
        if 'delivery_site_country' in draft:
            lot_dict['delivery_site_country'] = draft['delivery_site_country']
        # create sub-transaction
        lot, tx, lot_errors, tx_errors = load_mb_lot(d, context['entity'], request.user, lot_dict, 'MANUAL')
        if not tx:
            return JsonResponse({'status': 'error', 'message': 'Could not add lot %d to database: %s' % (i, lot_errors)}, status=400)
        lots.append(lot)
        txs.append(tx)
        lot_errors += lot_errors
        tx_errors += tx_errors
    new_lots, new_txs = bulk_insert(context['entity'], lots, txs, lot_errors, tx_errors, d)
    return JsonResponse({'status': 'success'})


@check_rights('entity_id')
def get_template_mass_balance(request, *args, **kwargs):
    context = kwargs['context']
    entity = context['entity']

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

@check_rights('entity_id')
def get_template_mass_balance_bcghg(request, *args, **kwargs):
    context = kwargs['context']
    entity = context['entity']
    
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

@check_rights('entity_id')
def upload_mass_balance(request, *args, **kwargs):
    context = kwargs['context']
    entity = context['entity']
    file = request.FILES.get('file')
    if file is None:
        return JsonResponse({'status': "error", 'message': "Missing File"}, status=400)
    
    # save file
    now = datetime.datetime.now()
    filename = '%s_%s.xlsx' % (now.strftime('%Y%m%d'), entity.name.upper())
    filepath = '/tmp/%s' % (filename)
    with open(filepath, 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)

    nb_loaded, nb_total, errors = load_excel_file(entity, request.user, file, mass_balance=True)
    if nb_loaded is False:
        return JsonResponse({'status': 'error', 'message': 'Could not load Excel file'})
    data = {'loaded': nb_loaded, 'total': nb_total}
    return JsonResponse({'status': 'success', 'data': data})


# given a set of objectives and constraints, outputs a list of lots/sublots that solves the problem
@check_rights('entity_id')
def generate_batch(request, *args, **kwargs):
    context = kwargs['context']
    entity = context['entity']
    volume = request.GET.get('volume', False)
    biocarburant = request.GET.get('biocarburant_code', False)
    depot_source = request.GET.get('depot_id', False)
    mp_blacklist = request.GET.getlist('mp_blacklist', False)
    ghg_target = request.GET.get('ghg_target', False)

    if not biocarburant:
        return JsonResponse({'status': "error", 'message': "Missing biocarburant_code"}, status=400)
    if not volume:
        return JsonResponse({'status': "error", 'message': "Missing volume"}, status=400)


    # get current stock
    txs = LotTransaction.objects.filter(carbure_client=entity, lot__status="Validated", delivery_status='A', lot__fused_with=None, lot__volume__gt=0)
    # filter by requested biofuel
    txs = txs.filter(lot__biocarburant__code=biocarburant)

    stock_per_depot = {}
    for tx in txs:
        if tx.delivery_site_is_in_carbure:
            if tx.carbure_delivery_site not in stock_per_depot:
                stock_per_depot[tx.carbure_delivery_site] = []
            stock_per_depot[tx.carbure_delivery_site].append(tx)
        else:
            if tx.unknown_delivery_site not in stock_per_depot:
                stock_per_depot[tx.unknown_delivery_site] = []
            stock_per_depot[tx.unknown_delivery_site].append(tx)
    # filter by depot_source if requested
    depots_to_check = stock_per_depot.keys()
    if depot_source:
        if depot_source not in stock_per_depot:
            return JsonResponse({'status': 'error', 'message': 'Could not find enough volume in depot %s' % (depot_source)}, status=400)
        else:
            depots_to_check = [stock_per_depot[depot_source]]

    # do the actual calculations
    for depot in depots_to_check:
        # do we have enough volume ?
        pass

    return JsonResponse({'status': 'success', 'data': []})

@otp_required
def send_drafts(request):
    tx_ids = request.POST.getlist('tx_ids', False)

    if not tx_ids:
        return JsonResponse({'status': 'forbidden', 'message': "Missing tx_ids"}, status=403)

    rights = [r.entity for r in UserRights.objects.filter(user=request.user)]
    send_errors = []
    for tx_id in tx_ids:
        try:
            tx = LotTransaction.objects.get(id=tx_id)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': "Unknown Transaction %s" % (tx_id), 'extra': str(e)},
                                status=400)

        sent, errors = send_lot_from_stock(rights, tx)
        if not sent:
            send_errors.append(errors)

    return JsonResponse({'status': 'success', 'data': send_errors})

@check_rights('entity_id')
def send_all_drafts(request, *args, **kwargs):
    context = kwargs['context']
    entity = context['entity']

    rights = [r.entity for r in UserRights.objects.filter(user=request.user)]
    stock_transactions_drafts = LotTransaction.objects.filter(lot__added_by=entity, lot__status='Draft').exclude(lot__parent_lot__isnull=True)
    send_errors = []
    for tx in stock_transactions_drafts:
        sent, errors = send_lot_from_stock(rights, tx)
        if not sent:
            send_errors.append(errors)
    return JsonResponse({'status': 'success', 'data': send_errors})

def convert_eth_stock_to_etbe(request, entity, c):
    previous_stock_tx_id = c['previous_stock_tx_id']
    volume_ethanol = c['volume_ethanol']
    volume_etbe = c['volume_etbe']
    volume_fossile = c['volume_fossile']
    volume_denaturant = c['volume_denaturant']
    volume_pertes = c['volume_pertes']
    etbe = Biocarburant.objects.get(code='ETBE')

    # retrieve stock line
    previous_stock_tx = LotTransaction.objects.get(carbure_client=entity, delivery_status='A', id=previous_stock_tx_id)
    # check if source TX is Ethanol
    if previous_stock_tx.lot.biocarburant.code != 'ETH': 
        raise Exception("Only ETH can be converted to ETBE") 


    previous_lot_id = previous_stock_tx.lot.pk
    new_lot = LotV2.objects.get(pk=previous_lot_id)
    # new_lot = previous_stock_tx.lot
    new_lot.pk = None
    new_lot.added_by = entity
    new_lot.data_origin_entity    
    new_lot.added_by_user = request.user
    new_lot.save()
    new_lot.carbure_id = generate_carbure_id(new_lot)
    new_lot.is_transformed = True
    new_lot.source = 'MANUAL'
    new_lot.biocarburant = etbe

    volume_ethanol = float(volume_ethanol)
    volume_etbe = float(volume_etbe)
    volume_denaturant = float(volume_denaturant)
    volume_fossile = float(volume_fossile)
    volume_pertes = float(volume_pertes)
    

    # ensure volume etbe = sum of other volume
    if volume_etbe != volume_ethanol + volume_fossile + volume_denaturant + volume_pertes:
        raise Exception("Volumes ETBE != Volume Ethanol + Pertes")

    # check available volume
    if previous_stock_tx.lot.volume < volume_ethanol:
        raise Exception("Cannot convert more ETH than stock") 

    previous_stock_tx.lot.volume -= volume_ethanol
    previous_stock_tx.lot.save()

    new_lot.volume = volume_etbe
    new_lot.parent_lot = LotV2.objects.get(pk=previous_lot_id)
    new_lot.save()

    # create transaction
    transaction = previous_stock_tx
    transaction.pk = None
    transaction.lot = new_lot
    transaction.vendor_is_in_carbure = True
    transaction.carbure_vendor = entity
    transaction.dae = 'CONVERSION-ETBE'
    transaction.champ_libre = 'CONVERSION-ETBE'
    transaction.save()

    # save ETBE Transformation
    t = ETBETransformation()
    t.previous_stock = previous_stock_tx
    t.new_stock = transaction
    t.volume_ethanol = volume_ethanol
    t.volume_etbe = volume_etbe
    t.volume_denaturant = volume_denaturant
    t.volume_fossile = volume_fossile
    t.volume_pertes = volume_pertes
    t.added_by = entity
    t.added_by_user = request.user
    t.save()    


@check_rights('entity_id')
def convert_to_etbe(request, *args, **kwargs):
    context = kwargs['context']
    entity = context['entity']

    conversions = request.POST.get('conversions', False)
    if not conversions:
        return JsonResponse({'status': 'error', 'message': 'Missing conversions'}, status=400)

    try:
        cs = json.loads(conversions)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': 'Could not deserialize POST data'}, status=400)

    for c in cs:
        try:
            convert_eth_stock_to_etbe(request, entity, c)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    return JsonResponse({'status': 'success'})





