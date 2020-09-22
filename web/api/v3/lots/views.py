import datetime
import calendar
import dateutil.relativedelta
from django.db.models import Q
from django.db.models.functions import TruncMonth
from django.db.models import Count
from django.db.models.fields import NOT_PROVIDED
from django.http import JsonResponse, HttpResponse
from core.models import LotV2, LotTransaction, LotValidationError
from core.models import Entity, UserRights, MatierePremiere, Biocarburant, Pays, TransactionComment
from core.xlsx_template import create_xslx_from_transactions, create_template_xlsx_v2_simple
from core.xlsx_template import create_template_xlsx_v2_advanced
from core.common import tx_is_valid, lot_is_valid, generate_carbure_id, load_excel_file, load_lot
from api.v3.sanity_checks import sanity_check


def get_lots(request):
    status = request.GET.get('status', False)
    producer = request.GET.get('producer_id', False)
    year = request.GET.get('year', False)
    periods = request.GET.getlist('periods', False)
    production_sites = request.GET.getlist('production_sites', False)
    matieres_premieres = request.GET.getlist('matieres_premieres', False)
    countries_of_origin = request.GET.getlist('countries_of_origin', False)
    biocarburants = request.GET.getlist('biocarburants', False)
    clients = request.GET.getlist('clients', False)
    limit = request.GET.get('limit', "100")
    from_idx = request.GET.get('from_idx', "0")
    export = request.GET.get('export', False)

    if not status:
        return JsonResponse({'status': 'error', 'message': 'Missing status'}, status=400)
    if producer is None:
        return JsonResponse({'status': 'error', 'message': "Missing producer_id"}, status=400)
    try:
        producer = Entity.objects.get(id=producer, entity_type='Producteur')
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': "Unknown producer %s" % (producer), 'extra': str(e)},
                            status=400)

    rights = [r.entity for r in UserRights.objects.filter(user=request.user)]
    if producer not in rights:
        return JsonResponse({'status': 'forbidden', 'message': "User not allowed"}, status=403)

    txs = LotTransaction.objects.filter(lot__carbure_producer=producer)

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
        txs = txs.filter(lot__biocarburant__code__in=matieres_premieres)
    if countries_of_origin:
        txs = txs.filter(lot__pays_origine__code_pays__in=countries_of_origin)
    if clients:
        txs = txs.filter(Q(carbure_client__name__in=clients) | Q(unknown_client__in=clients))

    limit = int(limit)
    from_idx = int(from_idx)
    returned = txs[from_idx:from_idx+limit]

    data = {}
    data['lots'] = [t.natural_key() for t in txs]
    data['total'] = len(txs)
    data['returned'] = len(returned)
    data['from'] = from_idx
    if not export:
        return JsonResponse({'status': 'success', 'data': data})
    else:
        file_location = create_xslx_from_transactions(producer, returned)
        with open(file_location, "rb") as excel:
            data = excel.read()
            ctype = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            response = HttpResponse(data=data, content_type=ctype)
            response['Content-Disposition'] = 'attachment; filename="%s"' % (file_location)
        return response


def get_snapshot(request):
    data = {}
    today = datetime.date.today()

    producer = request.GET.get('producer_id', False)
    if producer is None:
        return JsonResponse({'status': 'error', 'message': "Missing producer_id"}, status=400)
    try:
        producer = Entity.objects.get(id=producer, entity_type='Producteur')
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': "Unknown producer %s" % (producer), 'extra': str(e)},
                            status=400)

    rights = [r.entity for r in UserRights.objects.filter(user=request.user)]
    if producer not in rights:
        return JsonResponse({'status': 'forbidden', 'message': "User not allowed"}, status=403)

    txs = LotTransaction.objects.filter(lot__carbure_producer=producer)

    drafts = len(txs.filter(lot__status='Draft'))
    validated = len(txs.filter(lot__status='Validated', delivery_status__in=['N', 'AA']))
    tofix = len(txs.filter(lot__status='Validated', delivery_status='AC'))
    accepted = len(txs.filter(lot__status='Validated', delivery_status='A'))
    data['lots'] = {'drafts': drafts, 'validated': validated, 'tofix': tofix, 'accepted': accepted}

    mps = [{'key': m.code, 'label': m.name}
           for m in MatierePremiere.objects.filter(id__in=txs.values('lot__matiere_premiere').distinct())]

    bcs = [{'key': b.code, 'label': b.name}
           for b in Biocarburant.objects.filter(id__in=txs.values('lot__biocarburant').distinct())]

    periods = [{'key': i, 'label': p['lot__period']}
               for i, p in enumerate(txs.values('lot__period').distinct()) if p['lot__period']]

    countries = [{'key': c.code_pays, 'label': c.name}
                 for c in Pays.objects.filter(id__in=txs.values('lot__pays_origine').distinct())]

    c1 = [c['carbure_client__name'] for c in txs.values('carbure_client__name').distinct()]
    c2 = [c['unknown_client'] for c in txs.values('unknown_client').distinct()]

    clients = [{'key': i, 'label': c} for i, c in enumerate(c1 + c2) if c]

    ps1 = [p['lot__carbure_production_site__name'] for p in txs.values('lot__carbure_production_site__name').distinct()]
    ps2 = [p['lot__unknown_production_site'] for p in txs.values('lot__unknown_production_site').distinct()]
    psites = [{'key': i, 'label': p} for i, p in enumerate(ps1 + ps2) if p]

    data['filters'] = {'matieres_premieres': mps, 'biocarburants': bcs, 'periods': periods,
                       'production_sites': psites, 'countries_of_origin': countries, 'clients': clients}

    deadlines = txs.filter(lot__status='Draft').annotate(month=TruncMonth(
        'delivery_date')).values('month').annotate(total=Count('id'))
    for d in deadlines:
        if d['month'] is None:
            d['deadline'] = None
        else:
            nextmonth = d['month'] + dateutil.relativedelta.relativedelta(months=+1)
            (_, day) = calendar.monthrange(nextmonth.year, nextmonth.month)
            d['deadline'] = d['month'].replace(month=nextmonth.month, day=day)
            d['delta'] = (d['deadline'] - today).days
    data['deadlines'] = list(deadlines)
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

    load_lot(entity, request.user, request.POST.dict(), 'MANUAL')
    return JsonResponse({'status': 'success'})


