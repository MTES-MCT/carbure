from calendar import calendar, monthrange
import datetime
from json.encoder import py_encode_basestring_ascii
import unicodedata
import dictdiffer
import json
import time
import traceback
from django.db.models.aggregates import Count, Sum
from django.db.models.fields import NOT_PROVIDED

from django.http.response import HttpResponse, JsonResponse
from django.db.models.query_utils import Q
from api.v4.certificates import get_certificates
from core.common import convert_template_row_to_formdata, get_uploaded_files_directory
from core.decorators import check_user_rights
from api.v4.helpers import filter_lots, filter_stock, get_entity_lots_by_status, get_lot_comments, get_lot_errors, get_lot_updates, get_lots_summary_data, get_lots_with_metadata, get_lots_filters_data, get_entity_stock
from api.v4.helpers import get_prefetched_data, get_stock_events, get_stock_with_metadata, get_stock_filters_data, get_stocks_summary_data, get_transaction_distance, handle_eth_to_etbe_transformation, get_known_certificates
from api.v4.helpers import send_email_declaration_invalidated, send_email_declaration_validated
from api.v4.lots import construct_carbure_lot, bulk_insert_lots, try_get_date
from api.v4.sanity_checks import bulk_sanity_checks, sanity_check

from core.models import CarbureLot, CarbureLotComment, CarbureLotEvent, CarbureNotification, CarbureStock, CarbureStockEvent, CarbureStockTransformation, Depot, Entity, GenericError, Pays, SustainabilityDeclaration, UserRights
from core.notifications import notify_correction_done, notify_correction_request, notify_declaration_cancelled, notify_declaration_validated, notify_lots_recalled, notify_lots_received, notify_lots_rejected, notify_lots_recalled
from core.serializers import CarbureLotPublicSerializer, CarbureNotificationSerializer, CarbureStockPublicSerializer, CarbureStockTransformationPublicSerializer
from core.xlsx_v3 import template_v4, template_v4_stocks


@check_user_rights()
def get_years(request, *args, **kwargs):
    entity_id = int(kwargs['context']['entity_id'])
    data_lots = CarbureLot.objects.filter(Q(carbure_client_id=entity_id) | Q(carbure_supplier_id=entity_id) | Q(added_by_id=entity_id)).values_list('year', flat=True).distinct()
    data_transforms = CarbureStockTransformation.objects.filter(entity_id=entity_id).values_list('transformation_dt__year', flat=True).distinct()
    data = set(list(data_transforms) + list(data_lots))
    return JsonResponse({'status': 'success', 'data': list(data)})


@check_user_rights()
def get_notifications(request, *args, **kwargs):
    entity_id = int(kwargs['context']['entity_id'])
    notifications = CarbureNotification.objects.filter(dest_id=entity_id).order_by('-datetime')[0:15]
    data = CarbureNotificationSerializer(notifications, many=True).data
    return JsonResponse({'status': 'success', 'data': data})


@check_user_rights()
def ack_notifications(request, *args, **kwargs):
    entity_id = int(kwargs['context']['entity_id'])
    notification_ids = request.POST.getlist('notification_ids', False)
    notifications = CarbureNotification.objects.filter(dest_id=entity_id, id__in=notification_ids)
    notifications.update(acked=True)
    return JsonResponse({'status': 'success'})


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

    data = {}
    lots = CarbureLot.objects.filter(year=year)

    drafts = lots.filter(added_by_id=entity_id, lot_status=CarbureLot.DRAFT)
    drafts_imported = drafts.exclude(parent_stock__isnull=False)
    drafts_stocks = drafts.filter(parent_stock__isnull=False)

    lots_in = lots.filter(carbure_client_id=entity_id).exclude(lot_status__in=[CarbureLot.DELETED, CarbureLot.DRAFT])
    lots_in_pending = lots_in.filter(lot_status=CarbureLot.PENDING)
    lots_in_tofix = lots_in.exclude(correction_status=CarbureLot.NO_PROBLEMO)

    stock = CarbureStock.objects.filter(carbure_client_id=entity_id)
    stock_not_empty = stock.filter(remaining_volume__gt=0)

    lots_out = lots.filter(carbure_supplier_id=entity_id).exclude(lot_status__in=[CarbureLot.DELETED, CarbureLot.DRAFT])
    lots_out_pending = lots_out.filter(lot_status=CarbureLot.PENDING)
    lots_out_tofix = lots_out.exclude(correction_status=CarbureLot.NO_PROBLEMO)

    data['lots'] = {'draft': drafts.count(),
                    'in_total': lots_in.count(), 'in_pending': lots_in_pending.count(), 'in_tofix': lots_in_tofix.count(),
                    'stock': stock_not_empty.count(), 'stock_total': stock.count(),
                    'out_total': lots_out.count(), 'out_pending': lots_out_pending.count(), 'out_tofix': lots_out_tofix.count(),
                    'draft_imported': drafts_imported.count(), 'draft_stocks': drafts_stocks.count()}
    return JsonResponse({'status': 'success', 'data': data})


@check_user_rights()
def get_lots(request, *args, **kwargs):
    context = kwargs['context']
    entity_id = context['entity_id']
    status = request.GET.get('status', False)
    selection = request.GET.get('selection', False)
    export = request.GET.get('export', False)
    if not status and not selection:
        return JsonResponse({'status': 'error', 'message': 'Missing status'}, status=400)
    try:
        entity = Entity.objects.get(id=entity_id)
        lots = get_entity_lots_by_status(entity, status, export)
        return get_lots_with_metadata(lots, entity, request.GET)
    except Exception:
        traceback.print_exc()
        return JsonResponse({'status': 'error', 'message': "Could not get lots"}, status=400)


@check_user_rights()
def get_stock(request, *args, **kwargs):
    context = kwargs['context']
    entity_id = context['entity_id']
    try:
        stock = get_entity_stock(entity_id)
        return get_stock_with_metadata(stock, request.GET)
    except Exception:
        traceback.print_exc()
        return JsonResponse({'status': 'error', 'message': "Could not get stock"}, status=400)


@check_user_rights()
def get_lots_summary(request, *args, **kwargs):
    context = kwargs['context']
    entity_id = context['entity_id']
    status = request.GET.get('status', False)
    short = request.GET.get('short', False) == 'true'
    if not status:
        return JsonResponse({'status': 'error', 'message': 'Missing status'}, status=400)
    try:
        entity = Entity.objects.get(id=entity_id)
        lots = get_entity_lots_by_status(entity, status)
        lots = filter_lots(lots, request.GET, entity, will_aggregate=True)
        summary = get_lots_summary_data(lots, entity, short)
        return JsonResponse({'status': 'success', 'data': summary})
    except Exception:
        traceback.print_exc()
        return JsonResponse({'status': 'error', 'message': "Could not get lots summary"}, status=400)


@check_user_rights()
def get_stocks_summary(request, *args, **kwargs):
    context = kwargs['context']
    entity_id = context['entity_id']
    short = request.GET.get('short', False)
    try:
        stock = get_entity_stock(entity_id)
        stock = filter_stock(stock, request.GET, entity_id)
        summary = get_stocks_summary_data(stock, entity_id, short == 'true')
        return JsonResponse({'status': 'success', 'data': summary})
    except Exception:
        traceback.print_exc()
        return JsonResponse({'status': 'error', 'message': "Could not get stock summary"}, status=400)


@check_user_rights()
def get_stock_details(request, *args, **kwargs):
    context = kwargs['context']
    entity_id = context['entity_id']
    stock_id = request.GET.get('stock_id', False)
    if not stock_id:
        return JsonResponse({'status': 'error', 'message': 'Missing stock_id'}, status=400)

    stock = CarbureStock.objects.get(pk=stock_id)
    if str(stock.carbure_client_id) != entity_id:
        return JsonResponse({'status': 'forbidden', 'message': "User not allowed"}, status=403)

    data = {}
    data['stock'] = CarbureStockPublicSerializer(stock).data
    data['parent_lot'] = CarbureLotPublicSerializer(stock.parent_lot).data if stock.parent_lot else None
    data['parent_transformation'] = CarbureStockTransformationPublicSerializer(stock.parent_transformation).data if stock.parent_transformation else None
    children = CarbureLot.objects.filter(parent_stock=stock).exclude(lot_status=CarbureLot.DELETED)
    data['children_lot'] = CarbureLotPublicSerializer(children, many=True).data
    data['children_transformation'] = CarbureStockTransformationPublicSerializer(CarbureStockTransformation.objects.filter(source_stock=stock), many=True).data
    data['events'] = get_stock_events(stock.parent_lot, entity_id)
    data['updates'] = get_lot_updates(stock.parent_lot, entity_id)
    data['comments'] = get_lot_comments(stock.parent_lot, entity_id)
    return JsonResponse({'status': 'success', 'data': data})

