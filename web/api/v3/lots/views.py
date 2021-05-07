import datetime
import calendar
import logging
import unicodedata
import os
from dateutil.relativedelta import *
from django.db.models import Q, F, Case, When, Count
from django.db.models.functions import TruncMonth
from django.db.models.functions import Extract
from django.db.models.fields import NOT_PROVIDED
from django import db
from django.http import JsonResponse, HttpResponse
from django.db import transaction

from core.models import LotV2, LotTransaction, LotV2Error, TransactionError, EntityDepot
from core.models import Entity, UserRights, MatierePremiere, Biocarburant, Pays, TransactionComment, SustainabilityDeclaration
from core.xlsx_v3 import template_producers_simple, template_producers_advanced, template_operators, template_traders
from core.xlsx_v3 import export_transactions
from core.common import validate_lots, load_excel_file, load_lot, bulk_insert, get_prefetched_data, check_duplicates, send_rejection_emails, get_uploaded_files_directory
from api.v3.sanity_checks import bulk_sanity_checks
from django_otp.decorators import otp_required
from core.decorators import check_rights
from api.v3.lots.helpers import get_entity_lots_by_status, get_lots_with_metadata, get_snapshot_filters, get_errors, get_summary, filter_entity_transactions

logger = logging.getLogger(__name__)


@check_rights('entity_id')
def get_lots(request, *args, **kwargs):
    context = kwargs['context']
    entity = context['entity']

    status = request.GET.get('status', False)
    
    if not status:
        return JsonResponse({'status': 'error', 'message': 'Missing status'}, status=400)

    try:
        txs = get_entity_lots_by_status(entity, status)
        return get_lots_with_metadata(txs, entity, request.GET)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


@check_rights('entity_id')
def get_lots_summary(request, *args, **kwargs):
    context = kwargs['context']
    entity = context['entity']

    selection = request.GET.getlist('selection')

    try:
        if len(selection) > 0:
            txs = LotTransaction.objects.filter(pk__in=selection)
        else:
            txs, _, _, _ = filter_entity_transactions(entity, request.GET)
        data = get_summary(txs, entity)
        return JsonResponse({'status': 'success', 'data': data})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

@check_rights('entity_id')
def get_details(request, *args, **kwargs):
    context = kwargs['context']
    entity = context['entity']
    tx_id = request.GET.get('tx_id', False)

    if not tx_id:
        return JsonResponse({'status': 'error', 'message': 'Missing tx_id'}, status=400)

    tx = LotTransaction.objects.get(pk=tx_id)

    if tx.carbure_client != entity and tx.carbure_vendor != entity and tx.lot.added_by != entity:
        return JsonResponse({'status': 'forbidden', 'message': "User not allowed"}, status=403)

    now = datetime.datetime.now()
    (_, last_day) = calendar.monthrange(now.year, now.month)
    deadline_date = now.replace(day=last_day)

    data = {}
    data['transaction'] = tx.natural_key()
    data['errors'] = get_errors(tx)
    data['deadline'] = deadline_date.strftime("%Y-%m-%d")
    data['comments'] = []
    for c in tx.transactioncomment_set.all():
        comment = c.natural_key()
        if c.entity not in [tx.lot.added_by, tx.carbure_client]:
            comment['entity'] = {'name': 'Anonyme'}
        data['comments'].append(comment)

    return JsonResponse({'status': 'success', 'data': data})