def update_lot(request):
    # set is_valid to False
    pass


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
    tx_ids = request.POST.get('tx_ids', None)
    if not tx_ids:
        return JsonResponse({'status': 'forbidden', 'message': "Missing tx_ids"}, status=403)
    for tx_id in tx_ids:
        try:
            tx = LotTransaction.objects.get(id=tx_id, lot__status='Draft')
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': "Draft not found", 'extra': str(e)}, status=400)

        rights = [r.entity for r in UserRights.objects.filter(user=request.user)]
        if tx.lot.added_by not in rights:
            return JsonResponse({'status': 'forbidden', 'message': "User not allowed"}, status=403)

        # make sure all mandatory fields are set
        tx_valid, error = tx_is_valid(tx)
        if not tx_valid:
            return JsonResponse({'status': 'error', 'message': "Invalid transaction: %s" % (error)}, status=400)

        lot_valid, error = lot_is_valid(tx.lot)
        if not lot_valid:
            return JsonResponse({'status': 'error', 'message': "Invalid lot: %s" % (error)}, status=400)

        # run sanity_checks
        sanity_check(tx.lot)
        blocking_sanity_checks = LotValidationError.objects.filter(lot=tx.lot, block_validation=True)
        if len(blocking_sanity_checks):
            tx.lot.is_valid = False
        else:
            tx.lot.is_valid = True
            tx.lot.carbure_id = generate_carbure_id(tx.lot)
            tx.lot.status = "Validated"
        # when the lot is added to mass balance, auto-accept
        if tx.carbure_client == tx.carbure_vendor:
            tx.delivery_status = 'A'
            tx.save()
        tx.lot.save()
    return JsonResponse({'status': 'success'})


def accept_lot(request):
    tx_ids = request.POST.get('tx_ids', None)
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


def reject_lot(request):
    tx_ids = request.POST.get('tx_ids', None)
    if not tx_ids:
        return JsonResponse({'status': 'forbidden', 'message': "Missing tx_ids"}, status=403)
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
    if tx.carbure_client not in rights or tx.carbure_vendor not in rights or tx.lot.carbure_producer not in rights:
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


def check_lot(request):
    tx_ids = request.POST.get('tx_ids', None)
    if not tx_ids:
        return JsonResponse({'status': 'forbidden', 'message': "Missing tx_ids"}, status=400)
    for tx_id in tx_ids:
        try:
            tx = LotTransaction.objects.get(id=tx_id)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': "TX not found", 'extra': str(e)}, status=400)

        rights = [r.entity for r in UserRights.objects.filter(user=request.user)]
        if tx.carbure_client not in rights:
            return JsonResponse({'status': 'forbidden', 'message': "User not allowed"}, status=403)
        sanity_check(tx.lot)
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

    LotTransaction.objects.filter(lot__added_by=entity, lot__status='Draft').delete()
    return JsonResponse({'status': 'success'})


def template_simple(request):
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

    file_location = create_template_xlsx_v2_simple(entity)
    try:
        with open(file_location, 'rb') as f:
            file_data = f.read()
            # sending response
            response = HttpResponse(file_data, content_type='application/vnd.ms-excel')
            response['Content-Disposition'] = 'attachment; filename="carbure_template_simple.xlsx"'
            return response
    except Exception as e:
        return JsonResponse({'status': "error", 'message': "Error creating template file", 'error': str(e)}, status=500)


def template_advanced(request):
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

    file_location = create_template_xlsx_v2_advanced(entity)
    try:
        with open(file_location, 'rb') as f:
            file_data = f.read()
            # sending response
            response = HttpResponse(file_data, content_type='application/vnd.ms-excel')
            response['Content-Disposition'] = 'attachment; filename="carbure_template_advanced.xlsx"'
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
