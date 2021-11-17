import calendar
import datetime
import traceback
from unicodedata import category

from django.http.response import JsonResponse
from core.decorators import check_user_rights
from api.v4.helpers import get_entity_lots_by_status, get_lot_comments, get_lot_errors, get_lot_updates, get_lots_with_metadata, get_lots_filters_data, get_entity_stock, get_stock_with_metadata, get_stock_filters_data, get_transaction_distance, get_errors
from core.models import CarbureLot, CarbureLotComment, CarbureLotEvent, CarbureNotification, CarbureStock, Entity
from core.serializers import CarbureLotPublicSerializer


@check_user_rights()
def get_snapshot(request, *args, **kwargs):
    context = kwargs['context']
    entity_id = context['entity_id']
    year = request.GET.get('year', False)
    if year:
        try:
            year = int(year)
        except Exception:
            return JsonResponse({'status': 'error', 'message': 'Incorrect format for year. Expected YYYY'}, status=400)
    else:
        return JsonResponse({'status': 'error', 'message': 'Missing year'}, status=400)

    lots = CarbureLot.objects.filter(year=year)
    data = {}
    drafts = lots.filter(added_by_id=entity_id, lot_status=CarbureLot.DRAFT)
    lots_in = lots.filter(carbure_client_id=entity_id)
    lots_in_pending = lots_in.filter(lot_status=CarbureLot.PENDING)
    lots_in_tofix = lots_in.exclude(correction_status=CarbureLot.NO_PROBLEMO)
    stock = CarbureStock.objects.filter(carbure_client_id=entity_id)
    stock_not_empty = stock.filter(remaining_volume__gt=0)
    lots_out = lots.filter(carbure_supplier_id=entity_id)
    lots_out_pending = lots_out.filter(lot_status=CarbureLot.PENDING)
    lots_out_tofix = lots_out.exclude(correction_status=CarbureLot.NO_PROBLEMO)
    data['lots'] = {'draft': drafts.count(),
                    'in_total': lots_in.count(), 'in_pending': lots_in_pending.count(), 'in_tofix': lots_in_tofix.count(),
                    'stock': stock_not_empty.count(), 'stock_total': stock.count(),
                    'out_total': lots_out.count(), 'out_pending': lots_out_pending.count(), 'out_tofix': lots_out_tofix.count()}
    return JsonResponse({'status': 'success', 'data': data})


@check_user_rights()
def get_lots(request, *args, **kwargs):
    context = kwargs['context']
    entity_id = context['entity_id']
    status = request.GET.get('status', False)
    if not status:
        return JsonResponse({'status': 'error', 'message': 'Missing status'}, status=400)
    try:
        lots = get_entity_lots_by_status(entity_id, status)
        return get_lots_with_metadata(lots, entity_id, request.GET)
    except Exception:
        traceback.print_exc()
        return JsonResponse({'status': 'error', 'message': "Could not get lots"}, status=400)


@check_user_rights()
def get_stock(request, *args, **kwargs):
    context = kwargs['context']
    entity_id = context['entity_id']
    try:
        stock = get_entity_stock(entity_id)
        return get_stock_with_metadata(stock, entity_id, request.GET)
    except Exception:
        traceback.print_exc()
        return JsonResponse({'status': 'error', 'message': "Could not get stock"}, status=400)

@check_user_rights()
def get_lot_details(request, *args, **kwargs):
    context = kwargs['context']
    entity_id = context['entity_id']
    lot_id = request.GET.get('lot_id', False)
    if not lot_id:
        return JsonResponse({'status': 'error', 'message': 'Missing lot_id'}, status=400)

    lot = CarbureLot.objects.get(pk=lot_id)
    if str(lot.carbure_client_id) != entity_id and str(lot.carbure_supplier_id) != entity_id:
        return JsonResponse({'status': 'forbidden', 'message': "User not allowed"}, status=403)

    now = datetime.datetime.now()
    (_, last_day) = calendar.monthrange(now.year, now.month)
    deadline_date = now.replace(day=last_day)

    data = {}
    data['lot'] = CarbureLotPublicSerializer(lot).data
    data['children'] = CarbureLotPublicSerializer(CarbureLot.objects.filter(parent_lot=lot), many=True).data
    data['distance'] = get_transaction_distance(lot)
    data['errors'] = get_lot_errors(lot, entity_id)
    data['deadline'] = deadline_date.strftime("%Y-%m-%d")
    #data['certificates'] = check_certificates(tx)
    data['updates'] = get_lot_updates(lot, entity_id)
    data['comments'] = get_lot_comments(lot, entity_id)
    return JsonResponse({'status': 'success', 'data': data})