@check_rights('entity_id')
def get_snapshot(request, *args, **kwargs):
    context = kwargs['context']
    entity = context['entity']
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

    if entity.entity_type == 'Producteur' or entity.entity_type == 'Trader':
        txs = LotTransaction.objects.filter(carbure_vendor=entity)
        data['years'] = [t.year for t in txs.dates('delivery_date', 'year', order='DESC')]
        txs = txs.filter(delivery_date__gte=date_from).filter(delivery_date__lte=date_until)
        draft = txs.filter(lot__status='Draft', lot__parent_lot=None).count()
        validated = txs.filter(lot__status='Validated', delivery_status__in=['N', 'AA']).count()
        tofix = txs.filter(lot__status='Validated', delivery_status__in=['AC', 'R']).count()
        accepted = txs.filter(lot__status='Validated', delivery_status='A').count()
        data['lots'] = {'draft': draft, 'validated': validated, 'tofix': tofix, 'accepted': accepted}
    elif entity.entity_type == 'Opérateur':
        txs = LotTransaction.objects.filter(Q(carbure_client=entity) | Q(lot__added_by=entity, is_mac=True))
        data['years'] = [t.year for t in txs.dates('delivery_date', 'year', order='DESC')]
        txs = txs.filter(delivery_date__gte=date_from).filter(delivery_date__lte=date_until)
        draft = txs.filter(lot__added_by=entity, lot__status='Draft').count()
        ins = txs.filter(lot__status='Validated', delivery_status__in=['N', 'AA', 'AC'], is_mac=False).count()
        accepted = txs.filter(lot__status='Validated', delivery_status='A').count()
        data['lots'] = {'draft': draft, 'accepted': accepted, 'in': ins}
    else:
        return JsonResponse({'status': 'error', 'message': "Unknown entity_type"}, status=400)

    filters = get_snapshot_filters(txs)

    if entity.entity_type == 'Producteur':
        c1 = [c['carbure_client__name'] for c in txs.values('carbure_client__name').distinct()]
        c2 = [c['unknown_client'] for c in txs.values('unknown_client').distinct()]
        clients = [c for c in c1 + c2 if c]
        filters['clients'] = clients
    elif entity.entity_type == 'Opérateur':
        v1 = [v['carbure_vendor__name'] for v in txs.values('carbure_vendor__name').distinct()]
        v2 = [v['lot__unknown_supplier'] for v in txs.values('lot__unknown_supplier').distinct()]
        vendors = [v for v in v1 + v2 if v]
        filters['vendors'] = vendors

    data['filters'] = filters

    depots = [d.natural_key() for d in EntityDepot.objects.filter(entity=entity)]
    data['depots'] = depots

    return JsonResponse({'status': 'success', 'data': data})


@check_rights('entity_id')
def get_declaration_summary(request, *args, **kwargs):
    context = kwargs['context']
    entity = context['entity']

    period_year = request.POST.get('period_year', None)
    period_month = request.POST.get('period_month', None)

    if period_month is None or period_year is None:
        return JsonResponse({'status': "error", 'message': "Missing periods"}, status=400)

    period_date = datetime.date(year=int(period_year), month=int(period_month), day=1)
    period_str = period_date.strftime('%Y-%m')

    txs = LotTransaction.objects.filter(lot__status='Validated', lot__period=period_str)
    data = get_summary(txs, entity)

    # get associated declaration
    declaration, created = SustainabilityDeclaration.objects.get_or_create(entity=entity, period=period_date)
    data['declaration'] = declaration.natural_key()
    return JsonResponse({'status': 'success', 'data': data})


@check_rights('entity_id')
def add_lot(request, *args, **kwargs):
    context = kwargs['context']
    entity = context['entity']

    # prefetch some data
    d = get_prefetched_data(entity)
    lot, tx, lot_errors, tx_errors = load_lot(d, entity, request.user, request.POST.dict(), 'MANUAL')
    if not tx:
        return JsonResponse({'status': 'error', 'message': 'Could not add lot to database'}, status=400)
    new_lots, new_txs = bulk_insert(entity, [lot], [tx], [lot_errors], [tx_errors], d)
    if len(new_txs) == 0:
        print(request.POST)
        return JsonResponse({'status': 'error', 'message': 'Something went wrong'}, status=500)
    lot_data = new_txs[0].natural_key()
    return JsonResponse({'status': 'success', 'data': lot_data})


