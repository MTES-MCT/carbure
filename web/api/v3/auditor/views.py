import logging
from django.db.models import Q, Count
from django.http import JsonResponse

from core.models import LotTransaction
from core.models import UserRights
from core.decorators import check_rights
from api.v3.lots.helpers import get_lots_with_metadata, get_snapshot_filters, get_errors, get_summary, filter_entity_transactions, get_comments, get_history, get_current_deadline, get_year_bounds, get_lots_with_errors


logger = logging.getLogger(__name__)


@check_rights('entity_id')
def get_lots(request, *args, **kwargs):
    status = request.GET.get('status', False)

    if not status:
        return JsonResponse({'status': 'error', 'message': "Please provide a status"}, status=400)

    try:
        auditees = UserRights.objects.filter(user=request.user, role=UserRights.AUDITOR).values_list('entity')

        txs = LotTransaction.objects.filter(Q(carbure_vendor__id__in=auditees) | Q(carbure_client__id__in=auditees) | Q(lot__added_by__in=auditees))
        txs = txs.filter(lot__status='Validated')

        if status == 'alert':
            txs = get_lots_with_errors(txs)
        elif status == 'correction':
            txs = txs.filter(delivery_status__in=['AC', 'R', 'AA'])
        elif status == 'declaration':
            txs = txs.filter(delivery_status__in=['A', 'N'])

        return get_lots_with_metadata(txs, None, request.GET)

    except Exception:
        return JsonResponse({'status': 'error', 'message': "Something went wrong"}, status=400)


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
    except Exception:
        return JsonResponse({'status': 'error', 'message': "Could not get lots summary"}, status=400)


@check_rights('entity_id')
def get_details(request, *args, **kwargs):
    tx_id = request.GET.get('tx_id', False)

    if not tx_id:
        return JsonResponse({'status': 'error', 'message': 'Missing tx_id'}, status=400)

    tx = LotTransaction.objects.get(pk=tx_id)
    rights = UserRights.objects.filter(user=request.user, role=UserRights.AUDITOR, entity__in=(tx.carbure_vendor, tx.carbure_client, tx.lot.added_by))

    if rights.count() == 0:
        return JsonResponse({'status': 'forbidden', 'message': "User not allowed"}, status=403)

    data = {}
    data['transaction'] = tx.natural_key()
    data['errors'] = get_errors(tx)
    data['comments'] = get_comments(tx)
    data['updates'] = get_history(tx)
    data['deadline'] = get_current_deadline()

    return JsonResponse({'status': 'success', 'data': data})


@check_rights('entity_id')
def get_snapshot(request, *args, **kwargs):
    year = request.GET.get('year', False)

    try:
        date_from, date_until = get_year_bounds(year)
    except Exception:
        return JsonResponse({'status': 'error', 'message': 'Incorrect format for year. Expected YYYY'}, status=400)

    try:
        auditees = UserRights.objects.filter(user=request.user, role=UserRights.AUDITOR).values_list('entity')

        txs = LotTransaction.objects.filter(delivery_date__gte=date_from, delivery_date__lte=date_until).filter(
            Q(carbure_vendor__id__in=auditees) | Q(carbure_client__id__in=auditees) | Q(lot__added_by__in=auditees))

        years = [t.year for t in txs.dates('delivery_date', 'year', order='DESC')]

        lots = {}
        lots['alert'] = txs.annotate(Count('genericerror')).filter(genericerror__count__gt=0).count()
        lots['correction'] = txs.filter(delivery_status__in=['AC', 'AA', 'R']).count()
        lots['declaration'] = txs.filter(delivery_status__in=['A', 'N']).count()

        filters = get_snapshot_filters(txs, [
            'delivery_status',
            'periods',
            'biocarburants',
            'matieres_premieres',
            'countries_of_origin',
            'vendors',
            'clients',
            'production_sites',
            'delivery_sites',
            'added_by',
            'errors',
            'is_forwarded',
            'is_mac'
        ])

        data = {'lots': lots, 'filters': filters, 'years': years}
        return JsonResponse({'status': 'success', 'data': data})
    except Exception:
        return JsonResponse({'status': 'error', 'message': 'Failed building snapshot'}, status=400)
