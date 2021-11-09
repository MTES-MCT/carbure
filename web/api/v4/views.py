import traceback

from django.http.response import JsonResponse
from core.decorators import check_user_rights
from api.v4.helpers import get_entity_lots_by_status, get_lots_with_metadata, get_lots_filters
from core.models import CarbureLot, CarbureStock


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
    lots_in_accepted = lots_in.filter(lot_status__in=[CarbureLot.ACCEPTED, CarbureLot.FROZEN])
    lots_in_tofix = lots_in.exclude(correction_status=CarbureLot.NO_PROBLEMO)
    stock = CarbureStock.objects.filter(carbure_client_id=entity_id, remaining_volume__gt=0)
    lots_out = lots.filter(carbure_supplier_id=entity_id)
    lots_out_pending = lots_out.filter(lot_status=CarbureLot.PENDING)
    lots_out_accepted = lots_out.filter(lot_status__in=[CarbureLot.ACCEPTED, CarbureLot.FROZEN])
    lots_out_tofix = lots_out.exclude(correction_status=CarbureLot.NO_PROBLEMO)
    data['lots'] = {'draft': drafts.count(),
                    'in_total': lots_in.count(), 'in_pending': lots_in_pending.count(), 'in_accepted': lots_in_accepted.count(), 'in_tofix': lots_in_tofix.count(),
                    'stock': stock.count(),
                    'out_total': lots_out.count(), 'out_pending': lots_out_pending.count(), 'out_accepted': lots_out_accepted.count(), 'out_tofix': lots_out_tofix.count()}
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


def get_stock(request):
    pass


def get_details(request):
    pass


@check_user_rights()
def get_filters(request, *args, **kwargs):
    context = kwargs['context']
    entity_id = context['entity_id']
    status = request.GET.get('status', False)
    field = request.GET.get('field', False)
    if not field:
        return JsonResponse({'status': 'error', 'message': 'Please specify the field for which you want the filters'}, status=400)
    txs = get_entity_lots_by_status(entity_id, status)
    data = get_lots_filters(txs, request.GET, entity_id, field)
    if data is None:
        return JsonResponse({'status': 'error', 'message': "Could not find specified filter"}, status=400)
    else:
        return JsonResponse({'status': 'success', 'data': data})