@check_rights('entity_id')
def update_lot(request, *args, **kwargs):
    context = kwargs['context']
    entity = context['entity']

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
        bulk_sanity_checks([tx], d, background=False)
        # only if lot is already validated ?
        if lot.status == 'Validated':
            # make sure we do not create a duplicate
            check_duplicates([tx], background=False)
        return JsonResponse({'status': 'success'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Could not save lot: %s' % (lot_errors)}, status=400)

@otp_required
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

@otp_required
def delete_lot(request):
    tx_ids = request.POST.getlist('tx_ids', False)

    if not tx_ids:
        return JsonResponse({'status': 'forbidden', 'message': "Missing tx_ids"}, status=403)

    deleted = 0
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

        if tx.delivery_status == 'R' and tx.lot.parent_lot != None:
            # credit volume back to stock
            tx.lot.parent_lot.remaining_volume += tx.lot.volume
            tx.lot.parent_lot.save()
        tx.lot.delete()
        deleted += 1
    return JsonResponse({'status': 'success', 'deleted': deleted})


@otp_required
@check_rights('entity_id')
def validate_lot(request, *args, **kwargs):
    context = kwargs['context']
    entity = context['entity']
    tx_ids = request.POST.getlist('tx_ids', None)
    if not tx_ids:
        return JsonResponse({'status': 'forbidden', 'message': "Missing tx_ids"}, status=403)
    txs = LotTransaction.objects.filter(id__in=tx_ids, lot__added_by=entity)
    data = validate_lots(request.user, entity, txs)
    nb_duplicates = check_duplicates(txs, background=False)
    data['duplicates'] = nb_duplicates
    return JsonResponse({'status': 'success', 'data': data})


@otp_required
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


@otp_required
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


@otp_required
def reject_lot(request):
    tx_ids = request.POST.getlist('tx_ids', None)
    tx_comment = request.POST.get('comment', None)
    if not tx_ids:
        return JsonResponse({'status': 'error', 'message': "Missing tx_ids"}, status=400)
    if not tx_comment:
        return JsonResponse({'status': 'error', 'message': "Missing comment"}, status=400)

    tx_rejected = []

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

        # special case
        # if the rejected lot has been forwarded by an operator, the operator has no way to see it
        # so we actually delete the forwarded tx and send an email to the tx source
        if tx.parent_tx != None and tx.carbure_vendor.entity_type == Entity.OPERATOR:
            # cancel forward
            tx.parent_tx.is_forwarded = False
            tx.parent_tx.save()
        tx.comment = tx_comment
        tx_rejected.append(tx)

    send_rejection_emails(tx_rejected)
    return JsonResponse({'status': 'success'})

@check_rights('entity_id')
def comment_lot(request, *args, **kwargs):
    context = kwargs['context']
    entity = context['entity']

    tx_id = request.POST.get('tx_id', None)
    comment = request.POST.get('comment', None)
    comment_type = request.POST.get('comment_type', None)
    if tx_id is None:
        return JsonResponse({'status': 'error', 'message': "Missing TX ID"}, status=400)
    if comment is None:
        return JsonResponse({'status': 'error', 'message': "Missing comment"}, status=400)
    if comment_type is None:
        return JsonResponse({'status': 'error', 'message': "Missing comment_type"}, status=400)

    try:
        tx = LotTransaction.objects.get(id=tx_id)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': "TX not found", 'extra': str(e)}, status=400)

    rights = [r.entity for r in UserRights.objects.filter(user=request.user)]

    # only the client, vendor and producer can comment
    if tx.carbure_client not in rights and tx.carbure_vendor not in rights and tx.lot.carbure_producer not in rights:
        return JsonResponse({'status': 'forbidden', 'message': "User not allowed to comment on this transaction"},
                            status=403)

    txc = TransactionComment()
    txc.entity = entity
    txc.tx = tx
    txc.topic = comment_type
    txc.comment = comment
    txc.save()
    return JsonResponse({'status': 'success'})


@check_rights('entity_id')
def get_template_producers_simple(request, *args, **kwargs):
    context = kwargs['context']
    entity = context['entity']
    
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


@check_rights('entity_id')
def get_template_producers_advanced(request, *args, **kwargs):
    context = kwargs['context']
    entity = context['entity']

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


@check_rights('entity_id')
def get_template_producers_advanced_10k(request, *args, **kwargs):
    context = kwargs['context']
    entity = context['entity']

    file_location = template_producers_advanced(entity, nb_lots=10000)
    try:
        with open(file_location, 'rb') as f:
            file_data = f.read()
            # sending response
            response = HttpResponse(file_data, content_type='application/vnd.ms-excel')
            response['Content-Disposition'] = 'attachment; filename="carbure_template_advanced.xlsx"'
            return response
    except Exception as e:
        return JsonResponse({'status': "error", 'message': "Error creating template file", 'error': str(e)}, status=500)


@check_rights('entity_id')
def get_template_blend(request, *args, **kwargs):
    context = kwargs['context']
    entity = context['entity']
    
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

@check_rights('entity_id')
def get_template_trader(request, *args, **kwargs):
    context = kwargs['context']
    entity = context['entity']
    
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

@check_rights('entity_id')
def upload(request, *args, **kwargs):
    context = kwargs['context']
    entity = context['entity']

    f = request.FILES.get('file')
    if f is None:
        return JsonResponse({'status': "error", 'message': "Missing File"}, status=400)

    # save file
    directory = get_uploaded_files_directory()
    now = datetime.datetime.now()
    filename = '%s_%s.xlsx' % (now.strftime('%Y%m%d.%H%M%S'), entity.name.upper())
    filename = ''.join((c for c in unicodedata.normalize('NFD', filename) if unicodedata.category(c) != 'Mn'))
    filepath = '%s/%s' % (directory, filename)
    with open(filepath, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    nb_loaded, nb_total, errors = load_excel_file(entity, request.user, filepath)
    if nb_loaded is False:
        return JsonResponse({'status': 'error', 'message': 'Could not load Excel file'})
    data = {'loaded': nb_loaded, 'total': nb_total, 'errors': errors}
    return JsonResponse({'status': 'success', 'data': data})

@check_rights('entity_id')
def upload_blend(request, *args, **kwargs):
    context = kwargs['context']
    entity = context['entity']
    f = request.FILES.get('file')
    if f is None:
        return JsonResponse({'status': "error", 'message': "Missing File"}, status=400)

    # save file
    now = datetime.datetime.now()
    directory = get_uploaded_files_directory()
    filename = '%s_%s.xlsx' % (now.strftime('%Y%m%d.%H%M%S'), entity.name.upper())
    filename = ''.join((c for c in unicodedata.normalize('NFD', filename) if unicodedata.category(c) != 'Mn'))
    filepath = '%s/%s' % (directory, filename)
    with open(filepath, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

    nb_loaded, nb_total, errors = load_excel_file(entity, request.user, f)
    if nb_loaded is False:
        return JsonResponse({'status': 'error', 'message': 'Could not load Excel file'})
    data = {'loaded': nb_loaded, 'total': nb_total}
    return JsonResponse({'status': 'success', 'data': data})

@otp_required
@check_rights('entity_id')
def validate_declaration(request, *args, **kwargs):
    context = kwargs['context']
    entity = context['entity']
    period_year = request.POST.get('period_year', None)
    period_month = request.POST.get('period_month', None)

    if period_month is None or period_year is None:
        return JsonResponse({'status': "error", 'message': "Missing periods"}, status=400)
    
    try:
        py = int(period_year)
        pm = int(period_month)
        period = datetime.date(year=py, month=pm, day=1)
        declaration, created = SustainabilityDeclaration.objects.update_or_create(entity=entity, period=period, defaults={'declared': True})
    except Exception as e:
        print("Error while getting period")
        print(e)
        return JsonResponse({'status': "error", 'message': "Missing periods"}, status=400)
    return JsonResponse({'status': 'success'})


@check_rights('entity_id')
def forward_lots(request, *args, **kwargs):
    # note: this is the "Forward" feature for Operators (Processing done by someone else)
    context = kwargs['context']
    entity = context['entity']

    tx_ids = request.POST.getlist('tx_ids', None)
    comment = request.POST.get('comment', '')
    depots = {ed.depot: ed for ed in EntityDepot.objects.filter(entity=entity, blending_is_outsourced=True)}

    if not entity.entity_type == Entity.OPERATOR:
        return JsonResponse({'status': 'forbidden', 'message': "Feature only available to Operators"}, status=403)
    if not tx_ids:
        return JsonResponse({'status': 'error', 'message': "Missing tx_ids"}, status=400)

    for tx_id in tx_ids:
        # for each tx, make sure we are the client, status accepted, not already forwarded, and it has been delivered to a Depot with blending_is_outsourced
        try:
            tx = LotTransaction.objects.get(delivery_status__in=['A', 'N'], id=tx_id, carbure_client=entity, is_forwarded=False)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': "TX not found", 'extra': str(e)}, status=400)

        if tx.carbure_delivery_site in depots:
            # it has been delivered to a Depot with outsourced blending
            # we should forward the lot to the blender
            tx.delivery_status = 'A'
            tx.is_forwarded = True
            tx.save()
            new_tx = tx
            new_tx.pk = None
            new_tx.parent_tx_id = tx.id
            new_tx.is_forwarded = False
            new_tx.carbure_vendor = entity

            new_tx.client_is_in_carbure = True
            new_tx.carbure_client = depots[tx.carbure_delivery_site].blender
            new_tx.unknown_client = ''
            new_tx.delivery_status = 'N'
            new_tx.champ_libre = comment
            new_tx.save()
        else:
            return JsonResponse({'status': 'error', 'message': "Delivery site not registered for outsourcing"}, status=400)

    return JsonResponse({'status': 'success'})    