@check_user_rights(role=[UserRights.RW, UserRights.ADMIN])
def stock_cancel_transformation(request, *args, **kwargs):
    context = kwargs['context']
    entity_id = context['entity_id']
    stock_ids = request.POST.getlist('stock_ids', False)
    if not stock_ids:
        return JsonResponse({'status': 'error', 'message': 'Missing stock_ids'}, status=400)

    try:
        stocks = CarbureStock.objects.filter(pk__in=stock_ids)
    except:
        return JsonResponse({'status': 'error', 'message': 'Could not find stock'}, status=400)

    for stock in stocks:
        if stock.carbure_client_id != int(entity_id):
            return JsonResponse({'status': 'forbidden', 'message': 'Stock does not belong to you'}, status=403)

        if stock.parent_transformation_id is None:
            return JsonResponse({'status': 'error', 'message': 'Stock does not come from a transformation'}, status=400)

        # all good
        # delete of transformation should trigger a cascading delete of child_lots + recredit volume to the parent_stock
        event = CarbureStockEvent()
        event.stock = stock.parent_transformation.source_stock
        event.event_type = CarbureStockEvent.UNTRANSFORMED
        event.user = request.user
        event.save()
        stock.parent_transformation.delete()
    return JsonResponse({'status': 'success'})

@check_user_rights(role=[UserRights.RW, UserRights.ADMIN])
def stock_flush(request, *args, **kwargs):
    context = kwargs['context']
    entity_id = int(context['entity_id'])
    stock_ids = request.POST.getlist('stock_ids')
    free_field = request.POST.get('free_field', False)
    if not stock_ids:
        return JsonResponse({'status': 'error', 'message': 'Missing stock_ids'}, status=400)

    for stock_id in stock_ids:
        try:
            stock = CarbureStock.objects.get(pk=stock_id)
        except:
            return JsonResponse({'status': 'error', 'message': 'Could not find stock'}, status=400)

        if stock.carbure_client_id != entity_id:
            return JsonResponse({'status': 'forbidden', 'message': 'Stock does not belong to you'}, status=403)

        volume_to_flush = stock.remaining_volume
        initial_volume = 0
        if stock.parent_lot:
            initial_volume = stock.parent_lot.volume
        elif stock.parent_transformation:
            initial_volume = stock.parent_transformation.volume_destination

        if volume_to_flush > initial_volume * 0.05:
            return JsonResponse({'status': 'error', 'message': 'Cannot flush a stock with a remaining volume greater than 1%'}, status=400)

        # update remaining stock
        rounded_volume = round(volume_to_flush, 2)
        if rounded_volume >= stock.remaining_volume:
            stock.remaining_volume = 0
            stock.remaining_weight = 0
            stock.remaining_lhv_amount = 0
        else:
            stock.remaining_volume = round(stock.remaining_volume - rounded_volume, 2)
            stock.remaining_weight = stock.get_weight()
            stock.remaining_lhv_amount = stock.get_lhv_amount()
        stock.save()
        # create flushed lot
        lot = stock.get_parent_lot()
        lot.pk = None
        lot.transport_document_type = CarbureLot.OTHER
        lot.transport_document_reference = 'N/A - FLUSH'
        lot.volume = rounded_volume
        lot.weight = lot.get_weight()
        lot.lhv_amount = lot.get_lhv_amount()
        lot.lot_status = CarbureLot.ACCEPTED
        lot.delivery_type = CarbureLot.FLUSHED
        lot.unknown_client = None
        lot.carbure_delivery_site = None
        lot.unknown_delivery_site = None
        lot.delivery_site_country = None
        lot.parent_stock = stock
        if free_field:
            lot.free_field = free_field
        else:
            lot.free_field = 'FLUSHED'
        lot.save()
        # create events
        e = CarbureStockEvent()
        e.event_type = CarbureStockEvent.FLUSHED
        e.user = request.user
        e.stock = stock
        e.save()
        e = CarbureLotEvent()
        e.event_type = CarbureLotEvent.CREATED
        e.lot = lot
        e.user = request.user
        e.save()
        e.pk = None
        e.event_type = CarbureLotEvent.ACCEPTED
        e.save()
    return JsonResponse({'status': 'success'})

@check_user_rights(role=[UserRights.RW, UserRights.ADMIN])
def stock_split(request, *args, **kwargs):
    context = kwargs['context']
    entity_id = context['entity_id']
    payload = request.POST.get('payload', False)
    if not payload:
        return JsonResponse({'status': 'error', 'message': 'Missing payload'}, status=400)
    entity = Entity.objects.get(id=entity_id)
    prefetched_data = get_prefetched_data(entity)

    try:
        unserialized = json.loads(payload)
        # expected format: [{stock_id: "L20140-4243-XXX", volume: 3244.33, transport_document_type: 'DAE', transport_document_reference: 'FR221244342WW'
        # dispatch_date: '2021-05-11', carbure_delivery_site_id: None, unknown_delivery_site: "SomeUnknownDepot", delivery_site_country_id: 120,
        # delivery_type: 'EXPORT', carbure_client_id: 12, unknown_client: None}]
    except:
        return JsonResponse({'status': 'error', 'message': 'Cannot parse payload into JSON'}, status=400)

    if not isinstance(unserialized, list):
        return JsonResponse({'status': 'error', 'message': 'Parsed JSON is not a list'}, status=400)

    new_lot_ids = []
    for entry in unserialized:
        # check minimum fields
        required_fields = ['stock_id', 'volume', 'delivery_date']
        for field in required_fields:
            if field not in entry:
                return JsonResponse({'status': 'error', 'message': 'Missing field %s in json object' % (field)}, status=400)

        try:
            stock = CarbureStock.objects.get(carbure_id=entry['stock_id'])
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': 'Could not find stock'}, status=400)

        if stock.carbure_client_id != int(entity_id):
            return JsonResponse({'status': 'forbidden', 'message': 'Stock does not belong to you'}, status=403)

        try:
            volume = float(entry['volume'])
        except:
            return JsonResponse({'status': 'error', 'message': 'Could not parse volume'}, status=400)

        # create child lot
        rounded_volume = round(volume, 2)
        lot = stock.get_parent_lot()
        lot.pk = None
        lot.transport_document_reference = None
        lot.carbure_client = None
        lot.unknown_client = None
        lot.carbure_delivery_site = None
        lot.unknown_delivery_site = None
        lot.delivery_site_country = None
        lot.lot_status = CarbureLot.DRAFT
        lot.delivery_type = CarbureLot.UNKNOWN
        lot.volume = rounded_volume
        lot.biofuel = stock.biofuel
        lot.weight = lot.get_weight()
        lot.lhv_amount = lot.get_lhv_amount()
        lot.parent_stock = stock
        lot.parent_lot = None
        # common, mandatory data
        lot.delivery_date = try_get_date(entry['delivery_date'])
        lot.year = lot.delivery_date.year
        lot.period = lot.delivery_date.year * 100 + lot.delivery_date.month
        lot.carbure_dispatch_site = stock.depot
        lot.dispatch_site_country = lot.carbure_dispatch_site.country if lot.carbure_dispatch_site else None
        lot.carbure_supplier_id = entity_id
        lot.added_by_id = entity_id
        lot.dispatch_date = entry.get('dispatch_date', None)
        lot.unknown_client = entry.get('unknown_client', None)
        lot.unknown_delivery_site = entry.get('unknown_delivery_site', None)
        country_code = entry.get('delivery_site_country_id', None)
        if country_code is not None:
            try:
                lot.delivery_site_country = Pays.objects.get(code_pays=country_code)
            except:
                lot.delivery_site_country = None
        lot.transport_document_type = entry.get('transport_document_type', CarbureLot.OTHER)
        lot.delivery_type = entry.get('delivery_type', CarbureLot.UNKNOWN)
        lot.transport_document_reference = entry.get('transport_document_reference', lot.delivery_type)
        delivery_site_id = entry.get('carbure_delivery_site_id', None)
        try:
            delivery_site = Depot.objects.get(depot_id=delivery_site_id)
            lot.carbure_delivery_site = delivery_site
            lot.delivery_site_country = delivery_site.country
        except:
            pass
        try:
            lot.carbure_client = Entity.objects.get(id=entry.get('carbure_client_id', None))
        except:
            lot.carbure_client = None
        if lot.delivery_type in [CarbureLot.BLENDING, CarbureLot.DIRECT, CarbureLot.PROCESSING]:
            if lot.transport_document_reference is None:
                return JsonResponse({'status': 'error', 'message': 'Missing transport_document_reference'}, status=400)
            if lot.carbure_client is None:
                return JsonResponse({'status': 'error', 'message': 'Mandatory carbure_client_id'}, status=400)
            if lot.carbure_delivery_site is None:
                return JsonResponse({'status': 'error', 'message': 'Mandatory carbure_delivery_site'}, status=400)
        else:
            if lot.delivery_site_country is None:
                return JsonResponse({'status': 'error', 'message': 'Mandatory delivery_site_country'}, status=400)

        # check if the stock has enough volume and update it
        if rounded_volume > stock.remaining_volume:
            return JsonResponse({'status': 'error', 'message': 'Not enough stock available Available [%.2f] Requested [%.2f]' % (stock.remaining_volume, rounded_volume)}, status=400)

        lot.save()
        stock.remaining_volume = round(stock.remaining_volume - rounded_volume, 2)
        stock.remaining_weight = stock.get_weight()
        stock.remaining_lhv_amount = stock.get_lhv_amount()
        stock.save()
        event = CarbureStockEvent()
        event.event_type = CarbureStockEvent.SPLIT
        event.stock = stock
        event.user = request.user
        event.metadata = {'message': 'Envoi lot.', 'volume_to_deduct': lot.volume}
        event.save()
        new_lot_ids.append(lot.id)
        bulk_sanity_checks([lot], prefetched_data, background=False)
        # create events
        e = CarbureLotEvent()
        e.event_type = CarbureLotEvent.CREATED
        e.lot = lot
        e.user = request.user
        e.save()
    return JsonResponse({'status': 'success', 'data': new_lot_ids})


