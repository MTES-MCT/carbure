from calendar import calendar
from datetime import datetime
import traceback

from django.http.response import JsonResponse
from core.decorators import check_user_rights
from api.v4.helpers import get_entity_lots_by_status, get_lot_comments, get_lot_errors, get_lot_updates, get_lots_with_metadata, get_lots_filters_data, get_entity_stock, get_stock_with_metadata, get_stock_filters_data, get_transaction_distance, get_errors
from core.models import CarbureLot, CarbureStock
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
    #lots_in_accepted = lots_in.filter(lot_status__in=[CarbureLot.ACCEPTED, CarbureLot.FROZEN])
    lots_in_tofix = lots_in.exclude(correction_status=CarbureLot.NO_PROBLEMO)
    stock = CarbureStock.objects.filter(carbure_client_id=entity_id)
    stock_not_empty = stock.filter(remaining_volume__gt=0)
    lots_out = lots.filter(carbure_supplier_id=entity_id)
    lots_out_pending = lots_out.filter(lot_status=CarbureLot.PENDING)
    #lots_out_accepted = lots_out.filter(lot_status__in=[CarbureLot.ACCEPTED, CarbureLot.FROZEN])
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
def get_details(request, *args, **kwargs):
    context = kwargs['context']
    entity_id = context['entity_id']
    lot_id = request.GET.get('lot_id', False)
    if not lot_id:
        return JsonResponse({'status': 'error', 'message': 'Missing lot_id'}, status=400)

    lot = CarbureLot.objects.get(pk=lot_id)
    if lot.carbure_client_id != entity_id and lot.carbure_supplier != entity_id:
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