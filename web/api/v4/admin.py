import traceback
from django.db.models.aggregates import Count, Sum
from django.db.models.expressions import F
from django.db.models.functions.comparison import Coalesce

from django.http.response import JsonResponse
from django.db.models.query_utils import Q
from core.decorators import is_admin
from api.v4.helpers import filter_lots, get_entity_lots_by_status, get_lot_comments, get_lot_errors, get_lot_updates, get_lots_with_errors, get_lots_with_metadata, get_lots_filters_data, get_stock_events
from api.v4.helpers import get_transaction_distance

from core.models import CarbureLot, CarbureLotComment, CarbureStock, CarbureStockTransformation, Entity, GenericError
from core.serializers import CarbureLotPublicSerializer, CarbureStockPublicSerializer, CarbureStockTransformationPublicSerializer


@is_admin
def get_years(request, *args, **kwargs):
    data_lots = CarbureLot.objects.values_list('year', flat=True).distinct()
    data_transforms = CarbureStockTransformation.objects.values_list('transformation_dt__year', flat=True).distinct()
    data = set(list(data_transforms) + list(data_lots))
    return JsonResponse({'status': 'success', 'data': list(data)})


@is_admin
def get_snapshot(request, *args, **kwargs):
    year = request.GET.get('year', False)
    entity_id = request.GET.get('entity_id', False)
    if year:
        try:
            year = int(year)
        except Exception:
            return JsonResponse({'status': 'error', 'message': 'Incorrect format for year. Expected YYYY'}, status=400)
    else:
        return JsonResponse({'status': 'error', 'message': 'Missing year'}, status=400)

    data = {}
    entity = Entity.objects.get(id=entity_id)
    lots = CarbureLot.objects.filter(year=year).exclude(lot_status__in=[CarbureLot.DRAFT, CarbureLot.DELETED])
    alerts = get_lots_with_errors(lots, entity)
    corrections = lots.exclude(correction_status=CarbureLot.NO_PROBLEMO)
    # declarations = lots.exclude(lot_status__in=[CarbureLot.DRAFT, CarbureLot.DELETED])
    pinned = lots.filter(highlighted_by_admin=True)

    data['lots'] = {'alerts': alerts.count(),
                    'corrections': corrections.count(),
                    'declarations': lots.count(),
                    'pinned': pinned.count()}
    return JsonResponse({'status': 'success', 'data': data})


@is_admin
def get_lots(request, *args, **kwargs):
    status = request.GET.get('status', False)
    selection = request.GET.get('selection', False)
    entity_id = request.GET.get('entity_id', False)
    if not status and not selection:
        return JsonResponse({'status': 'error', 'message': 'Missing status'}, status=400)
    try:
        entity = Entity.objects.get(id=entity_id)
        lots = get_admin_lots_by_status(entity, status)
        return get_lots_with_metadata(lots, entity, request.GET)
    except Exception:
        traceback.print_exc()
        return JsonResponse({'status': 'error', 'message': "Could not get lots"}, status=400)


@is_admin
def get_lots_summary(request, *args, **kwargs):
    status = request.GET.get('status', False)
    short = request.GET.get('short', False)
    entity_id = request.GET.get('entity_id', False)
    if not status:
        return JsonResponse({'status': 'error', 'message': 'Missing status'}, status=400)
    try:
        entity = Entity.objects.get(id=entity_id)
        lots = get_admin_lots_by_status(entity, status)
        lots = filter_lots(lots, request.GET, entity, will_aggregate=True)
        summary = get_admin_summary_data(lots, short == 'true')
        return JsonResponse({'status': 'success', 'data': summary})
    except Exception:
        traceback.print_exc()
        return JsonResponse({'status': 'error', 'message': "Could not get lots summary"}, status=400)


@is_admin
def get_lot_details(request, *args, **kwargs):
    lot_id = request.GET.get('lot_id', False)
    entity_id = request.GET.get('entity_id', False)
    if not lot_id:
        return JsonResponse({'status': 'error', 'message': 'Missing lot_id'}, status=400)

    entity = Entity.objects.get(id=entity_id)
    lot = CarbureLot.objects.get(pk=lot_id)

    data = {}
    data['lot'] = CarbureLotPublicSerializer(lot).data
    data['parent_lot'] = CarbureLotPublicSerializer(lot.parent_lot).data if lot.parent_lot else None
    data['parent_stock'] = CarbureStockPublicSerializer(lot.parent_stock).data if lot.parent_stock else None
    data['children_lot'] = CarbureLotPublicSerializer(CarbureLot.objects.filter(parent_lot=lot), many=True).data
    data['children_stock'] = CarbureStockPublicSerializer(CarbureStock.objects.filter(parent_lot=lot), many=True).data
    data['distance'] = get_transaction_distance(lot)
    data['errors'] = get_lot_errors(lot, entity)
    #data['certificates'] = check_certificates(tx)
    data['updates'] = get_lot_updates(lot)
    data['comments'] = get_lot_comments(lot)
    return JsonResponse({'status': 'success', 'data': data})