@check_user_rights(role=[UserRights.RW, UserRights.ADMIN])
def stock_transform(request, *args, **kwargs):
    context = kwargs['context']
    entity_id = context['entity_id']
    entity = Entity.objects.get(pk=entity_id)
    payload = request.POST.get('payload', False)
    if not payload:
        return JsonResponse({'status': 'error', 'message': 'Missing payload'}, status=400)

    try:
        unserialized = json.loads(payload)
        # expected format: [{stock_id: 12344, transformation_type: 'ETBE', otherfields}]
    except:
        return JsonResponse({'status': 'error', 'message': 'Cannot parse payload into JSON'}, status=400)

    if not isinstance(unserialized, list):
        return JsonResponse({'status': 'error', 'message': 'Parsed JSON is not a list'}, status=400)

    for entry in unserialized:
        # check minimum fields
        required_fields = ['stock_id', 'transformation_type']
        for field in required_fields:
            if field not in entry:
                return JsonResponse({'status': 'error', 'message': 'Missing field %s in json object'}, status=400)

        try:
            stock = CarbureStock.objects.get(pk=entry['stock_id'])
        except:
            return JsonResponse({'status': 'error', 'message': 'Could not find stock'}, status=400)

        if stock.carbure_client != entity:
            return JsonResponse({'status': 'forbidden', 'message': 'Stock does not belong to you'}, status=403)

        ttype = entry['transformation_type']
        if ttype == CarbureStockTransformation.ETH_ETBE:
            error = handle_eth_to_etbe_transformation(request.user, stock, entry)
            if error:
                return error
    return JsonResponse({'status': 'success'})


@check_user_rights()
def get_lot_details(request, *args, **kwargs):
    context = kwargs['context']
    entity_id = int(context['entity_id'])
    lot_id = request.GET.get('lot_id', False)
    if not lot_id:
        return JsonResponse({'status': 'error', 'message': 'Missing lot_id'}, status=400)

    lot = CarbureLot.objects.get(pk=lot_id)
    if lot.carbure_client_id != entity_id and lot.carbure_supplier_id != entity_id and lot.added_by_id != entity_id:
        return JsonResponse({'status': 'forbidden', 'message': "User not allowed"}, status=403)

    data = {}
    data['lot'] = CarbureLotPublicSerializer(lot).data
    entity = Entity.objects.get(id=entity_id)
    if entity.entity_type == Entity.ADMIN or (lot.added_by == entity or (lot.parent_lot and lot.parent_lot.carbure_client == entity)):
        data['parent_lot'] = CarbureLotPublicSerializer(lot.parent_lot).data if lot.parent_lot else None
        data['parent_stock'] = CarbureStockPublicSerializer(lot.parent_stock).data if lot.parent_stock else None
    else:
        data['parent_lot'] = None
        data['parent_stock'] = None
    children = CarbureLot.objects.filter(parent_lot=lot).exclude(lot_status=CarbureLot.DELETED)
    data['children_lot'] = CarbureLotPublicSerializer(children, many=True).data
    data['children_stock'] = CarbureStockPublicSerializer(CarbureStock.objects.filter(parent_lot=lot), many=True).data
    data['distance'] = get_transaction_distance(lot)
    data['errors'] = get_lot_errors(lot, entity)
    data['certificates'] = get_known_certificates(lot)
    data['updates'] = get_lot_updates(lot, entity)
    data['comments'] = get_lot_comments(lot, entity)
    return JsonResponse({'status': 'success', 'data': data})


@check_user_rights()
def get_lots_filters(request, *args, **kwargs):
    context = kwargs['context']
    entity_id = context['entity_id']
    status = request.GET.get('status', False)
    field = request.GET.get('field', False)
    if not field:
        return JsonResponse({'status': 'error', 'message': 'Please specify the field for which you want the filters'}, status=400)
    entity = Entity.objects.get(id=entity_id)
    txs = get_entity_lots_by_status(entity, status)
    data = get_lots_filters_data(txs, request.GET, entity, field)
    if data is None:
        return JsonResponse({'status': 'error', 'message': "Could not find specified filter"}, status=400)
    else:
        return JsonResponse({'status': 'success', 'data': data})

@check_user_rights(role=[UserRights.RW, UserRights.ADMIN])
def add_lot(request, *args, **kwargs):
    context = kwargs['context']
    entity_id = context['entity_id']
    entity = Entity.objects.get(pk=entity_id)
    d = get_prefetched_data(entity)
    lot_obj, errors = construct_carbure_lot(d, entity, request.POST.dict())
    if not lot_obj:
        return JsonResponse({'status': 'error', 'message': 'Something went wrong'}, status=400)
    # run sanity checks, insert lot and errors
    lots_created = bulk_insert_lots(entity, [lot_obj], [errors], d)
    if len(lots_created) == 0:
        return JsonResponse({'status': 'error', 'message': 'Something went wrong'}, status=500)
    e = CarbureLotEvent()
    e.event_type = CarbureLotEvent.CREATED
    e.lot_id = lots_created[0].id
    e.user = request.user
    e.metadata = {'source': 'MANUAL'}
    e.save()
    data = CarbureLotPublicSerializer(e.lot).data
    return JsonResponse({'status': 'success', 'data': data})