@check_user_rights()
def get_lots_filters(request, *args, **kwargs):
    context = kwargs['context']
    entity_id = context['entity_id']
    status = request.GET.get('status', False)
    field = request.GET.get('field', False)
    if not field:
        return JsonResponse({'status': 'error', 'message': 'Please specify the field for which you want the filters'}, status=400)
    txs = get_entity_lots_by_status(entity_id, status)
    data = get_lots_filters_data(txs, request.GET, entity_id, field)
    if data is None:
        return JsonResponse({'status': 'error', 'message': "Could not find specified filter"}, status=400)
    else:
        return JsonResponse({'status': 'success', 'data': data})


@check_user_rights()
def get_stock_filters(request, *args, **kwargs):
    context = kwargs['context']
    entity_id = context['entity_id']
    field = request.GET.get('field', False)
    if not field:
        return JsonResponse({'status': 'error', 'message': 'Please specify the field for which you want the filters'}, status=400)
    txs = get_entity_stock(entity_id)
    data = get_stock_filters_data(txs, request.GET, entity_id, field)
    if data is None:
        return JsonResponse({'status': 'error', 'message': "Could not find specified filter"}, status=400)
    else:
        return JsonResponse({'status': 'success', 'data': data})


@check_user_rights()
def add_comment(request, *args, **kwargs):
    context = kwargs['context']
    entity_id = context['entity_id']
    lot_ids = request.POST.getlist('lot_ids', False)
    if not lot_ids:
        return JsonResponse({'status': 'error', 'message': 'Missing lot_ids'}, status=400)
    comment = request.POST.get('comment', False)
    if not comment:
        return JsonResponse({'status': 'error', 'message': 'Missing comment'}, status=400)
    is_visible_by_admin = request.POST.get('is_visible_by_admin', False)
    is_visible_by_auditor = request.POST.get('is_visible_by_auditor', False)


    entity = Entity.objects.get(pk=entity_id)
    for lot_id in lot_ids:
        try:
            lot = CarbureLot.objects.get(pk=lot_id)
        except:
            return JsonResponse({'status': 'error', 'message': 'Could not find lot id %d' % (lot_id)}, status=400)

        if lot.carbure_supplier != entity and lot.carbure_client != entity and entity.entity_type not in [Entity.AUDITOR, Entity.ADMIN]:
            return JsonResponse({'status': 'forbidden', 'message': 'Entity not authorized to comment on this lot'}, status=403)

        comment = CarbureLotComment()
        comment.entity = entity
        comment.user = request.user
        if entity.entity_type == Entity.AUDITOR:
            comment.comment_type = CarbureLotComment.AUDITOR
            if is_visible_by_admin == 'true':
                comment.is_visible_by_admin = True
        elif entity.entity_type == Entity.ADMIN:
            comment.comment_type = CarbureLotComment.ADMIN
            if is_visible_by_auditor == 'true':
                comment.is_visible_by_auditor = True
        else:
            comment.comment_type = CarbureLotComment.REGULAR
        comment.comment = comment
        comment.save()
    return JsonResponse({'status': 'success'})


@check_user_rights()
def request_fix(request, *args, **kwargs):
    context = kwargs['context']
    entity_id = context['entity_id']
    lot_ids = request.POST.getlist('lot_ids', False)
    if not lot_ids:
        return JsonResponse({'status': 'error', 'message': 'Missing lot_ids'}, status=400)

    entity = Entity.objects.get(pk=entity_id)
    for lot_id in lot_ids:
        try:
            lot = CarbureLot.objects.get(pk=lot_id)
        except:
            return JsonResponse({'status': 'error', 'message': 'Could not find lot id %d' % (lot_id)}, status=400)

        if lot.carbure_client != entity:
            return JsonResponse({'status': 'forbidden', 'message': 'Entity not authorized to change this lot'}, status=403)
        lot.correction_status = CarbureLot.IN_CORRECTION
        lot.save()
        event = CarbureLotEvent()
        event.event_type = CarbureLotEvent.FIX_REQUESTED
        event.lot = lot
        event.user = request.user
        event.save()
    return JsonResponse({'status': 'success'})

