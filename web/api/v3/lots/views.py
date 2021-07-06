import datetime
import calendar
import logging
import unicodedata
import traceback

import dictdiffer
from dateutil.relativedelta import *
from django.contrib.auth.models import User
from django.db.models import Q
from django.db.models.fields import NOT_PROVIDED
from django.http import JsonResponse, HttpResponse
from django.db import transaction
from django_otp.decorators import otp_required
from numpy.lib.arraysetops import isin

from core.models import Entity, UserRights, TransactionComment, SustainabilityDeclaration
from core.models import LotV2, LotTransaction, EntityDepot, GenericError
from core.models import TransactionUpdateHistory

from core.xlsx_v3 import template_producers_simple, template_producers_advanced, template_operators, template_traders
from core.common import validate_lots, load_excel_file, load_lot, bulk_insert, get_prefetched_data, check_duplicates, get_uploaded_files_directory
from core.common import check_certificates, get_transaction_distance
from core.decorators import check_rights
from core.notifications import notify_lots_rejected, notify_declaration_invalidated, notify_accepted_lot_in_correction
from api.v3.sanity_checks import bulk_sanity_checks
from api.v3.lots.helpers import get_entity_lots_by_status, get_lots_with_metadata, get_snapshot_filters, get_errors, get_summary, sort_lots, filter_lots


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
    except Exception:
        return JsonResponse({'status': 'error', 'message': "Could not get lots"}, status=400)


@check_rights('entity_id')
def get_lots_summary(request, *args, **kwargs):
    context = kwargs['context']
    entity = context['entity']

    status = request.GET.get('status', False)
    short = request.GET.get('short', False)

    if not status:
        raise Exception("Status is not specified")

    try:
        txs = get_entity_lots_by_status(entity, status)
        txs = filter_lots(txs, request.GET)[0]
        txs = sort_lots(txs, request.GET)
        data = get_summary(txs, entity, short)
        return JsonResponse({'status': 'success', 'data': data})
    except Exception:
        return JsonResponse({'status': 'error', 'message': "Could not get lots summary"}, status=400)


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
    data['distance'] = get_transaction_distance(tx)
    data['errors'] = get_errors(tx)
    data['deadline'] = deadline_date.strftime("%Y-%m-%d")
    data['certificates'] = check_certificates(tx)
    data['updates'] = [c.natural_key() for c in tx.transactionupdatehistory_set.all().order_by('-datetime')]
    data['comments'] = []
    for c in tx.transactioncomment_set.all():
        comment = c.natural_key()
        data['comments'].append(comment)

    return JsonResponse({'status': 'success', 'data': data})