@check_user_rights(role=[UserRights.RW, UserRights.ADMIN])
def add_excel(request, *args, **kwargs):
    context = kwargs['context']
    entity_id = context['entity_id']
    entity = Entity.objects.get(pk=entity_id)
    d = get_prefetched_data(entity)

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
    data = convert_template_row_to_formdata(entity, d, filepath)
    nb_total = 0
    nb_valid = 0
    nb_invalid = 0
    lots = []
    lots_errors = []
    for row in data:
        lot_obj, errors = construct_carbure_lot(d, entity, row)
        if not lot_obj:
            nb_invalid += 1
        else:
            nb_valid += 1
        nb_total += 1
        lots.append(lot_obj)
        lots_errors.append(errors)
    lots_created = bulk_insert_lots(entity, lots, lots_errors, d)
    if len(lots_created) == 0:
        return JsonResponse({'status': 'error', 'message': 'Something went wrong'}, status=500)
    for lot in lots_created:
        e = CarbureLotEvent()
        e.event_type = CarbureLotEvent.CREATED
        e.lot_id = lot.id
        e.user = request.user
        e.metadata = {'source': 'EXCEL'}
        e.save()
        if lot.parent_stock:
            rounded_volume = round(lot.volume, 2)
            stock = CarbureStock.objects.get(id=lot.parent_stock.id) # force fetch in db to get the actual uncached remaining_volume
            stock.remaining_volume = round(stock.remaining_volume - rounded_volume, 2)
            stock.remaining_weight = stock.get_weight()
            stock.remaining_lhv_amount = stock.get_lhv_amount()
            stock.save()
            event = CarbureStockEvent()
            event.event_type = CarbureStockEvent.SPLIT
            event.stock = stock
            event.user = request.user
            event.metadata = {'message': 'Envoi lot.', 'volume_to_deduct': lot.volume}
            event.save()
    return JsonResponse({'status': 'success', 'data': {'lots': nb_total, 'valid': nb_valid, 'invalid': nb_invalid}})


@check_user_rights(role=[UserRights.RW, UserRights.ADMIN])
def update_lot(request, *args, **kwargs):
    context = kwargs['context']
    entity_id = context['entity_id']
    lot_id = request.POST.get('lot_id', None)
    if not lot_id:
        return JsonResponse({'status': 'error', 'message': 'Missing lot_id'}, status=400)
    entity = Entity.objects.get(pk=entity_id)

    try:
        existing_lot = CarbureLot.objects.get(id=lot_id, added_by=entity)
    except:
        return JsonResponse({'status': 'error', 'message': 'Could not find lot'}, status=400)

    previous = CarbureLotPublicSerializer(existing_lot).data
    # prefetch some data
    d = get_prefetched_data(entity)
    updated_lot, errors = construct_carbure_lot(d, entity, request.POST.dict(), existing_lot)
    if not updated_lot:
        return JsonResponse({'status': 'error', 'message': 'Something went wrong'}, status=400)
    # run sanity checks, insert lot and errors
    updated_lot.save()
    for e in errors:
        e.lot = updated_lot
    GenericError.objects.bulk_create(errors, batch_size=100)
    bulk_sanity_checks([updated_lot], d, background=False)
    data = CarbureLotPublicSerializer(updated_lot).data
    diff = dictdiffer.diff(previous, data)
    added = []
    removed = []
    changed = []
    foreign_key_to_field_mapping = {'carbure_production_site': 'name', 'carbure_delivery_site': 'depot_id', 'carbure_client': 'name', 'delivery_site_country': 'code_pays', 'country_of_origin': 'code_pays', 'biofuel': 'code', 'feedstock': 'code'}
    fields_to_ignore = ['lhv_amount', 'weight']
    for d in diff:
        action, field, data = d
        if field in fields_to_ignore:
            continue
        if action == 'change':
            if '.' in field:
                s = field.split('.')
                mainfield = s[0]
                subfield = s[1]
                if mainfield in foreign_key_to_field_mapping:
                    subfield_to_record = foreign_key_to_field_mapping[mainfield]
                    if subfield != subfield_to_record:
                        continue
                field = mainfield
            changed.append((field, data[0], data[1]))
        if action == 'add':
            if isinstance(data, tuple):
                added.append((field, data))
            if isinstance(data, list):
                if field in foreign_key_to_field_mapping:
                    subfield_to_record = foreign_key_to_field_mapping[field]
                    for (subfield, value) in data:
                        if subfield != subfield_to_record:
                            continue
                        added.append((field, value))
        if action == 'remove':
            if isinstance(data, tuple):
                removed.append((field, data))
            if isinstance(data, list):
                if field in foreign_key_to_field_mapping:
                    subfield_to_record = foreign_key_to_field_mapping[field]
                    for (subfield, value) in data:
                        if subfield != subfield_to_record:
                            continue
                        removed.append((field, value))
    e = CarbureLotEvent()
    e.event_type = CarbureLotEvent.UPDATED
    e.lot = updated_lot
    e.user = request.user
    e.metadata = {'added': added, 'removed': removed, 'changed': changed}
    e.save()
    return JsonResponse({'status': 'success', 'data': data})


@check_user_rights(role=[UserRights.RW, UserRights.ADMIN])
def duplicate_lot(request, *args, **kwargs):
    context = kwargs['context']
    entity_id = context['entity_id']
    lot_id = request.POST.get('lot_id', None)
    try:
        lot = CarbureLot.objects.get(id=lot_id)
    except Exception:
        return JsonResponse({'status': 'error', 'message': "Unknown Lot %s" % (lot_id)}, status=400)

    if lot.added_by_id != int(entity_id):
        return JsonResponse({'status': 'forbidden', 'message': "User not allowed"}, status=403)

    lot.pk = None
    lot.parent_stock = None
    lot.parent_lot = None
    lot_fields_to_remove = ['carbure_id', 'correction_status', 'lot_status', 'delivery_status', 'declared_by_supplier', 'declared_by_client', 'highlighted_by_admin', 'highlighted_by_auditor']
    lot_meta_fields = {f.name: f for f in CarbureLot._meta.get_fields()}
    for f in lot_fields_to_remove:
        if f in lot_meta_fields:
            meta_field = lot_meta_fields[f]
            if meta_field.default != NOT_PROVIDED:
                setattr(lot, f, meta_field.default)
            else:
                setattr(lot, f, '')
    lot.save()
    return JsonResponse({'status': 'success'})


