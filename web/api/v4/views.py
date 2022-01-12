import datetime
from json.encoder import py_encode_basestring_ascii
import unicodedata
import dictdiffer
import json
import time
import traceback
from django.db.models.aggregates import Count
from django.db.models.fields import NOT_PROVIDED

from django.http.response import HttpResponse, JsonResponse
from django.db.models.query_utils import Q
from core.common import convert_template_row_to_formdata, get_uploaded_files_directory
from core.decorators import check_user_rights
from api.v4.helpers import filter_lots, filter_stock, get_entity_lots_by_status, get_lot_comments, get_lot_errors, get_lot_updates, get_lots_summary_data, get_lots_with_metadata, get_lots_filters_data, get_entity_stock
from api.v4.helpers import get_prefetched_data, get_stock_events, get_stock_with_metadata, get_stock_filters_data, get_stocks_summary_data, get_transaction_distance, handle_eth_to_etbe_transformation
from api.v4.helpers import send_email_declaration_invalidated, send_email_declaration_validated
from api.v4.lots import construct_carbure_lot, bulk_insert_lots
from api.v4.sanity_checks import bulk_sanity_checks, sanity_check

from core.models import CarbureLot, CarbureLotComment, CarbureLotEvent, CarbureNotification, CarbureStock, CarbureStockEvent, CarbureStockTransformation, Entity, GenericError, Pays, SustainabilityDeclaration, UserRights
from core.serializers import CarbureLotPublicSerializer, CarbureStockPublicSerializer, CarbureStockTransformationPublicSerializer
from core.xlsx_v3 import template_v4, template_v4_stocks


@check_user_rights()
def get_years(request, *args, **kwargs):
    entity_id = int(kwargs['context']['entity_id'])
    data_lots = CarbureLot.objects.filter(Q(carbure_client_id=entity_id) | Q(carbure_supplier_id=entity_id)).values_list('year', flat=True).distinct()
    data_transforms = CarbureStockTransformation.objects.filter(entity_id=entity_id).values_list('transformation_dt__year', flat=True).distinct()
    data = set(list(data_transforms) + list(data_lots))
    return JsonResponse({'status': 'success', 'data': list(data)})


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

    lots_in = lots.filter(carbure_client_id=entity_id).exclude(lot_status__in=[CarbureLot.DELETED, CarbureLot.DRAFT])
    lots_in_pending = lots_in.filter(lot_status=CarbureLot.PENDING)
    lots_in_tofix = lots_in.exclude(correction_status=CarbureLot.NO_PROBLEMO)

    stock = CarbureStock.objects.filter(carbure_client_id=entity_id).filter(Q(parent_lot__year=year) | Q(parent_transformation__transformation_dt__year=year))
    stock_not_empty = stock.filter(remaining_volume__gt=0)

    lots_out = lots.filter(carbure_supplier_id=entity_id).exclude(lot_status__in=[CarbureLot.DELETED, CarbureLot.DRAFT])
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
    selection = request.GET.get('selection', False)
    if not status and not selection:
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
def get_lots_summary(request, *args, **kwargs):
    context = kwargs['context']
    entity_id = context['entity_id']
    status = request.GET.get('status', False)
    short = request.GET.get('short', False)
    if not status:
        return JsonResponse({'status': 'error', 'message': 'Missing status'}, status=400)
    try:
        lots = get_entity_lots_by_status(entity_id, status)
        lots = filter_lots(lots, request.GET, entity_id, will_aggregate=True)
        summary = get_lots_summary_data(lots, entity_id, short == 'true')
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
    data['children_lot'] = CarbureLotPublicSerializer(CarbureLot.objects.filter(parent_stock=stock), many=True).data
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

    for stock_id in stock_ids:
        try:
            stock = CarbureStock.objects.filter(pk=stock_id)
        except:
            return JsonResponse({'status': 'error', 'message': 'Could not find stock'}, status=400)

        if stock.carbure_client_id != entity_id:
            return JsonResponse({'status': 'forbidden', 'message': 'Stock does not belong to you'}, status=403)

        if stock.parent_transformation_id is None:
            return JsonResponse({'status': 'error', 'message': 'Stock does not come from a transformation'}, status=400)

        # all good
        # delete of transformation should trigger a cascading delete of child_lots + recredit volume to the parent_stock
        event = CarbureStockEvent()
        event.stock = stock.parent_transformation.parent_stock
        event.event_type = CarbureStockEvent.UNTRANSFORMED
        event.user = request.user
        event.save()
        stock.parent_transformation.delete()
    return JsonResponse({'status': 'success'})