@check_user_rights()
def mark_as_fixed(request, *args, **kwargs):
    context = kwargs['context']
    entity_id = context['entity_id']
    lot_ids = request.POST.getlist('lot_ids', False)
    if not lot_ids:
        return JsonResponse({'status': 'error', 'message': 'Missing lot_ids'}, status=400)

    entity = Entity.objects.get(pk=entity_id)
    for lot_id in lot_ids:
        try:
            lot = CarbureLot.objects.get(pk=lot_id)
        except:
            return JsonResponse({'status': 'error', 'message': 'Could not find lot id %d' % (lot_id)}, status=400)

        if lot.carbure_supplier != entity and lot.carbure_client != entity:
            return JsonResponse({'status': 'forbidden', 'message': 'Entity not authorized to change this lot'}, status=403)
        lot.correction_status = CarbureLot.FIXED
        lot.save()
        event = CarbureLotEvent()
        event.event_type = CarbureLotEvent.MARKED_AS_FIXED
        event.lot = lot
        event.user = request.user
        event.save()        
    return JsonResponse({'status': 'success'})

@check_user_rights()
def approve_fix(request, *args, **kwargs):
    context = kwargs['context']
    entity_id = context['entity_id']
    lot_ids = request.POST.getlist('lot_ids', False)
    if not lot_ids:
        return JsonResponse({'status': 'error', 'message': 'Missing lot_ids'}, status=400)

    entity = Entity.objects.get(pk=entity_id)
    for lot_id in lot_ids:
        try:
            lot = CarbureLot.objects.get(pk=lot_id)
        except:
            return JsonResponse({'status': 'error', 'message': 'Could not find lot id %d' % (lot_id)}, status=400)

        if lot.carbure_supplier != entity and lot.carbure_client != entity:
            return JsonResponse({'status': 'forbidden', 'message': 'Entity not authorized to change this lot'}, status=403)
        lot.correction_status = CarbureLot.NO_PROBLEMO
        lot.save()
        event = CarbureLotEvent()
        event.event_type = CarbureLotEvent.FIX_ACCEPTED
        event.lot = lot
        event.user = request.user
        event.save()            
    return JsonResponse({'status': 'success'})

@check_user_rights()
def reject_lot(request, *args, **kwargs):
    context = kwargs['context']
    entity_id = context['entity_id']
    lot_ids = request.POST.getlist('lot_ids', False)
    if not lot_ids:
        return JsonResponse({'status': 'error', 'message': 'Missing lot_ids'}, status=400)

    entity = Entity.objects.get(pk=entity_id)
    for lot_id in lot_ids:
        notify_sender = False
        try:
            lot = CarbureLot.objects.get(pk=lot_id)
        except:
            return JsonResponse({'status': 'error', 'message': 'Could not find lot id %d' % (lot_id)}, status=400)
       
        if entity != lot.carbure_client:
            return JsonResponse({'status': 'forbidden', 'message': 'Only the client can reject this lot'}, status=403)

        if lot.lot_status == CarbureLot.DRAFT:
            return JsonResponse({'status': 'error', 'message': 'Cannot reject DRAFT'}, status=400)
        elif lot.lot_status == CarbureLot.PENDING:
            # ok no problem
            pass
        elif lot.lot_status == CarbureLot.REJECTED:
            return JsonResponse({'status': 'error', 'message': 'Lot is already rejected.'}, status=400)
        elif lot.lot_status == CarbureLot.ACCEPTED:
            # ok but will send a notification to the sender
            notify_sender = True
        elif lot.lot_status == CarbureLot.FROZEN:
            return JsonResponse({'status': 'error', 'message': 'Lot is Frozen. Cannot reject. Please invalidate declaration first.'}, status=400)
        elif lot.lot_status == CarbureLot.DELETED:
            return JsonResponse({'status': 'error', 'message': 'Lot is deleted. Cannot reject'}, status=400)

        lot.lot_status = CarbureLot.REJECTED
        lot.save()
        event = CarbureLotEvent()
        event.event_type = CarbureLotEvent.REJECTED
        event.lot = lot
        event.user = request.user
        event.save()
        if notify_sender:
            if event.lot.carbure_supplier and event.lot.carbure_client != event.lot.carbure_supplier:
                n = CarbureNotification()
                n.event = event
                n.recipient = event.lot.carbure_supplier
                n.save()        
    return JsonResponse({'status': 'success'})