@check_user_rights(role=[UserRights.RW, UserRights.ADMIN])
def lots_send(request, *args, **kwargs):
    context = kwargs['context']
    entity_id = context['entity_id']
    status = request.POST.get('status', None)
    entity = Entity.objects.get(id=entity_id)
    lots = get_entity_lots_by_status(entity, status)
    filtered_lots = filter_lots(lots, request.POST, entity)
    nb_lots = len(filtered_lots)
    nb_sent = 0
    nb_rejected = 0
    nb_ignored = 0
    nb_auto_accepted = 0
    trading_lots = []
    prefetched_data = get_prefetched_data(entity)
    for lot in filtered_lots:
        if lot.added_by != entity:
            return JsonResponse({'status': 'forbidden', 'message': 'Entity not authorized to send this lot'}, status=403)
        if lot.lot_status != CarbureLot.DRAFT:
            return JsonResponse({'status': 'error', 'message': 'Lot is not a draft'}, status=400)

        if lot.lot_status in [CarbureLot.ACCEPTED, CarbureLot.FROZEN]:
            # ignore, lot already accepted
            nb_ignored += 1
            continue

        # sanity check !!!
        is_sane, errors = sanity_check(lot, prefetched_data)
        if not is_sane:
            nb_rejected += 1
            continue
        nb_sent += 1
        event = CarbureLotEvent()
        event.event_type = CarbureLotEvent.VALIDATED
        event.lot = lot
        event.user = request.user
        event.save()

        lot.lot_status = CarbureLot.PENDING

        #### SPECIFIC CASES
        # I AM NEITHER THE PRODUCER NOR THE CLIENT (Trading)
        # create two transactions. unknown producer/supplier -> me and me -> client
        if lot.carbure_supplier != entity and lot.carbure_client != entity:
            # AUTO ACCEPT FIRST TRANSACTION
            final_client = lot.carbure_client
            nb_auto_accepted += 1
            lot.lot_status = CarbureLot.ACCEPTED
            lot.delivery_type = CarbureLot.TRADING
            lot.carbure_client = entity
            lot.save()
            first_lot_id = lot.id
            event = CarbureLotEvent()
            event.event_type = CarbureLotEvent.ACCEPTED
            event.lot = lot
            event.user = request.user
            event.save()
            # SECOND TRANSACTION
            lot.pk = None
            lot.parent_lot_id = first_lot_id
            lot.carbure_client = final_client
            lot.unknown_supplier = ''
            lot.carbure_supplier = lot.carbure_vendor
            lot.supplier_certificate = lot.vendor_certificate
            lot.supplier_certificate_type = lot.vendor_certificate_type
            lot.carbure_vendor = None
            lot.vendor_certificate = None
            lot.vendor_certificate_type = ''
            lot.lot_status = CarbureLot.PENDING
            lot.delivery_type = CarbureLot.UNKNOWN
            lot.save()
            trading_lots.append(lot)
            event = CarbureLotEvent()
            event.event_type = CarbureLotEvent.ACCEPTED
            event.lot = lot
            event.user = request.user
            event.save()
        elif lot.carbure_client_id is None:
            # RFC or EXPORT
            nb_auto_accepted += 1
            lot.lot_status = CarbureLot.ACCEPTED
            lot.save()
            event = CarbureLotEvent()
            event.event_type = CarbureLotEvent.ACCEPTED
            event.lot = lot
            event.user = request.user
            event.save()
        elif lot.carbure_client == entity and lot.delivery_type not in (CarbureLot.UNKNOWN, None):
            lot.lot_status = CarbureLot.ACCEPTED
            lot.save()
            event = CarbureLotEvent()
            event.event_type = CarbureLotEvent.ACCEPTED
            event.lot = lot
            event.user = request.user
            event.save()
            if lot.delivery_type == CarbureLot.STOCK:
                stock = CarbureStock()
                stock.parent_lot = lot
                if lot.carbure_delivery_site is None:
                    lot.lot_status = CarbureLot.DRAFT
                    lot.save()
                    return JsonResponse({'status': 'error', 'message': 'Cannot add stock into unknown Depot'}, status=400)
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
                stock.carbure_id = '%sS%d' % (lot.carbure_id, stock.id)
                stock.save()
        else:
            pass
        lot.save()
    if nb_sent == 0:
        return JsonResponse({'status': 'success', 'data': {'submitted': nb_lots, 'sent': nb_sent, 'auto-accepted': nb_auto_accepted, 'ignored': nb_ignored, 'rejected': nb_rejected}}, status=400)
    ids = [i.id for i in filtered_lots] + [i.id for i in trading_lots]
    notif_lots = CarbureLot.objects.filter(id__in=ids)
    notify_lots_received(notif_lots)
    return JsonResponse({'status': 'success', 'data': {'submitted': nb_lots, 'sent': nb_sent, 'auto-accepted': nb_auto_accepted, 'ignored': nb_ignored, 'rejected': nb_rejected}})


@check_user_rights(role=[UserRights.RW, UserRights.ADMIN])
def lots_delete(request, *args, **kwargs):
    context = kwargs['context']
    entity_id = context['entity_id']
    status = request.POST.get('status', None)
    entity = Entity.objects.get(id=entity_id)
    lots = get_entity_lots_by_status(entity, status)
    filtered_lots = filter_lots(lots, request.POST, entity)
    if filtered_lots.count() == 0:
        return JsonResponse({'status': 'error', 'message': 'Could not find lots to delete'}, status=400)
    for lot in filtered_lots:
        if lot.added_by != entity:
            return JsonResponse({'status': 'forbidden', 'message': 'Entity not authorized to delete this lot'}, status=403)

        if lot.lot_status not in [CarbureLot.DRAFT, CarbureLot.REJECTED] and not (lot.lot_status in [CarbureLot.PENDING, CarbureLot.ACCEPTED] and lot.correction_status == CarbureLot.IN_CORRECTION):
            # cannot delete lot accepted / frozen or already deleted
            return JsonResponse({'status': 'error', 'message': 'Cannot delete lot'}, status=400)

        event = CarbureLotEvent()
        event.event_type = CarbureLotEvent.DELETED
        event.lot = lot
        event.user = request.user
        event.save()
        lot.lot_status = CarbureLot.DELETED
        lot.save()
        if lot.parent_stock is not None:
            stock = CarbureStock.objects.get(id=lot.parent_stock.id) # force refresh from db
            stock.remaining_volume = round(stock.remaining_volume + lot.volume, 2)
            stock.remaining_weight = stock.get_weight()
            stock.remaining_lhv_amount = stock.get_lhv_amount()
            stock.save()
            # save event
            event = CarbureStockEvent()
            event.event_type = CarbureStockEvent.UNSPLIT
            event.stock = lot.parent_stock
            event.user = None
            event.metadata = {'message': 'child lot deleted. recredit volume.', 'volume_to_credit': lot.volume}
            event.save()
        if lot.parent_lot:
            if lot.parent_lot.delivery_type in [CarbureLot.PROCESSING, CarbureLot.TRADING]:
                lot.parent_lot.lot_status = CarbureLot.PENDING
                lot.parent_lot.delivery_type = CarbureLot.OTHER
                lot.parent_lot.save()
                # save event
                event = CarbureLotEvent()
                event.event_type = CarbureLotEvent.RECALLED
                event.lot = lot.parent_lot
                event.user = None
                event.metadata = {'message': 'child lot deleted. back to inbox.'}
                event.save()

    return JsonResponse({'status': 'success'})



@check_user_rights()
def get_stock_filters(request, *args, **kwargs):
    context = kwargs['context']
    entity_id = context['entity_id']
    field = request.GET.get('field', False)
    if not field:
        return JsonResponse({'status': 'error', 'message': 'Please specify the field for which you want the filters'}, status=400)
    txs = get_entity_stock(entity_id)
    data = get_stock_filters_data(txs, request.GET, field)
    if data is None:
        return JsonResponse({'status': 'error', 'message': "Could not find specified filter"}, status=400)
    else:
        return JsonResponse({'status': 'success', 'data': data})


@check_user_rights()
def get_declarations(request, *args, **kwargs):
    context = kwargs['context']
    entity_id = context['entity_id']
    year = request.GET.get('year', False)
    try:
        year = int(year)
    except Exception:
        return JsonResponse({'status': 'error', 'message': 'Missing year'}, status=400)

    periods = [str(year * 100 + i) for i in range(1, 13)]
    period_dates = [datetime.datetime(year, i, 1) for i in range(1, 13)]

    period_lots = CarbureLot.objects.filter(period__in=periods) \
        .filter(Q(carbure_client_id=entity_id) | Q(carbure_supplier_id=entity_id)) \
        .exclude(lot_status__in=[CarbureLot.DRAFT, CarbureLot.DELETED]) \
        .values('period') \
        .annotate(count=Count('id', distinct=True))
    lots_by_period = {}
    for period_lot in period_lots:
        lots_by_period[str(period_lot['period'])] = period_lot['count']

    pending_period_lots = CarbureLot.objects.filter(period__in=periods) \
        .filter(Q(carbure_client_id=entity_id) | Q(carbure_supplier_id=entity_id)) \
        .exclude(lot_status__in=[CarbureLot.DRAFT, CarbureLot.DELETED]) \
        .filter(Q(lot_status__in=[CarbureLot.PENDING, CarbureLot.REJECTED]) | Q(correction_status__in=[CarbureLot.IN_CORRECTION, CarbureLot.FIXED])) \
        .values('period') \
        .annotate(count=Count('id', distinct=True))
    pending_by_period = {}
    for period_lot in pending_period_lots:
        pending_by_period[str(period_lot['period'])] = period_lot['count']

    declarations = SustainabilityDeclaration.objects.filter(entity_id=entity_id, period__in=period_dates)
    declarations_by_period = {}
    for declaration in declarations:
        period = declaration.period.strftime('%Y%m')
        declarations_by_period[period] = declaration.natural_key()

    data = []
    for period in periods:
        data.append({
            'period': int(period),
            'lots': lots_by_period[period] if period in lots_by_period else 0,
            'pending': pending_by_period[period] if period in pending_by_period else 0,
            'declaration': declarations_by_period[period] if period in declarations_by_period else None
        })

    return JsonResponse({'status': 'success', 'data': data})


