import json
import datetime
from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from core.models import LotV2, LotTransaction, ETBETransformation, TransactionUpdateHistory
from core.models import Entity, UserRights, MatierePremiere, Biocarburant, Pays, LotV2, Depot
from core.decorators import check_rights
from core.common import get_prefetched_data, load_mb_lot, bulk_insert
from core.common import load_excel_file, send_lot_from_stock, generate_carbure_id
from core.xlsx_v3 import template_stock, template_stock_bcghg
from django_otp.decorators import otp_required
from api.v3.lots.helpers import get_snapshot_filters, get_summary, filter_lots, sort_lots, get_lots_with_metadata


sort_key_to_django_field = {'period': 'lot__period',
                            'biocarburant': 'lot__biocarburant__name',
                            'matiere_premiere': 'lot__matiere_premiere__name',
                            'ghg_reduction': 'lot__ghg_reduction',
                            'volume': 'lot__volume',
                            'pays_origine': 'lot__pays_origine__name',
                            'client': 'carbure_client__name',
                            'vendor': 'carbure_vendor__name',
                            'depot': 'carbure_delivery_site',
                            }


def filter_stock_transactions(entity, querySet):
    status = querySet.get('status', False)
    show_empty = querySet.get('show_empty', False)
    if show_empty == '1':
        show_empty = True
    else:
        show_empty = False

    if not status:
        raise Exception('Status is not specified')

    if entity.entity_type not in (Entity.PRODUCER, Entity.TRADER):
        raise Exception('Entity does not have stocks')

    if status == 'tosend':
        return LotTransaction.objects.filter(lot__added_by=entity, lot__status='Draft').exclude(lot__parent_lot=None)
    elif status == 'in':
        return LotTransaction.objects.filter(carbure_client=entity, lot__status='Validated', delivery_status__in=[LotTransaction.PENDING, LotTransaction.TOFIX, LotTransaction.FIXED])
    elif status == 'stock':
        stock = LotTransaction.objects.filter(carbure_client=entity, lot__status='Validated', delivery_status__in=[LotTransaction.ACCEPTED, LotTransaction.FROZEN], lot__fused_with=None, is_forwarded=False, is_mac=False)
        if not show_empty:
            stock = stock.filter(lot__remaining_volume__gt=0)
        return stock
    else:
        raise Exception('Unknown status')


@check_rights('entity_id')
def get_stocks(request, *args, **kwargs):
    context = kwargs['context']
    entity = context['entity']

    try:
        txs = filter_stock_transactions(entity, request.GET)
        return get_lots_with_metadata(txs, entity, request.GET)
    except Exception:
        return JsonResponse({'status': 'error', 'message': "Could not get lots"}, status=400)


@check_rights('entity_id')
def get_stocks_summary(request, *args, **kwargs):
    context = kwargs['context']
    entity = context['entity']

    short = request.GET.get('short', False)

    try:
        txs = filter_stock_transactions(entity, request.GET)
        txs = filter_lots(txs, request.GET)[0]
        txs = sort_lots(txs, request.GET)
        data = get_summary(txs, entity, short)
        return JsonResponse({'status': 'success', 'data': data})
    except Exception:
        return JsonResponse({'status': 'error', 'message': "Could not get lots summary"}, status=400)


@check_rights('entity_id')
def get_snapshot(request, *args, **kwargs):
    context = kwargs['context']
    entity = context['entity']

    data = {}

    if entity.entity_type in ['Producteur', 'Trader']:
        # drafts are lot that will be extracted from mass balance and sent to a client
        tx_drafts = LotTransaction.objects.filter(lot__added_by=entity, lot__status='Draft').exclude(lot__parent_lot=None)
        draft = tx_drafts.count()
        tx_inbox = LotTransaction.objects.filter(carbure_client=entity, lot__status='Validated', delivery_status__in=[LotTransaction.PENDING, LotTransaction.TOFIX, LotTransaction.FIXED])
        inbox = tx_inbox.count()
        tx_stock = LotTransaction.objects.filter(carbure_client=entity, lot__status="Validated", delivery_status__in=[LotTransaction.ACCEPTED, LotTransaction.FROZEN], lot__fused_with=None, lot__remaining_volume__gt=0, is_forwarded=False, is_mac=False)
        stock = tx_stock.count()
        data['lots'] = {'in': inbox,  'stock': stock, 'tosend': draft}
    else:
        return JsonResponse({'status': 'error', 'message': "Unknown entity_type"}, status=400)

    data['filters'] = [
        'periods',
        'biocarburants',
        'matieres_premieres',
        'countries_of_origin',
        'vendors',
        'production_sites',
        'delivery_sites'
    ]

    return JsonResponse({'status': 'success', 'data': data})