@check_rights('entity_id')
def get_snapshot(request, *args, **kwargs):
    context = kwargs['context']
    entity = context['entity']
    data = {}
    year = request.GET.get('year', False)
    if year:
        try:
            year = int(year)
        except Exception:
            return JsonResponse({'status': 'error', 'message': 'Incorrect format for year. Expected YYYY'}, status=400)

    if entity.entity_type in [Entity.PRODUCER, Entity.TRADER]:
        txs = LotTransaction.objects.filter(carbure_vendor=entity)
        data['years'] = [t.year for t in txs.dates('delivery_date', 'year', order='DESC')]
        txs = txs.filter(lot__year=year)
        draft = txs.filter(lot__status=LotV2.DRAFT, lot__parent_lot=None).count()
        validated = txs.filter(lot__status=LotV2.VALIDATED, delivery_status__in=[LotTransaction.PENDING, LotTransaction.FIXED]).count()
        tofix = txs.filter(lot__status=LotV2.VALIDATED, delivery_status__in=[LotTransaction.TOFIX, LotTransaction.REJECTED]).count()
        accepted = txs.filter(lot__status=LotV2.VALIDATED, delivery_status__in=[LotTransaction.ACCEPTED, LotTransaction.FROZEN]).count()
        data['lots'] = {'draft': draft, 'validated': validated, 'tofix': tofix, 'accepted': accepted}
    elif entity.entity_type == Entity.OPERATOR:
        txs = LotTransaction.objects.filter(Q(carbure_client=entity) | Q(lot__added_by=entity, is_mac=True) | Q(carbure_vendor=entity))
        data['years'] = [t.year for t in txs.dates('delivery_date', 'year', order='DESC')]
        txs = txs.filter(lot__year=year)
        draft = txs.filter(lot__added_by=entity, lot__status=LotV2.DRAFT).count()
        ins = txs.filter(lot__status=LotV2.VALIDATED, delivery_status__in=[LotTransaction.PENDING, LotTransaction.FIXED], is_mac=False).count()
        tofix = txs.filter(lot__status=LotV2.VALIDATED, delivery_status__in=[LotTransaction.TOFIX, LotTransaction.REJECTED]).count()
        accepted = txs.filter(lot__status=LotV2.VALIDATED, delivery_status__in=[LotTransaction.ACCEPTED, LotTransaction.FROZEN]).count()
        data['lots'] = {'draft': draft, 'accepted': accepted, 'in': ins, 'tofix': tofix}
    else:
        return JsonResponse({'status': 'error', 'message': "Unknown entity_type"}, status=400)

    base_filters = [
        'periods',
        'biocarburants',
        'matieres_premieres',
        'countries_of_origin',
        'production_sites',
        'delivery_sites',
    ]
    if entity.entity_type == Entity.OPERATOR:
        data['filters'] = base_filters + ['vendors']
    else:
        data['filters'] = base_filters + ['clients']
    depots = [d.natural_key() for d in EntityDepot.objects.filter(entity=entity)]
    data['depots'] = depots
    return JsonResponse({'status': 'success', 'data': data})


@check_rights('entity_id')
def get_filters(request, *args, **kwargs):
    context = kwargs['context']
    entity = context['entity']
    status = request.GET.get('status', False)
    field = request.GET.get('field', False)
    if not field:
        return JsonResponse({'status': 'error', 'message': 'Please specify the field for which you want the filters'}, status=400)
    if entity.entity_type == Entity.PRODUCER or entity.entity_type == Entity.TRADER:
        txs = LotTransaction.objects.filter(carbure_vendor=entity)
    elif entity.entity_type == Entity.OPERATOR:
        txs = LotTransaction.objects.filter(Q(carbure_client=entity) | Q(lot__added_by=entity, is_mac=True))
    else:
        return JsonResponse({'status': 'error', 'message': "Unknown entity_type"}, status=400)
    txs = get_entity_lots_by_status(entity, status)
    txs = filter_lots(txs, request.GET, [field])[0]
    d = get_snapshot_filters(txs, entity, [field])
    if field in d:
        values = d[field]
    else:
        return JsonResponse({'status': 'error', 'message': "Something went wrong"}, status=400)
    return JsonResponse({'status': 'success', 'data': values})


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

    remaining = txs.filter(Q(carbure_client=entity) | Q(carbure_vendor=entity)).exclude(delivery_status__in=[LotTransaction.ACCEPTED, LotTransaction.FROZEN]).count()

    # get associated declaration
    declaration, created = SustainabilityDeclaration.objects.get_or_create(entity=entity, period=period_date)
    data['declaration'] = declaration.natural_key()
    data['remaining'] = remaining
    return JsonResponse({'status': 'success', 'data': data})


@check_rights('entity_id', role=[UserRights.ADMIN, UserRights.RW])
def add_lot(request, *args, **kwargs):
    context = kwargs['context']
    entity = context['entity']

    # prefetch some data
    d = get_prefetched_data(entity)
    lot, tx, errors = load_lot(d, entity, request.user, request.POST.dict(), 'MANUAL')
    if not tx:
        return JsonResponse({'status': 'error', 'message': 'Could not add lot to database'}, status=400)
    new_lots, new_txs = bulk_insert(entity, [lot], [tx], [errors], d)
    if len(new_txs) == 0:
        print(request.POST)
        return JsonResponse({'status': 'error', 'message': 'Something went wrong'}, status=500)
    lot_data = new_txs[0].natural_key()
    return JsonResponse({'status': 'success', 'data': lot_data})