@check_user_rights()
def recall_lot(request, *args, **kwargs):
    context = kwargs['context']
    entity_id = context['entity_id']
    lot_ids = request.POST.getlist('lot_ids', False)
    if not lot_ids:
        return JsonResponse({'status': 'error', 'message': 'Missing lot_ids'}, status=400)

    entity = Entity.objects.get(pk=entity_id)
    for lot_id in lot_ids:
        notify_client = False
        try:
            lot = CarbureLot.objects.get(pk=lot_id)
        except:
            return JsonResponse({'status': 'error', 'message': 'Could not find lot id %d' % (lot_id)}, status=400)

        if entity != lot.carbure_supplier:
            return JsonResponse({'status': 'forbidden', 'message': 'Only the vendor can recall the lot'}, status=403)

        if lot.lot_status == CarbureLot.DRAFT:
            return JsonResponse({'status': 'error', 'message': 'Cannot recall DRAFT'}, status=400)
        elif lot.lot_status == CarbureLot.PENDING:
            # ok no problem
            pass
        elif lot.lot_status == CarbureLot.REJECTED:
            return JsonResponse({'status': 'error', 'message': 'Lot is already rejected. Recall has no effect'}, status=400)
        elif lot.lot_status == CarbureLot.ACCEPTED:
            # ok but will send a notification to the client
            notify_client = True
        elif lot.lot_status == CarbureLot.FROZEN:
            return JsonResponse({'status': 'error', 'message': 'Lot is Frozen. Cannot recall. Please invalidate declaration first.'}, status=400)
        elif lot.lot_status == CarbureLot.DELETED:
            return JsonResponse({'status': 'error', 'message': 'Lot is deleted. Cannot recall'}, status=400)

        lot.lot_status = CarbureLot.DRAFT
        lot.save()
        event = CarbureLotEvent()
        event.event_type = CarbureLotEvent.RECALLED
        event.lot = lot
        event.user = request.user
        event.save()
        if notify_client:
            if event.lot.carbure_client and event.lot.carbure_client != event.lot.carbure_supplier:
                n = CarbureNotification()
                n.event = event
                n.recipient = event.lot.carbure_client
                n.save()
    return JsonResponse({'status': 'success'})



@check_user_rights()
def accept_rfc(request, *args, **kwargs):
    context = kwargs['context']
    entity_id = context['entity_id']
    lot_ids = request.POST.getlist('lot_ids', False)
    if not lot_ids:
        return JsonResponse({'status': 'error', 'message': 'Missing lot_ids'}, status=400)

    entity = Entity.objects.get(pk=entity_id)
    for lot_id in lot_ids:
        try:
            lot = CarbureLot.objects.get(pk=lot_id)
        except:
            return JsonResponse({'status': 'error', 'message': 'Could not find lot id %d' % (lot_id)}, status=400)

        if entity != lot.carbure_client:
            return JsonResponse({'status': 'forbidden', 'message': 'Only the client can accept the lot'}, status=403)

        if lot.lot_status == CarbureLot.DRAFT:
            return JsonResponse({'status': 'error', 'message': 'Cannot accept DRAFT'}, status=400)
        elif lot.lot_status == CarbureLot.PENDING:
            # ok no problem
            pass
        elif lot.lot_status == CarbureLot.REJECTED:
            # the client changed his mind, ok
            pass
        elif lot.lot_status == CarbureLot.ACCEPTED:
            return JsonResponse({'status': 'error', 'message': 'Lot already accepted.'}, status=400)
        elif lot.lot_status == CarbureLot.FROZEN:
            return JsonResponse({'status': 'error', 'message': 'Lot is Frozen.'}, status=400)
        elif lot.lot_status == CarbureLot.DELETED:
            return JsonResponse({'status': 'error', 'message': 'Lot is deleted.'}, status=400)

        lot.lot_status = CarbureLot.ACCEPTED
        lot.delivery_type = CarbureLot.RFC
        lot.save()
        event = CarbureLotEvent()
        event.event_type = CarbureLotEvent.ACCEPTED
        event.lot = lot
        event.user = request.user
        event.save()
    return JsonResponse({'status': 'success'})