@check_rights('entity_id')
def get_filters(request, *args, **kwargs):
    context = kwargs['context']
    entity = context['entity']
    field = request.GET.get('field', False)
    if not field:
        return JsonResponse({'status': 'error', 'message': 'Please specify the field for which you want the filters'}, status=400)

    txs = filter_stock_transactions(entity, request.GET)
    txs = filter_lots(txs, request.GET, [field])[0]

    d = get_snapshot_filters(txs, entity, [field])
    if field in d:
        values = d[field]
    else:
        return JsonResponse({'status': 'error', 'message': "Something went wrong"}, status=400)
    return JsonResponse({'status': 'success', 'data': values})


@check_rights('entity_id')
def get_depots(request, *args, **kwargs):
    context = kwargs['context']
    entity = context['entity']
    biocarburant_code = request.GET.get('biocarburant_code', False)

    # return list of depots that have a stock
    stock = LotTransaction.objects.filter(carbure_client=entity, lot__status="Validated", delivery_status__in=[LotTransaction.ACCEPTED, LotTransaction.FROZEN], lot__fused_with=None, lot__volume__gt=0)
    if biocarburant_code:
        stock = stock.filter(lot__biocarburant__code=biocarburant_code)

    depots = sorted(list(set([s.carbure_delivery_site.name if s.carbure_delivery_site else s.unknown_delivery_site for s in stock])))
    return JsonResponse({'status': 'success', 'data': depots})


@check_rights('entity_id', role=[UserRights.RW, UserRights.ADMIN])
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
    all_errors = []
    try:
        drafts = json.loads(drafts)
    except Exception:
        return JsonResponse({'status': 'error', 'message': "Drafts is invalid json"}, status=400)

    for i, draft in enumerate(drafts):
        lot_dict = {}
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
        if 'mac' in draft:
            lot_dict['mac'] = draft['mac']
        if 'delivery_site_country' in draft:
            lot_dict['delivery_site_country'] = draft['delivery_site_country']
        if 'vendor_certificate' in draft:
            lot_dict['vendor_certificate'] = draft['vendor_certificate']


        # matching engine keys
        for key in ['tx_id', 'biocarburant_code', 'matiere_premiere_code', 'depot', 'pays_origine_code', 'ghg_total']:
            if key in draft:
                lot_dict[key] = draft[key]
        # create sub-transaction
        lot, tx, errors = load_mb_lot(d, context['entity'], request.user, lot_dict, 'MANUAL')
        if tx is None or not tx:
            return JsonResponse({'status': 'error', 'message': 'Could not add lot %d to database: %s' % (i, errors)}, status=400)
        lots.append(lot)
        txs.append(tx)
        all_errors.append(errors)
    new_lots, new_txs = bulk_insert(context['entity'], lots, txs, all_errors, d)
    return JsonResponse({'status': 'success', 'data': {'tx_ids': [tx.id for tx in new_txs]}})


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
    except Exception:
        return JsonResponse({'status': "error", 'message': "Error creating template file"}, status=500)

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
    except Exception:
        return JsonResponse({'status': "error", 'message': "Error creating template file"}, status=500)

@check_rights('entity_id', role=[UserRights.RW, UserRights.ADMIN])
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
@check_rights('entity_id', role=[UserRights.RW, UserRights.ADMIN])
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
    txs = LotTransaction.objects.filter(carbure_client=entity, lot__status="Validated", delivery_status__in=[LotTransaction.ACCEPTED, LotTransaction.FROZEN], lot__fused_with=None, lot__volume__gt=0)
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

@check_rights('entity_id', role=[UserRights.RW, UserRights.ADMIN])
def send_drafts(request, *args, **kwargs):
    context = kwargs['context']
    entity = context['entity']
    tx_ids = request.POST.getlist('tx_ids', False)
    if not tx_ids:
        return JsonResponse({'status': 'forbidden', 'message': "Missing tx_ids"}, status=403)

    prefetched_data = get_prefetched_data(entity)
    rights = [r.entity for r in UserRights.objects.filter(user=request.user)]
    valid_counter = 0
    invalid_counter = 0
    send_errors = []
    for tx_id in tx_ids:
        try:
            tx = LotTransaction.objects.get(id=tx_id)
            prev_remaining_volume = tx.lot.parent_lot.remaining_volume
        except Exception:
            return JsonResponse({'status': 'error', 'message': "Unknown Transaction %s" % (tx_id)},
                                status=400)
        sent, errors = send_lot_from_stock(rights, tx, prefetched_data)
        if sent:
            valid_counter += 1
            parent_tx = LotTransaction.objects.filter(lot=tx.lot.parent_lot).last()
            TransactionUpdateHistory.objects.create(tx=parent_tx, update_type=TransactionUpdateHistory.UPDATE, field='remaining_volume', value_before=prev_remaining_volume, value_after=parent_tx.lot.remaining_volume, modified_by=request.user, modified_by_entity=entity)
        else:
            invalid_counter += 1
            send_errors.append(errors)

    status_code = 200 if valid_counter > 0 else 400
    status = 'success' if valid_counter > 0 else 'error'
    total = valid_counter + invalid_counter
    data = { 'valid': valid_counter, 'invalid': invalid_counter, 'total': total, 'errors': send_errors }
    return JsonResponse({'status': status, 'data': data}, status=status_code)