@check_rights('entity_id', role=[UserRights.ADMIN, UserRights.RW])
def update_lot(request, *args, **kwargs):
    context = kwargs['context']
    entity = context['entity']

    tx_id = request.POST.get('tx_id', False)
    if not tx_id:
        return JsonResponse({'status': 'forbidden', 'message': "Missing tx_id"}, status=400)

    try:
        tx = LotTransaction.objects.get(id=tx_id)
        before_update = tx.natural_key()
    except Exception:
        return JsonResponse({'status': 'error', 'message': "Unknown transaction %s" % (tx_id)}, status=400)

    # am I allowed to update lot?
    # you can update data if you are data_origin_entity or carbure_vendor
    if entity != tx.carbure_vendor and entity != tx.lot.data_origin_entity:
        return JsonResponse({'status': 'forbidden', 'message': "Not allowed. You are not the lot creator nor intermediary"}, status=403)

    if tx.lot.status == LotV2.VALIDATED and tx.delivery_status not in (LotTransaction.TOFIX, LotTransaction.REJECTED):
        return JsonResponse({'status': 'forbidden', 'message': "Cannot update lot - please request a correction first"}, status=400)

    if tx.delivery_status == LotTransaction.FROZEN:
        return JsonResponse({'status': 'forbidden', 'message': "Tx already declared - please amend the declaration to unlock this line"}, status=400)

    GenericError.objects.filter(tx=tx).delete()
    d = get_prefetched_data(entity)
    lot, tx, errors = load_lot(d, entity, request.user, request.POST.dict(), 'MANUAL', tx)

    if not lot:
        return JsonResponse({'status': 'error', 'message': 'Could not save lot: %s' % (errors)}, status=400)

    lot.save()
    tx.save()
    GenericError.objects.bulk_create(errors)
    bulk_sanity_checks([tx], d, background=False)

    if lot.status != LotV2.DRAFT:
        # make sure we do not create a duplicate
        # only if lot is already validated ?
        check_duplicates([tx], background=False)

        # save the changes
        after_update = tx.natural_key()

        for key in before_update.keys():
            if before_update[key] is None and isinstance(after_update[key], dict):
                before_update[key] = {}
            if after_update[key] is None and isinstance(before_update[key], dict):
                after_update[key] = {}

        diff = dictdiffer.diff(before_update, after_update)

        with transaction.atomic():
            for d in diff:
                action, field, data = d
                if action == 'change':
                    if isinstance(data, tuple):
                        TransactionUpdateHistory.objects.create(tx=tx, update_type=TransactionUpdateHistory.UPDATE, field=field, value_before=data[0], value_after=data[1], modified_by=request.user, modified_by_entity=entity)
                    else:
                        print('change not tuple %s' % (d))
                if action == 'add':
                    if isinstance(data, list):
                        for (subfield, value) in data:
                            if field != '':
                                full_field_name = '%s.%s' % (field, subfield)
                            else:
                                full_field_name = subfield
                            TransactionUpdateHistory.objects.create(tx=tx, update_type=TransactionUpdateHistory.ADD, field=full_field_name, value_before='', value_after=value, modified_by=request.user, modified_by_entity=entity)
                    else:
                        print('add not list %s' % (d))
                if action == 'remove':
                    if isinstance(data, list):
                        for (subfield, value) in data:
                            if field != '':
                                full_field_name = '%s.%s' % (field, subfield)
                            else:
                                full_field_name = subfield
                            TransactionUpdateHistory.objects.create(tx=tx, update_type=TransactionUpdateHistory.REMOVE, field=full_field_name, value_before=value, value_after='', modified_by=request.user, modified_by_entity=entity)
                    else:
                        print('remove not list %s' % (d))
    return JsonResponse({'status': 'success'})

