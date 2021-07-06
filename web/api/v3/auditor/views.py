import logging
from django.db.models import Q, Count
from django.http import JsonResponse
from core.common import check_certificates

from core.models import LotTransaction
from core.models import UserRights
from core.decorators import check_rights
from api.v3.lots.helpers import filter_lots, get_lots_with_metadata, get_snapshot_filters, get_errors, get_general_summary, get_comments, get_history, get_current_deadline, get_year_bounds, get_lots_with_errors, sort_lots


logger = logging.getLogger(__name__)


def get_auditees(user):
    return UserRights.objects.filter(user=user, role=UserRights.AUDITOR).values_list('entity')


def get_lots_by_status(txs, querySet):
    status = querySet.get('status', None)
    hidden = querySet.get('is_hidden_by_auditor', None)

    if status == 'alert':
        txs = get_lots_with_errors(txs)
    elif status == 'correction':
        txs = txs.filter(delivery_status__in=['AC', 'R', 'AA'])
    elif status == 'declaration':
        txs = txs.filter(delivery_status__in=['A', 'N', 'F'])
    elif status == 'highlight':
        txs = txs.filter(highlighted_by_auditor=True)

    if hidden is None:
        txs = txs.filter(hidden_by_auditor=False)

    return txs


def get_audited_lots(auditees):
    return LotTransaction.objects.filter(Q(carbure_vendor__id__in=auditees) | Q(carbure_client__id__in=auditees) | Q(lot__added_by__in=auditees))


@check_rights('entity_id')
def get_lots(request, *args, **kwargs):
    status = request.GET.get('status', False)

    if not status:
        return JsonResponse({'status': 'error', 'message': "Please provide a status"}, status=400)

    try:
        auditees = get_auditees(request.user)

        txs = get_audited_lots(auditees)
        txs = txs.filter(lot__status='Validated')
        txs = get_lots_by_status(txs, request.GET)
        txs = filter_lots(txs, request.GET)[0]
        return get_lots_with_metadata(txs, None, request.GET, admin=True)
    except Exception:
        return JsonResponse({'status': 'error', 'message': "Something went wrong"}, status=400)


@check_rights('entity_id')
def get_filters(request, *args, **kwargs):
    field = request.GET.get('field', False)
    if not field:
        return JsonResponse({'status': 'error', 'message': "Missing field"}, status=400)

    auditees = get_auditees(request.user)
    txs = get_audited_lots(auditees)
    txs = get_lots_by_status(txs, request.GET)
    txs = filter_lots(txs, request.GET, [field])[0]
    d = get_snapshot_filters(txs, None, [field])
    if field in d:
        values = d[field]
    else:
        return JsonResponse({'status': 'error', 'message': "Something went wrong"}, status=400)
    return JsonResponse({'status': 'success', 'data': values})


@check_rights('entity_id')
def get_lots_summary(request, *args, **kwargs):
    auditees = get_auditees(request.user)
    txs = get_audited_lots(auditees)

    try:
        txs = get_lots_by_status(txs, request.GET)
        txs = filter_lots(txs, request.GET)[0]
        txs = sort_lots(txs, request.GET)
        data = get_general_summary(txs)
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
    data['transaction'] = tx.natural_key(admin=True)
    data['errors'] = get_errors(tx)
    data['comments'] = get_comments(tx)
    data['updates'] = get_history(tx)
    data['deadline'] = get_current_deadline()
    data['certificates'] = check_certificates(tx)

    return JsonResponse({'status': 'success', 'data': data})


@check_rights('entity_id')
def get_snapshot(request, *args, **kwargs):
    year = request.GET.get('year', False)

    try:
        date_from, date_until = get_year_bounds(year)
    except Exception:
        return JsonResponse({'status': 'error', 'message': 'Incorrect format for year. Expected YYYY'}, status=400)

    try:
        auditees = get_auditees(request.user)

        txs = get_audited_lots(auditees)
        txs = txs.filter(delivery_date__gte=date_from, delivery_date__lte=date_until)

        years = [t.year for t in txs.dates('delivery_date', 'year', order='DESC')]

        lots = {}
        lots['alert'] = txs.annotate(Count('genericerror')).filter(genericerror__count__gt=0).count()
        lots['correction'] = txs.filter(delivery_status__in=['AC', 'AA', 'R']).count()
        lots['declaration'] = txs.filter(delivery_status__in=['A', 'N', 'F']).count()
        lots['highlight'] = txs.filter(highlighted_by_auditor=True).count()

        filters = [
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
            'is_mac',
            'is_hidden_by_auditor',
            'client_types'
        ]
        data = {'lots': lots, 'filters': filters, 'years': years}
        return JsonResponse({'status': 'success', 'data': data})
    except Exception:
        return JsonResponse({'status': 'error', 'message': 'Failed building snapshot'}, status=400)


@check_rights('entity_id')
def highlight_transactions(request, *args, **kwargs):
    tx_ids = request.POST.getlist('tx_ids', False)
    notify_admin = request.POST.get('notify_admin', False)

    if not tx_ids:
        return JsonResponse({'status': 'forbidden', 'message': "Missing tx_ids"}, status=400)

    txs = LotTransaction.objects.filter(id__in=tx_ids)

    for tx in txs.iterator():
        tx.highlighted_by_auditor = not tx.highlighted_by_auditor
        if notify_admin == 'true':
            tx.highlighted_by_admin = True
        tx.save()

    return JsonResponse({'status': 'success'})

@check_rights('entity_id')
def hide_transactions(request, *args, **kwargs):
    tx_ids = request.POST.getlist('tx_ids', False)

    if not tx_ids:
        return JsonResponse({'status': 'forbidden', 'message': "Missing tx_ids"}, status=400)

    txs = LotTransaction.objects.filter(id__in=tx_ids)

    for tx in txs.iterator():
        tx.hidden_by_auditor = not tx.hidden_by_auditor
        tx.save()

    return JsonResponse({'status': 'success'})