@check_user_rights(role=[UserRights.RW, UserRights.ADMIN])
def add_comment(request, *args, **kwargs):
    context = kwargs['context']
    entity_id = context['entity_id']
    status = request.POST.get('status', False)
    comment = request.POST.get('comment', False)
    if not comment:
        return JsonResponse({'status': 'error', 'message': 'Missing comment'}, status=400)
    is_visible_by_admin = request.POST.get('is_visible_by_admin', False)
    is_visible_by_auditor = request.POST.get('is_visible_by_auditor', False)
    entity = Entity.objects.get(id=entity_id)
    lots = get_entity_lots_by_status(entity, status)
    lots = filter_lots(lots, request.POST, entity)

    for lot in lots.iterator():
        if lot.carbure_supplier != entity and lot.carbure_client != entity and entity.entity_type not in [Entity.AUDITOR, Entity.ADMIN]:
            return JsonResponse({'status': 'forbidden', 'message': 'Entity not authorized to comment on this lot'}, status=403)

        lot_comment = CarbureLotComment()
        lot_comment.entity = entity
        lot_comment.user = request.user
        lot_comment.lot = lot
        if entity.entity_type == Entity.AUDITOR:
            lot_comment.comment_type = CarbureLotComment.AUDITOR
            if is_visible_by_admin == 'true':
                lot_comment.is_visible_by_admin = True
        elif entity.entity_type == Entity.ADMIN:
            lot_comment.comment_type = CarbureLotComment.ADMIN
            if is_visible_by_auditor == 'true':
                lot_comment.is_visible_by_auditor = True
        else:
            lot_comment.comment_type = CarbureLotComment.REGULAR
        lot_comment.comment = comment
        lot_comment.save()
    return JsonResponse({'status': 'success'})


@check_user_rights(role=[UserRights.RW, UserRights.ADMIN])
def request_fix(request, *args, **kwargs):
    context = kwargs['context']
    entity_id = context['entity_id']
    lot_ids = request.POST.getlist('lot_ids', False)
    if not lot_ids:
        return JsonResponse({'status': 'error', 'message': 'Missing lot_ids'}, status=400)

    entity = Entity.objects.get(pk=entity_id)
    try:
        lots = CarbureLot.objects.filter(pk__in=lot_ids)
    except:
        return JsonResponse({'status': 'error', 'message': 'Could not find lots'}, status=400)
    for lot in lots.iterator():
        if lot.lot_status == CarbureLot.FROZEN:
            return JsonResponse({'status': 'error', 'message': 'Lot is already declared, now in read-only mode.'}, status=400)

        if lot.carbure_client != entity:
            return JsonResponse({'status': 'forbidden', 'message': 'Entity not authorized to change this lot'}, status=403)
        lot.correction_status = CarbureLot.IN_CORRECTION
        lot.save()
        event = CarbureLotEvent()
        event.event_type = CarbureLotEvent.FIX_REQUESTED
        event.lot = lot
        event.user = request.user
        event.save()
    notify_correction_request(lots)
    return JsonResponse({'status': 'success'})

@check_user_rights(role=[UserRights.RW, UserRights.ADMIN])
def mark_as_fixed(request, *args, **kwargs):
    context = kwargs['context']
    entity_id = context['entity_id']
    lot_ids = request.POST.getlist('lot_ids', False)
    if not lot_ids:
        return JsonResponse({'status': 'error', 'message': 'Missing lot_ids'}, status=400)

    entity = Entity.objects.get(pk=entity_id)
    try:
        lots = CarbureLot.objects.filter(pk__in=lot_ids)
    except:
        return JsonResponse({'status': 'error', 'message': 'Could not find lots'}, status=400)
    for lot in lots.iterator():
        if lot.added_by != entity and lot.carbure_supplier != entity and lot.carbure_client != entity:
            return JsonResponse({'status': 'forbidden', 'message': 'Entity not authorized to change this lot'}, status=403)

        if lot.lot_status == CarbureLot.REJECTED:
            lot.lot_status = CarbureLot.PENDING
            lot.correction_status = CarbureLot.NO_PROBLEMO
        elif lot.added_by == entity and (lot.carbure_client == entity or lot.carbure_client is None):
            lot.correction_status = CarbureLot.NO_PROBLEMO
        else:
            lot.correction_status = CarbureLot.FIXED
        lot.save()
        child = CarbureLot.objects.filter(parent_lot=lot)
        for c in child:
            c.copy_sustainability_data(lot)
            # also copy transaction detail
            c.volume = lot.volume
            c.weight = lot.weight
            c.lhv_amount = lot.lhv_amount
            c.transport_document_type = lot.transport_document_type
            c.transport_document_reference = lot.transport_document_reference
            c.delivery_date = lot.delivery_date
            c.carbure_delivery_site = lot.carbure_delivery_site
            c.unknown_delivery_site = lot.unknown_delivery_site
            c.delivery_site_country = lot.delivery_site_country
            c.save()
        event = CarbureLotEvent()
        event.event_type = CarbureLotEvent.MARKED_AS_FIXED
        event.lot = lot
        event.user = request.user
        event.save()
    notify_correction_done(lots)
    return JsonResponse({'status': 'success'})

@check_user_rights(role=[UserRights.RW, UserRights.ADMIN])
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
        # CASCADING CORRECTIONS
        if lot.delivery_type == CarbureLot.STOCK:
            stocks = CarbureStock.objects.filter(parent_lot=lot)
            children = CarbureLot.objects.filter(parent_stock__in=stocks)
            for c in children:
                c.copy_sustainability_data(lot)
                c.save()
                event = CarbureLotEvent()
                event.event_type = CarbureLotEvent.UPDATED
                event.lot = lot
                event.user = request.user
                event.metadata = {'comment': 'Cascading update of sustainability data'}
                event.save()
            transformations = CarbureStockTransformation.objects.filter(source_stock__in=stocks)
            for t in transformations:
                new_stock = t.dest_stock
                child = CarbureLot.objects.filter(parent_stock=new_stock)
                for c in child:
                    c.copy_sustainability_data(lot)
                    c.save()
                    event = CarbureLotEvent()
                    event.event_type = CarbureLotEvent.UPDATED
                    event.lot = lot
                    event.user = request.user
                    event.metadata = {'comment': 'Cascading update of sustainability data'}
                    event.save()
        event = CarbureLotEvent()
        event.event_type = CarbureLotEvent.FIX_ACCEPTED
        event.lot = lot
        event.user = request.user
        event.save()
    return JsonResponse({'status': 'success'})

@check_user_rights(role=[UserRights.RW, UserRights.ADMIN])
def reject_lot(request, *args, **kwargs):
    context = kwargs['context']
    entity_id = context['entity_id']
    status = request.POST.get('status', False)

    entity = Entity.objects.get(id=entity_id)
    lots = get_entity_lots_by_status(entity, status)
    lots = filter_lots(lots, request.POST, entity, will_aggregate=True)

    for lot in lots.iterator():
        if lot.carbure_client != entity:
            return JsonResponse({'status': 'forbidden', 'message': 'Only the client can reject this lot'}, status=403)

        if lot.lot_status == CarbureLot.DRAFT:
            return JsonResponse({'status': 'error', 'message': 'Cannot reject DRAFT'}, status=400)
        elif lot.lot_status == CarbureLot.PENDING:
            pass
        elif lot.lot_status == CarbureLot.REJECTED:
            return JsonResponse({'status': 'error', 'message': 'Lot is already rejected.'}, status=400)
        elif lot.lot_status == CarbureLot.ACCEPTED:
            pass
        elif lot.lot_status == CarbureLot.FROZEN:
            return JsonResponse({'status': 'error', 'message': 'Lot is Frozen. Cannot reject. Please invalidate declaration first.'}, status=400)
        elif lot.lot_status == CarbureLot.DELETED:
            return JsonResponse({'status': 'error', 'message': 'Lot is deleted. Cannot reject'}, status=400)

        lot.lot_status = CarbureLot.REJECTED
        lot.correction_status = CarbureLot.IN_CORRECTION
        lot.carbure_client = None
        lot.save()
        event = CarbureLotEvent()
        event.event_type = CarbureLotEvent.REJECTED
        event.lot = lot
        event.user = request.user
        event.save()
    notify_lots_rejected(lots)
    return JsonResponse({'status': 'success'})