@check_user_rights()
def accept_in_stock(request, *args, **kwargs):
    context = kwargs['context']
    entity_id = context['entity_id']
    lot_ids = request.POST.getlist('lot_ids', False)
    if not lot_ids:
        return JsonResponse({'status': 'error', 'message': 'Missing lot_ids'}, status=400)

    entity = Entity.objects.get(pk=entity_id)
    for lot_id in lot_ids:
        try:
            lot = CarbureLot.objects.get(pk=lot_id)
        except:
            return JsonResponse({'status': 'error', 'message': 'Could not find lot id %d' % (lot_id)}, status=400)

        if entity != lot.carbure_client:
            return JsonResponse({'status': 'forbidden', 'message': 'Only the client can accept the lot'}, status=403)

        if lot.lot_status == CarbureLot.DRAFT:
            return JsonResponse({'status': 'error', 'message': 'Cannot accept DRAFT'}, status=400)
        elif lot.lot_status == CarbureLot.PENDING:
            # ok no problem
            pass
        elif lot.lot_status == CarbureLot.REJECTED:
            # the client changed his mind, ok
            pass
        elif lot.lot_status == CarbureLot.ACCEPTED:
            return JsonResponse({'status': 'error', 'message': 'Lot already accepted.'}, status=400)
        elif lot.lot_status == CarbureLot.FROZEN:
            return JsonResponse({'status': 'error', 'message': 'Lot is Frozen.'}, status=400)
        elif lot.lot_status == CarbureLot.DELETED:
            return JsonResponse({'status': 'error', 'message': 'Lot is deleted.'}, status=400)

        lot.lot_status = CarbureLot.ACCEPTED
        lot.delivery_type = CarbureLot.STOCK
        lot.save()
        event = CarbureLotEvent()
        event.event_type = CarbureLotEvent.ACCEPTED
        event.lot = lot
        event.user = request.user
        event.save()
        stock = CarbureStock()
        stock.parent_lot = lot
        stock.carbure_id = lot.carbure_id
        if lot.carbure_delivery_site is None:
            return JsonResponse({'status': 'error', 'message': 'Cannot add stock for unknown Depot'}, status=400)
        stock.depot = lot.carbure_delivery_site
        stock.carbure_client = lot.carbure_client
        stock.remaining_volume = lot.volume
        stock.remaining_weight = lot.weight
        stock.remaining_lhv_amount = lot.lhv_amount
        stock.feedstock = lot.feedstock
        stock.biofuel = lot.biofuel
        stock.country_of_origin = lot.country_of_origin
        stock.carbure_production_site = lot.carbure_production_site
        stock.unknown_production_site = lot.unknown_production_site
        stock.production_country = lot.production_country
        stock.carbure_supplier = lot.carbure_supplier
        stock.unknown_supplier = lot.unknown_supplier
        stock.ghg_reduction = lot.ghg_reduction
        stock.ghg_reduction_red_ii = lot.ghg_reduction_red_ii
        stock.save()
    return JsonResponse({'status': 'success'})


@check_user_rights()
def accept_blending(request, *args, **kwargs):
    context = kwargs['context']
    entity_id = context['entity_id']
    lot_ids = request.POST.getlist('lot_ids', False)
    if not lot_ids:
        return JsonResponse({'status': 'error', 'message': 'Missing lot_ids'}, status=400)

    entity = Entity.objects.get(pk=entity_id)
    for lot_id in lot_ids:
        try:
            lot = CarbureLot.objects.get(pk=lot_id)
        except:
            return JsonResponse({'status': 'error', 'message': 'Could not find lot id %d' % (lot_id)}, status=400)

        if entity != lot.carbure_client:
            return JsonResponse({'status': 'forbidden', 'message': 'Only the client can accept the lot'}, status=403)

        if lot.lot_status == CarbureLot.DRAFT:
            return JsonResponse({'status': 'error', 'message': 'Cannot accept DRAFT'}, status=400)
        elif lot.lot_status == CarbureLot.PENDING:
            # ok no problem
            pass
        elif lot.lot_status == CarbureLot.REJECTED:
            # the client changed his mind, ok
            pass
        elif lot.lot_status == CarbureLot.ACCEPTED:
            return JsonResponse({'status': 'error', 'message': 'Lot already accepted.'}, status=400)
        elif lot.lot_status == CarbureLot.FROZEN:
            return JsonResponse({'status': 'error', 'message': 'Lot is Frozen.'}, status=400)
        elif lot.lot_status == CarbureLot.DELETED:
            return JsonResponse({'status': 'error', 'message': 'Lot is deleted.'}, status=400)

        lot.lot_status = CarbureLot.ACCEPTED
        lot.delivery_type = CarbureLot.BLENDING
        lot.save()
        event = CarbureLotEvent()
        event.event_type = CarbureLotEvent.ACCEPTED
        event.lot = lot
        event.user = request.user
        event.save()
    return JsonResponse({'status': 'success'})

