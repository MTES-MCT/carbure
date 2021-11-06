import traceback

from django.http.response import JsonResponse
from core.decorators import check_user_rights
from api.v4.helpers import get_entity_lots_by_status, get_lots_with_metadata

def get_snapshot(request):
    pass

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