@check_user_rights(role=[UserRights.RW, UserRights.ADMIN])
def stock_flush(request, *args, **kwargs):
    context = kwargs['context']
    entity_id = context['entity_id']
    payload = request.POST.getlist('payload', False)
    free_field = request.POST.getlist('free_field', False)
    if not payload:
        return JsonResponse({'status': 'error', 'message': 'Missing payload'}, status=400)

    try:
        unserialized = json.loads(payload)
        # expected format: [{stock_id: 12344, volume_flushed: 3244.33}]
    except:
        return JsonResponse({'status': 'error', 'message': 'Cannot parse payload into JSON'}, status=400)

    if not isinstance(unserialized, list):
        return JsonResponse({'status': 'error', 'message': 'Parsed JSON is not a list'}, status=400)

    for entry in unserialized:
        if 'stock_id' not in entry:
            return JsonResponse({'status': 'error', 'message': 'Missing key stock_id in object'}, status=400)
        if 'volume_flushed' not in entry:
            return JsonResponse({'status': 'error', 'message': 'Missing key volume_flushed in object'}, status=400)

        try:
            stock = CarbureStock.objects.filter(pk=entry['stock_id'])
        except:
            return JsonResponse({'status': 'error', 'message': 'Could not find stock'}, status=400)

        if stock.carbure_client_id != entity_id:
            return JsonResponse({'status': 'forbidden', 'message': 'Stock does not belong to you'}, status=403)

        try:
            volume_to_flush = float(entry['volume_flushed'])
        except:
            return JsonResponse({'status': 'error', 'message': 'Could not parse volume to flush'}, status=400)

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
        lot = stock.parent_lot
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

    try:
        unserialized = json.loads(payload)
        # expected format: [{stock_id: 12344, volume: 3244.33, transport_document_type: 'DAE', transport_document_reference: 'FR221244342WW'
        # dispatch_date: '2021-05-11', carbure_delivery_site_id: None, unknown_delivery_site: "SomeUnknownDepot", delivery_site_country_id: 120,
        # delivery_type: 'EXPORT', carbure_client_id: 12, unknown_client: None}]
    except:
        return JsonResponse({'status': 'error', 'message': 'Cannot parse payload into JSON'}, status=400)

    if not isinstance(unserialized, list):
        return JsonResponse({'status': 'error', 'message': 'Parsed JSON is not a list'}, status=400)

    for entry in unserialized:
        # check minimum fields
        required_fields = ['stock_id', 'volume', 'delivery_date', 'delivery_site_country_id'] # 'delivery_type'
        for field in required_fields:
            if field not in entry:
                return JsonResponse({'status': 'error', 'message': 'Missing field %s in json object' % (field)}, status=400)

        try:
            stock = CarbureStock.objects.get(pk=entry['stock_id'])
        except:
            return JsonResponse({'status': 'error', 'message': 'Could not find stock'}, status=400)

        if stock.carbure_client_id != int(entity_id):
            return JsonResponse({'status': 'forbidden', 'message': 'Stock does not belong to you'}, status=403)

        try:
            volume = float(entry['volume'])
        except:
            return JsonResponse({'status': 'error', 'message': 'Could not parse volume'}, status=400)

        # delivery_type = entry['delivery_type']
        # if delivery_type not in [CarbureLot.BLENDING, CarbureLot.EXPORT, CarbureLot.DIRECT, CarbureLot.PROCESSING, CarbureLot.RFC]:
        #     return JsonResponse({'status': 'error', 'message': 'Cannot split stock for this type of delivery'}, status=400)

        # create child lot
        rounded_volume = round(volume, 2)
        lot = stock.get_parent_lot()
        lot.pk = None
        lot.lot_status = CarbureLot.DRAFT
        lot.volume = rounded_volume
        lot.weight = lot.get_weight()
        lot.lhv_amount = lot.get_lhv_amount()
        lot.parent_stock = stock
        # common, mandatory data
        lot.delivery_site_country = Pays.objects.get(code_pays=entry['delivery_site_country_id'])
        lot.transport_document_reference = entry['transport_document_reference']
        lot.delivery_date = entry['delivery_date']
        lot.period = lot.delivery_date.year * 100 + lot.delivery_date.month
        if 'dispatch_date' in entry:
            lot.dispatch_date = entry['dispatch_date']
        lot.carbure_dispatch_site = stock.depot
        lot.dispatch_site_country = lot.carbure_dispatch_site.country
        lot.carbure_supplier_id = entity_id
        lot.added_bt_id = entity_id
        if 'carbure_client_id' in entry:
            lot.carbure_client_id = entry['carbure_client_id']
        elif 'unknown_client' in entry:
            lot.unknown_client = entry['unknown_client']

        # lot.delivery_type = delivery_type
        # delivery type specific data
        # if delivery_type in [CarbureLot.RFC, CarbureLot.EXPORT]:
        #     # carbure_client, carbure_delivery_site, transport_document_type and transport_document_reference are optional
        #     lot.lot_status = CarbureLot.ACCEPTED
        #     if 'transport_document_type' in entry:
        #         lot.transport_document_type = entry['transport_document_type']
        #     else:
        #         lot.transport_document_type = CarbureLot.OTHER
        #     if 'transport_document_reference' in entry:
        #         lot.transport_document_reference = entry['transport_document_reference']
        #     else:
        #         lot.transport_document_reference = lot.delivery_type
        #     if 'carbure_client_id' in entry:
        #         lot.carbure_client_id = entry['carbure_client_id']
        #     if 'carbure_delivery_site_id' in entry:
        #         lot.carbure_delivery_site_id = entry['carbure_delivery_site_id']
        #     if 'unknown_client' in entry:
        #         lot.unknown_client = entry['unknown_client']
        #     if 'unknown_delivery_site' in entry:
        #         lot.unknown_delivery_site = entry['unknown_delivery_site']
        # else: # BLENDING, DIRECT, PROCESSING
        #     required_fields = ['transport_document_type', 'transport_document_reference', 'carbure_delivery_site_id', 'carbure_client_id']
        #     for field in required_fields:
        #         if field not in entry:
        #             return JsonResponse({'status': 'error', 'message': 'Missing field %s in json object'}, status=400)
        #     lot.transport_document_type = entry['transport_document_type']
        #     lot.transport_document_reference = entry['transport_document_reference']
        #     lot.carbure_delivery_site_id = entry['carbure_delivery_site_id']
        #     lot.carbure_client_id = entry['carbure_client_id']
        lot.save()
        # update stock
        if rounded_volume >= stock.remaining_volume:
            stock.remaining_volume = 0
            stock.remaining_weight = 0
            stock.remaining_lhv_amount = 0
            rounded_volume = round(stock.remaining_volume, 2)
        else:
            stock.remaining_volume = round(stock.remaining_volume - rounded_volume, 2)
            stock.remaining_weight = stock.get_weight()
            stock.remaining_lhv_amount = stock.get_lhv_amount()
        stock.save()
        # create events
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
    if entity.entity_type == Entity.ADMIN or lot.added_by == entity:
        data['parent_lot'] = CarbureLotPublicSerializer(lot.parent_lot).data if lot.parent_lot else None
        data['parent_stock'] = CarbureStockPublicSerializer(lot.parent_stock).data if lot.parent_stock else None
    else:
        data['parent_lot'] = None
        data['parent_stock'] = None
    data['children_lot'] = CarbureLotPublicSerializer(CarbureLot.objects.filter(parent_lot=lot), many=True).data
    data['children_stock'] = CarbureStockPublicSerializer(CarbureStock.objects.filter(parent_lot=lot), many=True).data
    data['distance'] = get_transaction_distance(lot)
    data['errors'] = get_lot_errors(lot, entity_id)
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
    entity_id = int(context['entity_id'])
    status = request.POST.get('status', None)
    lots = get_entity_lots_by_status(entity_id, status)
    filtered_lots = filter_lots(lots, request.POST, entity_id)
    nb_lots = len(filtered_lots)
    nb_sent = 0
    nb_rejected = 0
    nb_ignored = 0
    nb_auto_accepted = 0
    entity = Entity.objects.get(pk=entity_id)
    prefetched_data = get_prefetched_data(entity)
    for lot in filtered_lots:
        if lot.added_by_id != entity_id:
            return JsonResponse({'status': 'forbidden', 'message': 'Entity not authorized to send this lot'}, status=403)
        if lot.lot_status != CarbureLot.DRAFT:
            return JsonResponse({'status': 'error', 'message': 'Lot is not a draft'}, status=400)

        if lot.lot_status in [CarbureLot.ACCEPTED, CarbureLot.FROZEN]:
            # ignore, lot already accepted
            nb_ignored += 1
            continue

        # sanity check !!!
        if not sanity_check(lot, prefetched_data):
            nb_rejected += 1
            continue
        nb_sent += 1
        event = CarbureLotEvent()
        event.event_type = CarbureLotEvent.VALIDATED
        event.lot = lot
        event.user = request.user
        event.save()

        if lot.parent_stock:
            stock = lot.parent_stock
            if stock.remaining_volume >= lot.volume:
                stock.remaining_volume = round(stock.remaining_volume - lot.volume, 2)
                stock.remaining_weight = stock.get_weight()
                stock.remaining_lhv_amount = stock.get_lhv_amount()
                stock.save()
                event = CarbureStockEvent()
                event.event_type = CarbureStockEvent.SPLIT
                event.stock = stock
                event.user = request.user
                event.metadata = {'message': 'Envoi lot.', 'volume_to_deduct': lot.volume}
            else:
                return JsonResponse({'status': 'error', 'message': 'Available volume lower than lot volume'}, status=400)

        lot.lot_status = CarbureLot.PENDING

        #### SPECIFIC CASES
        # I AM NEITHER THE SUPPLIER NOR THE CLIENT
        # create two transactions. unknown producer/supplier -> me and me -> client
        if lot.carbure_supplier != entity and lot.carbure_client != entity:
            # AUTO ACCEPT FIRST TRANSACTION
            final_client = lot.carbure_client
            nb_auto_accepted += 1
            lot.lot_status = CarbureLot.ACCEPTED
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
            lot.vendor_certificate = ''
            lot.vendor_certificate_type = ''
            lot.lot_status = CarbureLot.PENDING
            lot.save()
            event = CarbureLotEvent()
            event.event_type = CarbureLotEvent.ACCEPTED
            event.lot = lot
            event.user = request.user
            event.save()
        elif lot.carbure_client_id is None:
            # RFC or EXPORT
            nb_auto_accepted += 1
            lot.lot_status = CarbureLot.ACCEPTED
            event = CarbureLotEvent()
            event.event_type = CarbureLotEvent.ACCEPTED
            event.lot = lot
            event.user = request.user
            event.save()
        else:
            pass
        lot.save()
    return JsonResponse({'status': 'success', 'data': {'submitted': nb_lots, 'sent': nb_sent, 'auto-accepted': nb_auto_accepted, 'ignored': nb_ignored, 'rejected': nb_rejected}})