def convert_eth_stock_to_etbe(request, entity, c):
    previous_stock_tx_id = c['previous_stock_tx_id']
    volume_ethanol = c['volume_ethanol']
    volume_etbe = c['volume_etbe']
    volume_denaturant = c['volume_denaturant']
    volume_etbe_eligible = c['volume_etbe_eligible']
    etbe = Biocarburant.objects.get(code='ETBE')

    # retrieve stock line
    previous_stock_tx = LotTransaction.objects.get(carbure_client=entity, delivery_status__in=[LotTransaction.ACCEPTED, LotTransaction.FROZEN], id=previous_stock_tx_id)
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
    volume_etbe_eligible = float(volume_etbe_eligible)
    volume_denaturant = float(volume_denaturant)


    # check available volume
    if previous_stock_tx.lot.remaining_volume < volume_ethanol:
        raise Exception("Cannot convert more ETH than stock")

    previous_stock_tx.lot.remaining_volume -= volume_ethanol
    previous_stock_tx.lot.save()

    new_lot.volume = volume_etbe
    new_lot.remaining_volume = volume_etbe
    new_lot.parent_lot = LotV2.objects.get(pk=previous_lot_id)
    new_lot.save()

    # create transaction
    transaction = previous_stock_tx
    transaction.pk = None
    transaction.lot = new_lot
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
    t.volume_etbe_eligible = volume_etbe_eligible
    t.volume_denaturant = volume_denaturant
    t.added_by = entity
    t.added_by_user = request.user
    t.save()


@check_rights('entity_id', role=[UserRights.RW, UserRights.ADMIN])
def convert_to_etbe(request, *args, **kwargs):
    context = kwargs['context']
    entity = context['entity']

    conversions = request.POST.get('conversions', False)
    if not conversions:
        return JsonResponse({'status': 'error', 'message': 'Missing conversions'}, status=400)

    try:
        cs = json.loads(conversions)
    except Exception:
        return JsonResponse({'status': 'error', 'message': 'Could not deserialize POST data'}, status=400)

    for c in cs:
        try:
            convert_eth_stock_to_etbe(request, entity, c)
        except Exception:
            return JsonResponse({'status': 'error'}, status=400)

    return JsonResponse({'status': 'success'})


@check_rights('entity_id', role=[UserRights.RW, UserRights.ADMIN])
def forward(request, *args, **kwargs):
    context = kwargs['context']
    entity = context['entity']
    tx_ids = request.POST.getlist('tx_ids', None)
    recipient = request.POST.get('recipient', None)
    certificate_id = request.POST.get('certificate_id', None)

    prefetched_data = get_prefetched_data(entity)
    if not tx_ids:
        return JsonResponse({'status': 'error', 'message': "Missing tx_ids"}, status=400)
    if not recipient:
        return JsonResponse({'status': 'error', 'message': "Missing recipient"}, status=400)

    if certificate_id not in prefetched_data['my_vendor_certificates']:
        return JsonResponse({'status': 'error', 'message': "Unknown certificate"}, status=400)

    # make some checks on the client
    try:
        client = Entity.objects.get(id=recipient)
    except:
        return JsonResponse({'status': 'error', 'message': "Unknown recipient"}, status=400)

    nbforwarded = 0
    for tx_id in tx_ids:
        # for each tx, make sure we are the client, status accepted, and it has not been already forwarded
        try:
            tx = LotTransaction.objects.get(delivery_status__in=[LotTransaction.ACCEPTED, LotTransaction.FROZEN, LotTransaction.PENDING], id=tx_id, carbure_client=entity, is_forwarded=False)
            parent_tx_id = tx.id
        except Exception:
            return JsonResponse({'status': 'error', 'message': "Transaction already forwarded"}, status=400)

        # all good
        # make current tx as "is_forwarded" and create the next tx
        if tx.delivery_status == LotTransaction.PENDING:
            tx.delivery_status = LotTransaction.ACCEPTED
        tx.is_forwarded = True
        tx.save()

        new_tx = tx
        new_tx.pk = None
        new_tx.parent_tx = LotTransaction.objects.get(id=parent_tx_id)
        new_tx.is_forwarded = False
        new_tx.carbure_vendor = entity
        new_tx.carbure_vendor_certificate = certificate_id
        new_tx.client_is_in_carbure = True
        new_tx.carbure_client = client
        new_tx.unknown_client = ''
        new_tx.delivery_status = LotTransaction.PENDING
        new_tx.save()
        nbforwarded += 1

    return JsonResponse({'status': 'success', 'data': {'forwarded': nbforwarded}})