@check_rights('entity_id', role=[UserRights.ADMIN, UserRights.RW])
def duplicate_lot(request, *args, **kwargs):
    context = kwargs['context']
    entity = context['entity']

    tx_id = request.POST.get('tx_id', None)

    try:
        tx = LotTransaction.objects.get(id=tx_id)
    except Exception:
        return JsonResponse({'status': 'error', 'message': "Unknown Transaction %s" % (tx_id)}, status=400)

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
    tx.is_forwarded = False
    for f in tx_fields_to_remove:
        if f in tx_meta_fields:
            meta_field = tx_meta_fields[f]
            if meta_field.default != NOT_PROVIDED:
                setattr(tx, f, meta_field.default)
            else:
                setattr(tx, f, '')
    tx.save()
    return JsonResponse({'status': 'success'})

@check_rights('entity_id', role=[UserRights.ADMIN, UserRights.RW])
def delete_lot(request, *args, **kwargs):
    context = kwargs['context']
    entity = context['entity']

    tx_ids = request.POST.getlist('tx_ids', False)

    if not tx_ids:
        return JsonResponse({'status': 'forbidden', 'message': "Missing tx_ids"}, status=403)

    deleted = 0
    for tx_id in tx_ids:
        try:
            tx = LotTransaction.objects.get(id=tx_id)
        except Exception:
            return JsonResponse({'status': 'error', 'message': "Unknown Transaction %s" % (tx_id)}, status=400)

        rights = [r.entity for r in UserRights.objects.filter(user=request.user)]
        if tx.lot.added_by not in rights:
            return JsonResponse({'status': 'forbidden', 'message': "User not allowed to delete this tx"}, status=403)

        # only allow to delete pending or rejected transactions
        if tx.delivery_status not in ['N', 'R']:
            return JsonResponse({'status': 'forbidden', 'message': "Transaction already accepted by client"},
                                status=403)

        if tx.delivery_status == LotTransaction.REJECTED and tx.lot.parent_lot != None:
            # credit volume back to stock
            tx.lot.parent_lot.remaining_volume += tx.lot.volume
            tx.lot.parent_lot.save()
        tx.lot.delete()
        deleted += 1
    return JsonResponse({'status': 'success', 'deleted': deleted})


@check_rights('entity_id', role=[UserRights.ADMIN, UserRights.RW])
def validate_lot(request, *args, **kwargs):
    context = kwargs['context']
    entity = context['entity']
    tx_ids = request.POST.getlist('tx_ids', None)
    if not tx_ids:
        return JsonResponse({'status': 'forbidden', 'message': "Missing tx_ids"}, status=403)
    txs = LotTransaction.objects.filter(Q(id__in=tx_ids) & (Q(lot__added_by=entity) | Q(carbure_vendor=entity)))
    if txs.count() != len(tx_ids):
        return JsonResponse({'status': 'forbidden', 'message': "Some transactions do not belong to you"}, status=403)
    data = validate_lots(request.user, entity, txs)
    nb_duplicates = check_duplicates(txs, background=False)
    data['duplicates'] = nb_duplicates
    return JsonResponse({'status': 'success', 'data': data})


@check_rights('entity_id', role=[UserRights.RW, UserRights.ADMIN])
def accept_lot(request, *args, **kwargs):
    context = kwargs['context']
    entity = context['entity']
    tx_ids = request.POST.getlist('tx_ids', None)
    if not tx_ids:
        return JsonResponse({'status': 'forbidden', 'message': "Missing tx_ids"}, status=403)
    for tx_id in tx_ids:
        try:
            tx = LotTransaction.objects.get(delivery_status__in=[LotTransaction.PENDING, LotTransaction.TOFIX, LotTransaction.FIXED], id=tx_id)
        except Exception:
            return JsonResponse({'status': 'error', 'message': "TX not found"}, status=400)
        if tx.carbure_client != entity:
            return JsonResponse({'status': 'forbidden', 'message': "User not allowed"}, status=403)
        TransactionUpdateHistory.objects.create(tx=tx, update_type=TransactionUpdateHistory.UPDATE, field='status', value_before=tx.delivery_status, value_after=LotTransaction.ACCEPTED, modified_by=request.user, modified_by_entity=entity)
        tx.delivery_status = LotTransaction.ACCEPTED
        tx.save()
    return JsonResponse({'status': 'success'})