@check_user_rights(role=[UserRights.RW, UserRights.ADMIN])
def lots_delete(request, *args, **kwargs):
    context = kwargs['context']
    entity_id = context['entity_id']
    status = request.POST.get('status', None)
    lots = get_entity_lots_by_status(entity_id, status)
    filtered_lots = filter_lots(lots, request.POST, entity_id)
    if filtered_lots.count() == 0:
        return JsonResponse({'status': 'error', 'message': 'Could not find lots to delete'}, status=400)
    for lot in filtered_lots:
        if lot.added_by_id != int(entity_id):
            return JsonResponse({'status': 'forbidden', 'message': 'Entity not authorized to delete this lot'}, status=403)

        if lot.lot_status not in [CarbureLot.DRAFT, CarbureLot.PENDING, CarbureLot.REJECTED]:
            # cannot delete lot accepted / frozen or already deleted
            return JsonResponse({'status': 'error', 'message': 'Cannot delete lot'}, status=400)

        event = CarbureLotEvent()
        event.event_type = CarbureLotEvent.DELETED
        event.lot = lot
        event.user = request.user
        event.save()
        lot.lot_status = CarbureLot.DELETED
        lot.save()
    return JsonResponse({'status': 'success'})



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
        .values('period') \
        .annotate(count=Count('id', distinct=True))
    lots_by_period = {}
    for period_lot in period_lots:
        lots_by_period[str(period_lot['period'])] = period_lot['count']

    pending_period_lots = CarbureLot.objects.filter(period__in=periods) \
        .filter(Q(carbure_client_id=entity_id) | Q(carbure_supplier_id=entity_id)) \
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
    lots = get_entity_lots_by_status(entity_id, status)
    lots = filter_lots(lots, request.POST, entity_id)

    entity = Entity.objects.get(pk=entity_id)
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