@check_user_rights(role=[UserRights.RW, UserRights.ADMIN])
def recall_lot(request, *args, **kwargs):
    context = kwargs['context']
    entity_id = context['entity_id']
    lot_ids = request.POST.getlist('lot_ids', False)
    if not lot_ids:
        return JsonResponse({'status': 'error', 'message': 'Missing lot_ids'}, status=400)

    entity = Entity.objects.get(pk=entity_id)
    try:
        lots = CarbureLot.objects.filter(pk__in=lot_ids)
    except:
        return JsonResponse({'status': 'error', 'message': 'Could not find lots'}, status=400)
    for lot in lots.iterator():
        if lot.carbure_supplier != entity and lot.added_by != entity:
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

        lot.correction_status = CarbureLot.IN_CORRECTION
        lot.save()
        event = CarbureLotEvent()
        event.event_type = CarbureLotEvent.RECALLED
        event.lot = lot
        event.user = request.user
        event.save()
    notify_lots_recalled(lots)
    return JsonResponse({'status': 'success'})


@check_user_rights(role=[UserRights.RW, UserRights.ADMIN])
def accept_rfc(request, *args, **kwargs):
    context = kwargs['context']
    entity_id = context['entity_id']
    status = request.POST.get('status', False)

    entity = Entity.objects.get(id=entity_id)
    lots = get_entity_lots_by_status(entity, status)
    lots = filter_lots(lots, request.POST, entity, will_aggregate=True)

    for lot in lots.iterator():
        if int(entity_id) != lot.carbure_client_id:
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

@check_user_rights(role=[UserRights.RW, UserRights.ADMIN])
def accept_in_stock(request, *args, **kwargs):
    context = kwargs['context']
    entity_id = context['entity_id']
    status = request.POST.get('status', False)

    entity = Entity.objects.get(id=entity_id)
    lots = get_entity_lots_by_status(entity, status)
    lots = filter_lots(lots, request.POST, entity, will_aggregate=True)

    if entity.entity_type == Entity.OPERATOR:
        return JsonResponse({'status': 'error', 'message': 'Stock unavailable for Operators'}, status=400)

    for lot in lots.iterator():
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
        if lot.carbure_delivery_site is None:
            lot.lot_status = CarbureLot.PENDING
            lot.delivery_type = CarbureLot.UNKNOWN
            lot.save()
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
        stock.carbure_id = '%sS%d' % (lot.carbure_id, stock.id)
        stock.save()
    return JsonResponse({'status': 'success'})


@check_user_rights(role=[UserRights.RW, UserRights.ADMIN])
def accept_blending(request, *args, **kwargs):
    context = kwargs['context']
    entity_id = context['entity_id']
    status = request.POST.get('status', False)

    entity = Entity.objects.get(id=entity_id)
    lots = get_entity_lots_by_status(entity, status)
    lots = filter_lots(lots, request.POST, entity, will_aggregate=True)

    for lot in lots.iterator():
        if int(entity_id) != lot.carbure_client_id:
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

@check_user_rights(role=[UserRights.RW, UserRights.ADMIN])
def accept_export(request, *args, **kwargs):
    context = kwargs['context']
    entity_id = context['entity_id']
    status = request.POST.get('status', False)

    entity = Entity.objects.get(id=entity_id)
    lots = get_entity_lots_by_status(entity, status)
    lots = filter_lots(lots, request.POST, entity, will_aggregate=True)

    for lot in lots.iterator():
        if int(entity_id) != lot.carbure_client_id:
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

@check_user_rights(role=[UserRights.RW, UserRights.ADMIN])
def accept_direct_delivery(request, *args, **kwargs):
    context = kwargs['context']
    entity_id = context['entity_id']
    status = request.POST.get('status', False)

    entity = Entity.objects.get(id=entity_id)
    lots = get_entity_lots_by_status(entity, status)
    lots = filter_lots(lots, request.POST, entity, will_aggregate=True)

    for lot in lots.iterator():
        if int(entity_id) != lot.carbure_client_id:
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
        lot.delivery_type = CarbureLot.DIRECT
        lot.save()
        event = CarbureLotEvent()
        event.event_type = CarbureLotEvent.ACCEPTED
        event.lot = lot
        event.user = request.user
        event.save()
    return JsonResponse({'status': 'success'})

@check_user_rights(role=[UserRights.RW, UserRights.ADMIN])
def accept_processing(request, *args, **kwargs):
    context = kwargs['context']
    entity_id = context['entity_id']
    status = request.POST.get('status', False)
    processing_entity_id = request.POST.get('processing_entity_id', False)

    entity = Entity.objects.get(pk=entity_id)
    processing_entity = Entity.objects.get(pk=processing_entity_id)

    lots = get_entity_lots_by_status(entity, status)
    lots = filter_lots(lots, request.POST, entity, will_aggregate=True)

    for lot in lots.iterator():
        if int(entity_id) != lot.carbure_client_id:
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

@check_user_rights(role=[UserRights.RW, UserRights.ADMIN])
def accept_trading(request, *args, **kwargs):
    context = kwargs['context']
    entity_id = context['entity_id']
    client_entity_id = request.POST.get('client_entity_id', False)
    unknown_client = request.POST.get('unknown_client', False)
    certificate = request.POST.get('certificate', False)
    status = request.POST.get('status', False)
    entity = Entity.objects.get(id=entity_id)

    if not client_entity_id and not unknown_client:
        return JsonResponse({'status': 'error', 'message': 'Please specify either client_entity_id or unknown_client'}, status=400)

    if not certificate and entity.default_certificate == "":
        return JsonResponse({'status': 'error', 'message': 'Please specify a certificate'}, status=400)

    lots = get_entity_lots_by_status(entity, status)
    lots = filter_lots(lots, request.POST, entity, will_aggregate=True)

    if client_entity_id:
        try:
            client_entity = Entity.objects.get(pk=client_entity_id)
        except:
            return JsonResponse({'status': 'error', 'message': 'Could not find client entity'}, status=400)
    else:
        client_entity = None

    for lot in lots.iterator():
        if int(entity_id) != lot.carbure_client_id:
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
        child_lot.supplier_certificate = certificate
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

