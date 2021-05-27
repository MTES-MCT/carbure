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
from api.v3.sanity_checks import bulk_sanity_checks, generic_error
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
    year = request.GET.get('year', False)

    try:
        if year:
            year = int(year)
            date_from = datetime.date(year=year, month=1, day=1)
            date_until = datetime.date(year=year, month=12, day=31)
        else:
            today = datetime.date.today()
            date_from = today.replace(month=1, day=1)
            date_until = today.replace(month=12, day=31)
    except Exception:
        return JsonResponse({'status': 'error', 'message': 'Incorrect format for year. Expected YYYY'}, status=400)

    try:
        auditees = UserRights.objects.filter(user=request.user, role=UserRights.AUDITOR).values_list('entity')

        txs = LotTransaction.objects.filter(delivery_date__gte=date_from, delivery_date__lte=date_until).filter(
            Q(carbure_vendor__id__in=auditees) | Q(carbure_client__id__in=auditees))

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
