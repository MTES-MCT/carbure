import traceback

from django.http.response import JsonResponse
from core.decorators import check_user_rights
from api.v4.helpers import get_entity_lots_by_status, get_lots_with_metadata
from core.models import CarbureLot, CarbureStock

@check_user_rights
def get_snapshot(request, *args, **kwargs):
    context = kwargs['context']
    entity = context['entity']
    year = request.GET.get('year', False)
    if year:
        try:
            year = int(year)
        except Exception:
            return JsonResponse({'status': 'error', 'message': 'Incorrect format for year. Expected YYYY'}, status=400)

    lots = CarbureLot.objects.filter(year=year)
    data = {}
    drafts = lots.filter(added_by=entity, lot_status=CarbureLot.DRAFT).count()
    lots_in = lots.filter(carbure_client=entity, lot_status__in=[CarbureLot.PENDING, CarbureLot.ACCEPTED, CarbureLot.FROZEN])
    lots_in_tofix = lots_in.exclude(correction_status=CarbureLot.NO_PROBLEMO).count()
    stock = CarbureStock.objects.filter(carbure_client=entity, remaining_volume__gt=0).count()
    lots_out = lots.filter(carbure_supplier=entity, lot_status__in=[CarbureLot.PENDING, CarbureLot.ACCEPTED, CarbureLot.FROZEN])
    lots_out_tofix = lots_out.exclude(correction_status=CarbureLot.NO_PROBLEMO).count()
    data['lots'] = {'draft': drafts, 'in': lots_in.count(), 'in_tofix': lots_in_tofix, 'stock': stock, 'out': lots_out.count(), 'out_tofix': lots_out_tofix}
    base_filters = [
        'periods',
        'biocarburants',
        'matieres_premieres',
        'countries_of_origin',
        'production_sites',
        'delivery_sites',
        'suppliers',
        'clients'
    ]
    data['filters'] = base_filters
    return JsonResponse({'status': 'success', 'data': data})


@check_user_rights
def get_lots(request, *args, **kwargs):
    context = kwargs['context']
    entity = context['entity']
    status = request.GET.get('status', False)
    if not status:
        return JsonResponse({'status': 'error', 'message': 'Missing status'}, status=400)
    try:
        lots = get_entity_lots_by_status(entity, status)
        return get_lots_with_metadata(lots, entity, request.GET)
    except Exception as e:
        traceback.print_exc()
        return JsonResponse({'status': 'error', 'message': "Could not get lots"}, status=400)

def get_stock(request):
    pass

def get_details(request):
    pass