@is_admin
def get_stock_details(request, *args, **kwargs):
    stock_id = request.GET.get('stock_id', False)
    if not stock_id:
        return JsonResponse({'status': 'error', 'message': 'Missing stock_id'}, status=400)

    stock = CarbureStock.objects.get(pk=stock_id)

    data = {}
    data['stock'] = CarbureStockPublicSerializer(stock).data
    data['parent_lot'] = CarbureLotPublicSerializer(stock.parent_lot).data if stock.parent_lot else None
    data['parent_transformation'] = CarbureStockTransformationPublicSerializer(stock.parent_transformation).data if stock.parent_transformation else None
    data['children_lot'] = CarbureLotPublicSerializer(CarbureLot.objects.filter(parent_stock=stock), many=True).data
    data['children_transformation'] = CarbureStockTransformationPublicSerializer(CarbureStockTransformation.objects.filter(source_stock=stock), many=True).data
    data['events'] = get_stock_events(stock.parent_lot)
    data['updates'] = get_lot_updates(stock.parent_lot)
    data['comments'] = get_lot_comments(stock.parent_lot)
    return JsonResponse({'status': 'success', 'data': data})


@is_admin
def get_lots_filters(request, *args, **kwargs):
    status = request.GET.get('status', False)
    field = request.GET.get('field', False)
    entity_id = request.GET.get('entity_id', False)
    if not field:
        return JsonResponse({'status': 'error', 'message': 'Please specify the field for which you want the filters'}, status=400)
    entity = Entity.objects.get(id=entity_id)
    lots = get_admin_lots_by_status(entity, status)
    data = get_lots_filters_data(lots, request.GET, entity, field)
    if data is None:
        return JsonResponse({'status': 'error', 'message': "Could not find specified filter"}, status=400)
    else:
        return JsonResponse({'status': 'success', 'data': data})


@is_admin
def add_comment(request, *args, **kwargs):
    entity_id = request.POST.get('entity_id', False)
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


@is_admin
def toggle_warning(request, *args, **kwargs):
    lot_id = request.POST.get('lot_id')
    error = request.POST.get('error')
    try:
        lot_error = GenericError.objects.get(lot_id=lot_id, error=error)
    except:
        traceback.print_exc()
        return JsonResponse({'status': "error", 'message': "Could not locate wanted lot or error"}, status=404)
    try:
        lot_error.acked_by_admin = not lot_error.acked_by_admin
        lot_error.save()
        return JsonResponse({'status': "success"})
    except:
        traceback.print_exc()
        return JsonResponse({'status': "error", 'message': "Could not update warning"}, status=500)


def get_admin_lots_by_status(entity, status):
    lots = CarbureLot.objects.select_related(
        'carbure_producer', 'carbure_supplier', 'carbure_client', 'added_by',
        'carbure_production_site', 'carbure_production_site__producer', 'carbure_production_site__country', 'production_country',
        'carbure_dispatch_site', 'carbure_dispatch_site__country', 'dispatch_site_country',
        'carbure_delivery_site', 'carbure_delivery_site__country', 'delivery_site_country',
        'feedstock', 'biofuel', 'country_of_origin',
        'parent_lot', 'parent_stock', 'parent_stock__carbure_client', 'parent_stock__carbure_supplier',
        'parent_stock__feedstock', 'parent_stock__biofuel', 'parent_stock__depot', 'parent_stock__country_of_origin', 'parent_stock__production_country'
    ).prefetch_related('genericerror_set', 'carbure_production_site__productionsitecertificate_set')

    lots = lots.exclude(lot_status__in=[CarbureLot.DRAFT, CarbureLot.DELETED])

    if status == 'ALERTS':
        lots = get_lots_with_errors(lots, entity, will_aggregate=True)
    elif status == 'CORRECTIONS':
        lots = lots.exclude(correction_status=CarbureLot.NO_PROBLEMO)
    elif status == 'DECLARATIONS':
        lots = lots.exclude(lot_status__in=[CarbureLot.DRAFT, CarbureLot.DELETED])
    elif status == 'PINNED':
        lots = lots.filter(highlighted_by_admin=True)

    return lots


def get_admin_summary_data(lots, short=False):
    data = {'count': lots.count(), 'total_volume': lots.aggregate(Sum('volume'))['volume__sum'] or 0}

    if short:
        return data

    pending_filter = Q(lot_status__in=[CarbureLot.PENDING, CarbureLot.REJECTED]) | Q(correction_status__in=[CarbureLot.IN_CORRECTION, CarbureLot.FIXED])

    lots = lots.annotate(
        supplier=Coalesce('carbure_supplier__name', 'unknown_supplier'),
        client=Coalesce('carbure_client__name', 'unknown_client'),
        biofuel_code=F('biofuel__code')
    ).values(
        'supplier',
        'client',
        'biofuel_code',
        'delivery_type'
    ).annotate(
        volume_sum=Sum('volume'),
        avg_ghg_reduction=Sum(F('volume') * F('ghg_reduction')) / Sum('volume'),
        total=Count('id'),
        pending=Count('id', filter=pending_filter)
    ).distinct().order_by()

    data['lots'] = list(lots)
    return data