@check_rights('entity_id', role=[UserRights.RW, UserRights.ADMIN])
def accept_with_reserves(request, *args, **kwargs):
    # I want my supplier to fix something
    context = kwargs['context']
    entity = context['entity']
    tx_ids = request.POST.getlist('tx_ids', None)
    if not tx_ids:
        return JsonResponse({'status': 'forbidden', 'message': "Missing tx_ids"}, status=403)
    for tx_id in tx_ids:
        try:
            tx = LotTransaction.objects.get(id=tx_id)
        except Exception:
            return JsonResponse({'status': 'error', 'message': "TX not found"}, status=400)

        if not tx.carbure_client == entity:
            return JsonResponse({'status': 'forbidden', 'message': "User not allowed"}, status=403)

        if tx.delivery_status == LotTransaction.FROZEN:
            #
            # send email
            # invalidate declaration for both
            if tx.carbure_client:
                notify_declaration_invalidated(tx, tx.carbure_client)
            if tx.carbure_vendor:
                notify_declaration_invalidated(tx, tx.carbure_vendor)
        TransactionUpdateHistory.objects.create(tx=tx, update_type=TransactionUpdateHistory.UPDATE, field='status', value_before=tx.delivery_status, value_after=LotTransaction.TOFIX, modified_by=request.user, modified_by_entity=entity)
        tx.delivery_status = LotTransaction.TOFIX
        tx.save()
    return JsonResponse({'status': 'success'})


@check_rights('entity_id', role=[UserRights.RW, UserRights.ADMIN])
def amend_lot(request, *args, **kwargs):
    # I want to fix one of my own transaction
    # This only changes the status to TOFIX
    context = kwargs['context']
    entity = context['entity']
    tx_id = request.POST.get('tx_id', None)
    if not tx_id:
        return JsonResponse({'status': 'error', 'message': "Missing tx_id"}, status=400)
    try:
        tx = LotTransaction.objects.get(id=tx_id)
    except Exception:
        return JsonResponse({'status': 'error', 'message': "TX not found"}, status=400)

    if tx.carbure_vendor != entity and tx.lot.added_by != entity:
        print(tx.carbure_vendor)
        print(entity)
        return JsonResponse({'status': 'forbidden', 'message': "User not allowed"}, status=403)

    if tx.delivery_status in [LotTransaction.ACCEPTED, LotTransaction.FROZEN]:
        # create notification / alert
        notify_accepted_lot_in_correction(tx)
    if tx.delivery_status == LotTransaction.FROZEN:
        # get period declaration and invalidate it
        notify_declaration_invalidated(tx, entity)
    TransactionUpdateHistory.objects.create(tx=tx, update_type=TransactionUpdateHistory.UPDATE, field='status', value_before=tx.delivery_status, value_after=LotTransaction.TOFIX, modified_by=request.user, modified_by_entity=entity)
    tx.delivery_status = LotTransaction.TOFIX
    tx.save()
    return JsonResponse({'status': 'success'})