@check_user_rights(role=[UserRights.RW, UserRights.ADMIN])
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

        if lot.lot_status == CarbureLot.REJECTED:
            lot.lot_status = CarbureLot.PENDING
            lot.correction_status = CarbureLot.NO_PROBLEMO
        else:
            lot.correction_status = CarbureLot.FIXED
        lot.save()

        event = CarbureLotEvent()
        event.event_type = CarbureLotEvent.MARKED_AS_FIXED
        event.lot = lot
        event.user = request.user
        event.save()
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
                c.update_sustainability_data(lot)
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
                    c.update_sustainability_data(lot)
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

    lots = get_entity_lots_by_status(entity_id, status)
    lots = filter_lots(lots, request.POST, entity_id, will_aggregate=True)

    for lot in lots.iterator():
        notify_sender = False

        if int(entity_id) != lot.carbure_client_id:
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
        lot.correction_status = CarbureLot.IN_CORRECTION
        lot.carbure_client = None
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

@check_user_rights(role=[UserRights.RW, UserRights.ADMIN])
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
        lot.correction_status = CarbureLot.NO_PROBLEMO
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


@check_user_rights(role=[UserRights.RW, UserRights.ADMIN])
def accept_rfc(request, *args, **kwargs):
    context = kwargs['context']
    entity_id = context['entity_id']
    status = request.POST.get('status', False)

    lots = get_entity_lots_by_status(entity_id, status)
    lots = filter_lots(lots, request.POST, entity_id, will_aggregate=True)

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

    lots = get_entity_lots_by_status(entity_id, status)
    lots = filter_lots(lots, request.POST, entity_id, will_aggregate=True)

    entity = Entity.objects.get(pk=entity_id)
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

    lots = get_entity_lots_by_status(entity_id, status)
    lots = filter_lots(lots, request.POST, entity_id, will_aggregate=True)

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

    lots = get_entity_lots_by_status(entity_id, status)
    lots = filter_lots(lots, request.POST, entity_id, will_aggregate=True)

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
def accept_processing(request, *args, **kwargs):
    context = kwargs['context']
    entity_id = context['entity_id']
    status = request.POST.get('status', False)
    processing_entity_id = request.POST.get('processing_entity_id', False)

    entity = Entity.objects.get(pk=entity_id)
    processing_entity = Entity.objects.get(pk=processing_entity_id)

    lots = get_entity_lots_by_status(entity_id, status)
    lots = filter_lots(lots, request.POST, entity_id, will_aggregate=True)

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

    if not client_entity_id and not unknown_client:
        return JsonResponse({'status': 'error', 'message': 'Please specify either client_entity_id or unknown_client'}, status=400)

    if not certificate:
        return JsonResponse({'status': 'error', 'message': 'Please specify a certificate'}, status=400)

    lots = get_entity_lots_by_status(entity_id, status)
    lots = filter_lots(lots, request.POST, entity_id, will_aggregate=True)

    entity = Entity.objects.get(pk=entity_id)
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
        declaration, _ = SustainabilityDeclaration.objects.get_or_create(entity_id=entity_id, period=period_d)
    except:
        return JsonResponse({'status': 'error', 'message': 'Could not parse period.'}, status=400)

    # ensure everything is in order
    pending_reception = CarbureLot.objects.filter(carbure_client=declaration.entity, period=period_int, lot_status__in=[CarbureLot.DRAFT, CarbureLot.PENDING]).count()
    if pending_reception > 0:
        return JsonResponse({'status': 'error', 'message': 'Cannot validate declaration. Some lots are pending reception.'}, status=400)
    pending_correction = CarbureLot.objects.filter(carbure_client=declaration.entity, period=period_int, lot_status__in=[CarbureLot.ACCEPTED], correction_status__in=[CarbureLot.IN_CORRECTION, CarbureLot.FIXED]).count()
    if pending_correction > 0:
        return JsonResponse({'status': 'error', 'message': 'Cannot validate declaration. Some accepted lots need correction.'}, status=400)
    lots_sent_rejected_or_drafts = CarbureLot.objects.filter(carbure_supplier=declaration.entity, period=period_int, lot_status__in=[CarbureLot.DRAFT, CarbureLot.REJECTED]).count()
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
        declaration, _ = SustainabilityDeclaration.objects.get_or_create(entity_id=entity_id, period=period_d)
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