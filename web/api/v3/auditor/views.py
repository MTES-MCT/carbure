import datetime
import calendar
import logging
import unicodedata
from dateutil.relativedelta import *
from django.db.models import Q, F, Case, When, Count
from django.db.models.functions import TruncMonth
from django.db.models.functions import Extract
from django.db.models.fields import NOT_PROVIDED
from django import db
from django.http import JsonResponse, HttpResponse
from django.db import transaction

from core.models import LotV2, LotTransaction, EntityDepot
from core.models import Entity, UserRights, MatierePremiere, Biocarburant, Pays, TransactionComment, SustainabilityDeclaration
from core.xlsx_v3 import template_producers_simple, template_producers_advanced, template_operators, template_traders
from core.xlsx_v3 import export_transactions
from core.common import validate_lots, load_excel_file, get_prefetched_data, check_duplicates, send_rejection_emails
from api.v3.sanity_checks import bulk_sanity_checks
from django_otp.decorators import otp_required
from core.decorators import check_rights
from api.v3.lots.helpers import get_entity_lots_by_status, get_lots_with_metadata, get_snapshot_filters, get_errors, get_summary, filter_entity_transactions

logger = logging.getLogger(__name__)


@check_rights('entity_id')
def get_lots(request, *args, **kwargs):
    context = kwargs['context']
    entity = context['entity']

    status = request.GET.get('status', False)
    
    if not status:
        return JsonResponse({'status': 'error', 'message': 'Missing status'}, status=400)

    try:
        txs = get_entity_lots_by_status(entity, status)
        return get_lots_with_metadata(txs, entity, request.GET)
    except Exception:
        return JsonResponse({'status': 'error', 'message': "Could not get lots"}, status=400)


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
    context = kwargs['context']
    entity = context['entity']
    tx_id = request.GET.get('tx_id', False)

    if not tx_id:
        return JsonResponse({'status': 'error', 'message': 'Missing tx_id'}, status=400)

    tx = LotTransaction.objects.get(pk=tx_id)

    if tx.carbure_client != entity and tx.carbure_vendor != entity and tx.lot.added_by != entity:
        return JsonResponse({'status': 'forbidden', 'message': "User not allowed"}, status=403)

    now = datetime.datetime.now()
    (_, last_day) = calendar.monthrange(now.year, now.month)
    deadline_date = now.replace(day=last_day)

    data = {}
    data['transaction'] = tx.natural_key()
    data['errors'] = get_errors(tx)
    data['deadline'] = deadline_date.strftime("%Y-%m-%d")
    data['comments'] = []
    for c in tx.transactioncomment_set.all():
        comment = c.natural_key()
        if c.entity not in [tx.lot.added_by, tx.carbure_client]:
            comment['entity'] = {'name': 'Anonyme'}
        data['comments'].append(comment)

    return JsonResponse({'status': 'success', 'data': data})

@check_rights('entity_id')
def get_snapshot(request, *args, **kwargs):
    context = kwargs['context']
    entity = context['entity']
    data = {}
    year = request.GET.get('year', False)
    today = datetime.date.today()
    date_from = today.replace(month=1, day=1)
    date_until = today.replace(month=12, day=31)
    if year:
        try:
            year = int(year)
            date_from = datetime.date(year=year, month=1, day=1)
            date_until = datetime.date(year=year, month=12, day=31)
        except Exception:
            return JsonResponse({'status': 'error', 'message': 'Incorrect format for year. Expected YYYY'}, status=400)

    if entity.entity_type == 'Producteur' or entity.entity_type == 'Trader':
        txs = LotTransaction.objects.filter(carbure_vendor=entity)
        data['years'] = [t.year for t in txs.dates('delivery_date', 'year', order='DESC')]
        txs = txs.filter(delivery_date__gte=date_from).filter(delivery_date__lte=date_until)
        draft = txs.filter(lot__status='Draft', lot__parent_lot=None).count()
        validated = txs.filter(lot__status='Validated', delivery_status__in=['N', 'AA']).count()
        tofix = txs.filter(lot__status='Validated', delivery_status__in=['AC', 'R']).count()
        accepted = txs.filter(lot__status='Validated', delivery_status='A').count()
        data['lots'] = {'draft': draft, 'validated': validated, 'tofix': tofix, 'accepted': accepted}
    elif entity.entity_type == 'Opérateur':
        txs = LotTransaction.objects.filter(Q(carbure_client=entity) | Q(lot__added_by=entity, is_mac=True))
        data['years'] = [t.year for t in txs.dates('delivery_date', 'year', order='DESC')]
        txs = txs.filter(delivery_date__gte=date_from).filter(delivery_date__lte=date_until)
        draft = txs.filter(lot__added_by=entity, lot__status='Draft').count()
        ins = txs.filter(lot__status='Validated', delivery_status__in=['N', 'AA', 'AC'], is_mac=False).count()
        accepted = txs.filter(lot__status='Validated', delivery_status='A').count()
        data['lots'] = {'draft': draft, 'accepted': accepted, 'in': ins}
    else:
        return JsonResponse({'status': 'error', 'message': "Unknown entity_type"}, status=400)

    filters = get_snapshot_filters(txs)

    if entity.entity_type == 'Producteur':
        c1 = [c['carbure_client__name'] for c in txs.values('carbure_client__name').distinct()]
        c2 = [c['unknown_client'] for c in txs.values('unknown_client').distinct()]
        clients = [c for c in c1 + c2 if c]
        filters['clients'] = clients
    elif entity.entity_type == 'Opérateur':
        v1 = [v['carbure_vendor__name'] for v in txs.values('carbure_vendor__name').distinct()]
        v2 = [v['lot__unknown_supplier'] for v in txs.values('lot__unknown_supplier').distinct()]
        vendors = [v for v in v1 + v2 if v]
        filters['vendors'] = vendors

    data['filters'] = filters

    depots = [d.natural_key() for d in EntityDepot.objects.filter(entity=entity)]
    data['depots'] = depots

    return JsonResponse({'status': 'success', 'data': data})