@check_rights('entity_id', role=[UserRights.RW, UserRights.ADMIN])
def reject_lot(request, *args, **kwargs):
    context = kwargs['context']
    entity = context['entity']
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
        except Exception:
            return JsonResponse({'status': 'error', 'message': "TX not found"}, status=400)


        if tx.carbure_client != entity:
            return JsonResponse({'status': 'forbidden', 'message': "User not allowed"}, status=403)
        TransactionUpdateHistory.objects.create(tx=tx, update_type=TransactionUpdateHistory.UPDATE, field='status', value_before=tx.delivery_status, value_after=LotTransaction.REJECTED, modified_by=request.user, modified_by_entity=entity)
        tx.delivery_status = LotTransaction.REJECTED
        tx.save()
        txerr = TransactionComment()
        txerr.entity = tx.carbure_client
        txerr.tx = tx
        txerr.comment = tx_comment
        txerr.save()

        # special case 1
        # if the rejected transaction came from stocks, move this transaction back to drafts
        # and recredit the parent lot with the corresponding volume
        if tx.lot.parent_lot is not None:
            tx.delivery_status = LotTransaction.PENDING
            tx.lot.status = LotV2.DRAFT
            tx.lot.parent_lot.remaining_volume += tx.lot.volume
            tx.lot.parent_lot.save()
            tx.lot.save()
            tx.save()

        tx.comment = tx_comment
        tx_rejected.append(tx)

    notify_lots_rejected(tx_rejected)
    return JsonResponse({'status': 'success'})

@check_rights('entity_id', role=[UserRights.RW, UserRights.ADMIN])
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
    except Exception:
        return JsonResponse({'status': 'error', 'message': "TX not found"}, status=400)

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
    except Exception:
        return JsonResponse({'status': "error", 'message': "Error creating template file"}, status=500)


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
    except Exception:
        return JsonResponse({'status': "error", 'message': "Error creating template file"}, status=500)


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
    except Exception:
        return JsonResponse({'status': "error", 'message': "Error creating template file"}, status=500)


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
    except Exception:
        return JsonResponse({'status': "error", 'message': "Error creating template file"}, status=500)

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
    except Exception:
        return JsonResponse({'status': "error", 'message': "Error creating template file"}, status=500)

@check_rights('entity_id', role=[UserRights.RW, UserRights.ADMIN])
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
    data = {'loaded': nb_loaded, 'total': nb_total, 'errors': [e.natural_key() if isinstance(e, GenericError) else e for e in errors]}
    return JsonResponse({'status': 'success', 'data': data})

@check_rights('entity_id', role=[UserRights.RW, UserRights.ADMIN])
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

@check_rights('entity_id', role=[UserRights.RW, UserRights.ADMIN])
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
        # check if we have pending transactions (received or sent)
        txs = LotTransaction.objects.filter(lot__period=period.strftime('%Y-%m')).filter(Q(carbure_client=entity) | Q(carbure_vendor=entity)).exclude(delivery_status__in=[LotTransaction.ACCEPTED, LotTransaction.FROZEN]).exclude(lot__status=LotV2.DRAFT)
        if txs.count() > 0:
            return JsonResponse({'status': "error", 'message': "PENDING_TRANSACTIONS_CANNOT_DECLARE", 'data': {'pending_txs': txs.count(), 'ids': [t.id for t in txs]}}, status=400)
        declaration, created = SustainabilityDeclaration.objects.update_or_create(entity=entity, period=period, defaults={'declared': True})
        # freeze transactions
        LotTransaction.objects.filter(lot__period=period.strftime('%Y-%m')).filter(Q(carbure_client=entity) | Q(carbure_vendor=entity)).exclude(delivery_status__in=[LotTransaction.FROZEN]).exclude(lot__status=LotV2.DRAFT).update(delivery_status=LotTransaction.FROZEN)
    except Exception:
        traceback.print_exc()
        return JsonResponse({'status': "error", 'message': "server error"}, status=500)
    return JsonResponse({'status': 'success'})


@check_rights('entity_id', role=[UserRights.RW, UserRights.ADMIN])
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
        except Exception:
            return JsonResponse({'status': 'error', 'message': "TX not found"}, status=400)

        if tx.carbure_delivery_site in depots:
            # it has been delivered to a Depot with outsourced blending
            # we should forward the lot to the blender
            parent_tx_id = tx.id
            tx.delivery_status = 'A'
            tx.is_forwarded = True
            tx.save()
            new_tx = tx
            new_tx.pk = None
            new_tx.parent_tx_id = parent_tx_id
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