@check_user_rights()
def accept_export(request, *args, **kwargs):
    context = kwargs['context']
    entity_id = context['entity_id']
    lot_ids = request.POST.getlist('lot_ids', False)
    if not lot_ids:
        return JsonResponse({'status': 'error', 'message': 'Missing lot_ids'}, status=400)

    entity = Entity.objects.get(pk=entity_id)
    for lot_id in lot_ids:
        try:
            lot = CarbureLot.objects.get(pk=lot_id)
        except:
            return JsonResponse({'status': 'error', 'message': 'Could not find lot id %d' % (lot_id)}, status=400)

        if entity != lot.carbure_client:
            return JsonResponse({'status': 'forbidden', 'message': 'Only the client can accept the lot'}, status=403)

        if lot.lot_status == CarbureLot.DRAFT:
            return JsonResponse({'status': 'error', 'message': 'Cannot accept DRAFT'}, status=400)
        elif lot.lot_status == CarbureLot.PENDING:
            # ok no problem
            pass
        elif lot.lot_status == CarbureLot.REJECTED:
            # the client changed his mind, ok
            pass
        elif lot.lot_status == CarbureLot.ACCEPTED:
            return JsonResponse({'status': 'error', 'message': 'Lot already accepted.'}, status=400)
        elif lot.lot_status == CarbureLot.FROZEN:
            return JsonResponse({'status': 'error', 'message': 'Lot is Frozen.'}, status=400)
        elif lot.lot_status == CarbureLot.DELETED:
            return JsonResponse({'status': 'error', 'message': 'Lot is deleted.'}, status=400)

        lot.lot_status = CarbureLot.ACCEPTED
        lot.delivery_type = CarbureLot.EXPORT
        lot.save()
        event = CarbureLotEvent()
        event.event_type = CarbureLotEvent.ACCEPTED
        event.lot = lot
        event.user = request.user
        event.save()
    return JsonResponse({'status': 'success'})

@check_user_rights()
def accept_processing(request, *args, **kwargs):
    context = kwargs['context']
    entity_id = context['entity_id']
    lot_ids = request.POST.getlist('lot_ids', False)
    processing_entity_id = request.POST.get('processing_entity_id', False)
    if not lot_ids:
        return JsonResponse({'status': 'error', 'message': 'Missing lot_ids'}, status=400)

    entity = Entity.objects.get(pk=entity_id)
    try:
        processing_entity = Entity.objects.get(pk=processing_entity_id)
    except:
        return JsonResponse({'status': 'error', 'message': 'Could not find processing entity'}, status=400)

    for lot_id in lot_ids:
        try:
            lot = CarbureLot.objects.get(pk=lot_id)
        except:
            return JsonResponse({'status': 'error', 'message': 'Could not find lot id %d' % (lot_id)}, status=400)

        if entity != lot.carbure_client:
            return JsonResponse({'status': 'forbidden', 'message': 'Only the client can accept the lot'}, status=403)

        if lot.lot_status == CarbureLot.DRAFT:
            return JsonResponse({'status': 'error', 'message': 'Cannot accept DRAFT'}, status=400)
        elif lot.lot_status == CarbureLot.PENDING:
            # ok no problem
            pass
        elif lot.lot_status == CarbureLot.REJECTED:
            # the client changed his mind, ok
            pass
        elif lot.lot_status == CarbureLot.ACCEPTED:
            return JsonResponse({'status': 'error', 'message': 'Lot already accepted.'}, status=400)
        elif lot.lot_status == CarbureLot.FROZEN:
            return JsonResponse({'status': 'error', 'message': 'Lot is Frozen.'}, status=400)
        elif lot.lot_status == CarbureLot.DELETED:
            return JsonResponse({'status': 'error', 'message': 'Lot is deleted.'}, status=400)

        lot.lot_status = CarbureLot.ACCEPTED
        lot.delivery_type = CarbureLot.PROCESSING
        lot.save()
        event = CarbureLotEvent()
        event.event_type = CarbureLotEvent.ACCEPTED
        event.lot = lot
        event.user = request.user
        event.save()

        # create child lot
        parent_lot_id = lot.id
        child_lot = lot
        child_lot.pk = None
        child_lot.carbure_client = processing_entity
        child_lot.delivery_type = CarbureLot.UNKNOWN
        child_lot.lot_status = CarbureLot.PENDING
        child_lot.correction_status = CarbureLot.NO_PROBLEMO
        child_lot.declared_by_supplier = False
        child_lot.declared_by_client = False
        child_lot.added_by = entity
        child_lot.carbure_supplier = entity
        child_lot.unknown_supplier = None
        child_lot.parent_lot_id = parent_lot_id
        child_lot.save()
        event = CarbureLotEvent()
        event.event_type = CarbureLotEvent.CREATED
        event.lot = child_lot
        event.user = request.user
        event.save()
    return JsonResponse({'status': 'success'})