@check_user_rights(role=[UserRights.RW, UserRights.ADMIN])
def validate_declaration(request, *args, **kwargs):
    context = kwargs['context']
    entity_id = context['entity_id']
    period = request.POST.get('period', False)

    try:
        period_int = int(period)
        year = int(period_int / 100)
        month = period_int % 100
        period_d = datetime.date(year=year, month=month, day=1)
        nextmonth = period_d + datetime.timedelta(days=31)
        (weekday, lastday) = monthrange(nextmonth.year, nextmonth.month)
        deadline = datetime.date(year=nextmonth.year, month=nextmonth.month, day=lastday)
        declaration, _ = SustainabilityDeclaration.objects.get_or_create(entity_id=entity_id, period=period_d, deadline=deadline)
    except:
        return JsonResponse({'status': 'error', 'message': 'Could not parse period.'}, status=400)

    # ensure everything is in order
    pending_reception = CarbureLot.objects.filter(carbure_client=declaration.entity, period=period_int, lot_status=CarbureLot.PENDING).count()
    if pending_reception > 0:
        return JsonResponse({'status': 'error', 'message': 'Cannot validate declaration. Some lots are pending reception.'}, status=400)
    pending_correction = CarbureLot.objects.filter(carbure_client=declaration.entity, period=period_int, lot_status__in=[CarbureLot.ACCEPTED], correction_status__in=[CarbureLot.IN_CORRECTION, CarbureLot.FIXED]).count()
    if pending_correction > 0:
        return JsonResponse({'status': 'error', 'message': 'Cannot validate declaration. Some accepted lots need correction.'}, status=400)
    lots_sent_rejected_or_drafts = CarbureLot.objects.filter(carbure_supplier=declaration.entity, period=period_int, lot_status=CarbureLot.REJECTED).count()
    if lots_sent_rejected_or_drafts > 0:
        return JsonResponse({'status': 'error', 'message': 'Cannot validate declaration. Some outgoing lots need your attention.'}, status=400)
    lots_sent_to_fix = CarbureLot.objects.filter(carbure_supplier=declaration.entity, period=period_int, lot_status__in=[CarbureLot.ACCEPTED], correction_status__in=[CarbureLot.IN_CORRECTION]).count()
    if lots_sent_to_fix > 0:
        return JsonResponse({'status': 'error', 'message': 'Cannot validate declaration. Some outgoing lots need correction.'}, status=400)
    lots_received = CarbureLot.objects.filter(carbure_client=declaration.entity, period=period_int)
    lots_received.update(declared_by_client=True)
    lots_sent = CarbureLot.objects.filter(carbure_supplier=declaration.entity, period=period_int)
    lots_sent.update(declared_by_supplier=True)
    bulk_events = []
    for lot in lots_received:
        bulk_events.append(CarbureLotEvent(event_type=CarbureLotEvent.DECLARED, lot=lot, user=request.user))
    for lot in lots_sent:
        bulk_events.append(CarbureLotEvent(event_type=CarbureLotEvent.DECLARED, lot=lot, user=request.user))
    CarbureLotEvent.objects.bulk_create(bulk_events)
    # freeze lots
    CarbureLot.objects.filter(carbure_client=declaration.entity, period=period_int, declared_by_client=True, declared_by_supplier=True).update(lot_status=CarbureLot.FROZEN)
    CarbureLot.objects.filter(carbure_supplier=declaration.entity, period=period_int, declared_by_client=True, declared_by_supplier=True).update(lot_status=CarbureLot.FROZEN)
    # mark declaration
    declaration.declared = True
    declaration.save()
    # send email
    notify_declaration_validated(declaration)
    send_email_declaration_validated(declaration)
    return JsonResponse({'status': 'success'})


@check_user_rights(role=[UserRights.RW, UserRights.ADMIN])
def invalidate_declaration(request, *args, **kwargs):
    context = kwargs['context']
    entity_id = context['entity_id']
    period = request.POST.get('period', False)

    try:
        period_int = int(period)
        year = int(period_int / 100)
        month = period_int % 100
        period_d = datetime.date(year=year, month=month, day=1)
        nextmonth = period_d + datetime.timedelta(days=31)
        (weekday, lastday) = monthrange(nextmonth.year, nextmonth.month)
        deadline = datetime.date(year=nextmonth.year, month=nextmonth.month, day=lastday)
        declaration, _ = SustainabilityDeclaration.objects.get_or_create(entity_id=entity_id, period=period_d, deadline=deadline)
        declaration.declared = False
        declaration.checked = False
        declaration.save()
    except:
        return JsonResponse({'status': 'error', 'message': 'Could not parse period.'}, status=400)

    lots_received = CarbureLot.objects.filter(carbure_client=declaration.entity, period=period_int)
    lots_received.update(declared_by_client=False)
    lots_sent = CarbureLot.objects.filter(carbure_supplier=declaration.entity, period=period_int)
    lots_sent.update(declared_by_supplier=False)
    bulk_events = []
    for lot in lots_received:
        bulk_events.append(CarbureLotEvent(event_type=CarbureLotEvent.DECLCANCEL, lot=lot, user=request.user))
    for lot in lots_sent:
        bulk_events.append(CarbureLotEvent(event_type=CarbureLotEvent.DECLCANCEL, lot=lot, user=request.user))
    CarbureLotEvent.objects.bulk_create(bulk_events)
    # unfreeze lots
    CarbureLot.objects.filter(carbure_client=declaration.entity, period=period_int, declared_by_client=True, declared_by_supplier=True, lot_status=CarbureLot.FROZEN).update(lot_status=CarbureLot.ACCEPTED)
    CarbureLot.objects.filter(carbure_supplier=declaration.entity, period=period_int, declared_by_client=True, declared_by_supplier=True, lot_status=CarbureLot.FROZEN).update(lot_status=CarbureLot.ACCEPTED)
    # send email
    notify_declaration_cancelled(declaration)
    send_email_declaration_invalidated(declaration)
    return JsonResponse({'status': 'success'})

@check_user_rights()
def get_template(request, *args, **kwargs):
    context = kwargs['context']
    entity_id = context['entity_id']
    entity = Entity.objects.get(id=entity_id)
    file_location = template_v4(entity)
    try:
        with open(file_location, 'rb') as f:
            file_data = f.read()
            # sending response
            response = HttpResponse(file_data, content_type='application/vnd.ms-excel')
            response['Content-Disposition'] = 'attachment; filename="carbure_template.xlsx"'
            return response
    except Exception:
        return JsonResponse({'status': "error", 'message': "Error creating template file"}, status=500)

@check_user_rights()
def get_template_stock(request, *args, **kwargs):
    context = kwargs['context']
    entity_id = context['entity_id']
    entity = Entity.objects.get(id=entity_id)
    file_location = template_v4_stocks(entity)
    try:
        with open(file_location, 'rb') as f:
            file_data = f.read()
            # sending response
            response = HttpResponse(file_data, content_type='application/vnd.ms-excel')
            response['Content-Disposition'] = 'attachment; filename="carbure_template_stocks.xlsx"'
            return response
    except Exception:
        return JsonResponse({'status': "error", 'message': "Error creating template file"}, status=500)


@check_user_rights()
def toggle_warning(request, *args, **kwargs):
    context = kwargs['context']
    entity_id = context['entity_id']
    lot_id = request.POST.get('lot_id')
    errors = request.POST.getlist('errors')
    checked = request.POST.get('checked') == 'true'
    try:
        for error in errors:
            try:
                lot = CarbureLot.objects.get(id=lot_id)
                lot_error = GenericError.objects.get(lot_id=lot_id, error=error)
            except:
                traceback.print_exc()
                return JsonResponse({'status': "error", 'message': "Could not locate wanted lot or error"}, status=404)
            # is creator
            if lot.added_by_id == int(entity_id):
                lot_error.acked_by_creator = checked
            # is recipient
            if lot.carbure_client_id == int(entity_id):
                lot_error.acked_by_recipient = checked
            lot_error.save()
        return JsonResponse({'status': "success"})
    except:
        traceback.print_exc()
        return JsonResponse({'status': "error", 'message': "Could not update warning"}, status=500)


def get_stats(request):
    try:
        today = datetime.date.today()
        year = str(today.year)
        total_volume = CarbureLot.objects.filter(lot_status__in=[CarbureLot.ACCEPTED, CarbureLot.FROZEN], year=year, carbure_client__entity_type=Entity.OPERATOR).aggregate(Sum('volume'))
        entity_count = Entity.objects.filter(entity_type__in=[Entity.PRODUCER, Entity.TRADER, Entity.OPERATOR]).values('entity_type').annotate(count=Count('id'))
        entities = {}
        for r in entity_count:
            entities[r['entity_type']] = r['count']
        total = total_volume['volume__sum']
        if total is None:
            total = 1000
        return JsonResponse({'status': 'success', 'data': {'total_volume': total / 1000, 'entities': entities}})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': 'Could not compute statistics'})


@check_user_rights(role=[UserRights.RW, UserRights.ADMIN])
def update_entity(request, *args, **kwargs):
    context = kwargs['context']
    entity_id = context['entity_id']
    legal_name = request.POST.get('legal_name', False)
    registration_id = request.POST.get('registration_id', False)
    sustainability_officer_phone_number = request.POST.get('sustainability_officer_phone_number', False)
    sustainability_officer = request.POST.get('sustainability_officer', False)
    registered_address = request.POST.get('registered_address', False)
    entity = Entity.objects.get(id=entity_id)

    if legal_name:
        entity.legal_name = legal_name
    if sustainability_officer_phone_number:
        entity.sustainability_officer_phone_number = sustainability_officer_phone_number
    if registration_id:
        entity.registration_id = registration_id
    if sustainability_officer:
        entity.sustainability_officer = sustainability_officer
    if registered_address:
        entity.registered_address = registered_address
    entity.save()
    return JsonResponse({'status': 'success'})