@check_user_rights()
def accept_trading(request, *args, **kwargs):
    context = kwargs['context']
    entity_id = context['entity_id']
    lot_ids = request.POST.getlist('lot_ids', False)
    client_entity_id = request.POST.get('client_entity_id', False)
    unknown_client = request.POST.get('unknown_client', False)
    if not lot_ids:
        return JsonResponse({'status': 'error', 'message': 'Missing lot_ids'}, status=400)
    if not client_entity_id and not unknown_client:
        return JsonResponse({'status': 'error', 'message': 'Please specify either client_entity_id or unknown_client'}, status=400)

    entity = Entity.objects.get(pk=entity_id)
    if client_entity_id:
        try:
            client_entity = Entity.objects.get(pk=client_entity_id)
        except:
            return JsonResponse({'status': 'error', 'message': 'Could not find client entity'}, status=400)
    else:
        client_entity = None

    for lot_id in lot_ids:
        try:
            lot = CarbureLot.objects.get(pk=lot_id)
        except:
            return JsonResponse({'status': 'error', 'message': 'Could not find lot id %d' % (lot_id)}, status=400)

        if entity != lot.carbure_client:
            return JsonResponse({'status': 'forbidden', 'message': 'Only the client can accept the lot'}, status=403)

        if lot.lot_status == CarbureLot.DRAFT:
            return JsonResponse({'status': 'error', 'message': 'Cannot accept DRAFT'}, status=400)
        elif lot.lot_status == CarbureLot.PENDING:
            # ok no problem
            pass
        elif lot.lot_status == CarbureLot.REJECTED:
            # the client changed his mind, ok
            pass
        elif lot.lot_status == CarbureLot.ACCEPTED:
            return JsonResponse({'status': 'error', 'message': 'Lot already accepted.'}, status=400)
        elif lot.lot_status == CarbureLot.FROZEN:
            return JsonResponse({'status': 'error', 'message': 'Lot is Frozen.'}, status=400)
        elif lot.lot_status == CarbureLot.DELETED:
            return JsonResponse({'status': 'error', 'message': 'Lot is deleted.'}, status=400)

        lot.lot_status = CarbureLot.ACCEPTED
        lot.delivery_type = CarbureLot.TRADING
        lot.save()
        event = CarbureLotEvent()
        event.event_type = CarbureLotEvent.ACCEPTED
        event.lot = lot
        event.user = request.user
        event.save()

        # create child lot
        parent_lot_id = lot.id
        child_lot = lot
        child_lot.pk = None
        child_lot.carbure_client = client_entity
        child_lot.unknown_client = unknown_client
        child_lot.delivery_type = CarbureLot.UNKNOWN
        if child_lot.carbure_client is None:
            # auto-accept when the client is not registered in carbure
            child_lot.lot_status = CarbureLot.ACCEPTED
            child_lot.declared_by_client = True
        else:
            child_lot.declared_by_client = False
            child_lot.lot_status = CarbureLot.PENDING
        child_lot.correction_status = CarbureLot.NO_PROBLEMO
        child_lot.declared_by_supplier = False
        child_lot.added_by = entity
        child_lot.carbure_supplier = entity
        child_lot.unknown_supplier = None
        child_lot.parent_lot_id = parent_lot_id
        child_lot.save()
        event = CarbureLotEvent()
        event.event_type = CarbureLotEvent.CREATED
        event.lot = child_lot
        event.user = request.user
        event.save()
        event = CarbureLotEvent()
        event.event_type = CarbureLotEvent.ACCEPTED
        event.lot = child_lot
        event.user = request.user
        event.save()        
    return JsonResponse({'status': 'success'})