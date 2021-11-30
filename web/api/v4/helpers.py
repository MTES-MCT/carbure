import os
import datetime
import calendar
import time
from multiprocessing.context import Process
from dateutil.relativedelta import relativedelta
from django.db.models.aggregates import Count, Sum
from django.db.models.expressions import F, OuterRef, Subquery
from django.db.models.functions.comparison import Coalesce
from django.db.models.query_utils import Q
from django.http.response import HttpResponse, JsonResponse
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from certificates.models import DoubleCountingRegistration

from core.ign_distance import get_distance
from core.models import Biocarburant, CarbureLot, CarbureLotComment, CarbureLotEvent, CarbureStock, CarbureStockEvent, CarbureStockTransformation, Depot, Entity, EntityCertificate, EntityDepot, GenericCertificate, MatierePremiere, Pays, TransactionDistance, UserRights
from core.models import GenericError
from core.serializers import CarbureLotCommentSerializer, CarbureLotEventSerializer, CarbureLotPublicSerializer, CarbureStockEventSerializer, CarbureStockPublicSerializer, GenericErrorSerializer
from core.xlsx_v3 import export_carbure_lots, export_carbure_stock
from producers.models import ProductionSite


sort_key_to_django_field = {'period': 'delivery_date',
                            'feedstock': 'feedstock__name',
                            'ghg_reduction': 'ghg_reduction',
                            'volume': 'volume',
                            'country_of_origin': 'country_of_origin__name',
                            'added_by': 'added_by__name'}

stock_sort_key_to_django_field = {'feedstock': 'feedstock__name',
                                  'ghg_reduction': 'ghg_reduction',
                                  'volume': 'remaining_volume',
                                  'country_of_origin': 'country_of_origin__name'}


def get_entity_stock(entity_id):
    return CarbureStock.objects.filter(carbure_client_id=entity_id) \
        .select_related('parent_lot', 'parent_transformation',
                        'biofuel', 'feedstock', 'country_of_origin',
                        'depot', 'depot__country',
                        'carbure_production_site', 'carbure_production_site__country', 'production_country',
                        'carbure_client', 'carbure_supplier')


def get_entity_lots_by_status(entity_id, status=None):
    lots = CarbureLot.objects.select_related(
        'carbure_producer', 'carbure_supplier', 'carbure_client', 'added_by',
        'carbure_production_site', 'carbure_production_site__producer', 'carbure_production_site__country', 'production_country',
        'carbure_dispatch_site', 'carbure_dispatch_site__country', 'dispatch_site_country',
        'carbure_delivery_site', 'carbure_delivery_site__country', 'delivery_site_country',
        'feedstock', 'biofuel', 'country_of_origin',
        'parent_lot', 'parent_stock', 'parent_stock__carbure_client', 'parent_stock__carbure_supplier',
        'parent_stock__feedstock', 'parent_stock__biofuel', 'parent_stock__depot', 'parent_stock__country_of_origin', 'parent_stock__production_country'
    ).prefetch_related('genericerror_set', 'carbure_production_site__productionsitecertificate_set')
    if status == 'DRAFTS':
        lots = lots.filter(added_by_id=entity_id, lot_status=CarbureLot.DRAFT)
    elif status == 'IN':
        lots = lots.filter(carbure_client_id=entity_id, lot_status__in=[CarbureLot.PENDING, CarbureLot.ACCEPTED, CarbureLot.FROZEN])
    elif status == 'OUT':
        lots = lots.filter(carbure_supplier_id=entity_id, lot_status__in=[CarbureLot.PENDING, CarbureLot.ACCEPTED, CarbureLot.FROZEN])
    elif status == 'DECLARATION':
        lots = lots.filter(Q(carbure_supplier_id=entity_id) | Q(carbure_client_id=entity_id)).exclude(lot_status__in=[CarbureLot.DRAFT, CarbureLot.DELETED])
    else:
        lots = lots.filter(Q(added_by_id=entity_id) | Q(carbure_supplier_id=entity_id) | Q(carbure_client_id=entity_id))
    return lots


def get_lots_with_metadata(lots, entity_id, query, is_admin=False):
    export = query.get('export', False)
    limit = query.get('limit', None)
    from_idx = query.get('from_idx', "0")

    # filtering
    lots = filter_lots(lots, query, entity_id)
    # sorting
    lots = sort_lots(lots, query)

    # pagination
    from_idx = int(from_idx)
    returned = lots[from_idx:]
    if limit is not None:
        limit = int(limit)
        returned = returned[:limit]

    total_errors, total_deadline = count_lots_of_interest(lots, entity_id)

    # enrich dataset with additional metadata
    serializer = CarbureLotPublicSerializer(returned, many=True)
    data = {}
    data['lots'] = serializer.data
    data['from'] = from_idx
    data['returned'] = returned.count()
    data['total'] = lots.count()
    data['total_errors'] = total_errors
    data['total_deadline'] = total_deadline
    data['errors'] = get_lots_errors(returned, entity_id)
    data['ids'] = list(lots.values_list('id', flat=True))

    if not export:
        return JsonResponse({'status': 'success', 'data': data})
    else:
        file_location = export_carbure_lots(entity_id, returned)
        with open(file_location, "rb") as excel:
            data = excel.read()
            ctype = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            response = HttpResponse(content=data, content_type=ctype)
            response['Content-Disposition'] = 'attachment; filename="%s"' % (file_location)
        return response


def get_errors(lot, entity_id=None, is_admin=False):
    if is_admin:
        return [e.natural_key() for e in lot.genericerror_set.all()]
    elif entity_id == lot.added_by_id:
        return [e.natural_key() for e in lot.genericerror_set.filter(display_to_creator=True)]
    elif entity_id == lot.carbure_client_id:
        return [e.natural_key() for e in lot.genericerror_set.filter(display_to_recipient=True)]
    else:
        return [e.natural_key() for e in lot.genericerror_set.filter(display_to_creator=True)]


def get_current_deadline():
    now = datetime.datetime.now()
    (_, last_day) = calendar.monthrange(now.year, now.month)
    deadline_date = now.replace(day=last_day)
    return deadline_date


def get_comments(tx):
    comments = []
    for c in tx.transactioncomment_set.all():
        comment = c.natural_key()
        comments.append(comment)
    return comments


def get_history(tx):
    return [c.natural_key() for c in tx.transactionupdatehistory_set.all().order_by('-datetime')]


def get_stock_with_errors(stock, entity_id=None):
    if entity_id is None:
        filter = Q(lot=OuterRef('pk'))
    else:
        filter = Q(lot=OuterRef('pk')) & (Q(parent_lot__added_by_id=entity_id, display_to_creator=True) | Q(parent_lot__carbure_client_id=entity_id, display_to_recipient=True))
    tx_errors = GenericError.objects.filter(filter).values('lot').annotate(errors=Count('id')).values('errors')
    return stock.annotate(errors=Subquery(tx_errors)).filter(errors__gt=0)


def get_lots_with_errors(lots, entity_id, will_aggregate=False):
    if will_aggregate:
        # use a subquery so we can later do aggregations on this queryset without wrecking the results
        if entity_id is not None:
            filter = Q(lot__added_by_id=entity_id, display_to_creator=True) | Q(lot__carbure_client_id=entity_id, display_to_recipient=True)
        tx_errors = GenericError.objects.filter(lot=OuterRef('pk')).filter(filter).values('lot').annotate(errors=Count('id')).values('errors')
        return lots.annotate(errors=Subquery(tx_errors)).filter(errors__gt=0)
    else:
        if entity_id is not None:
            filter = Q(added_by_id=entity_id, genericerror__display_to_creator=True) | Q(carbure_client_id=entity_id, genericerror__display_to_recipient=True)
        return lots.annotate(errors=Count('genericerror', filter=filter)).filter(errors__gt=0)


def get_lots_with_deadline(lots, deadline=get_current_deadline()):
    affected_date = deadline - relativedelta(months=1)
    period = affected_date.year * 100 + affected_date.month
    return lots.filter(period=period, lot_status__in=[CarbureLot.DRAFT, CarbureLot.REJECTED, CarbureLot.PENDING])


def filter_lots(lots, query, entity_id=None, will_aggregate=False, blacklist=[]):
    year = query.get('year', False)
    periods = query.getlist('periods', [])
    production_sites = query.getlist('production_sites', [])
    delivery_sites = query.getlist('delivery_sites', [])
    feedstocks = query.getlist('feedstocks', [])
    countries_of_origin = query.getlist('countries_of_origin', [])
    biofuels = query.getlist('biofuels', [])
    clients = query.getlist('clients', [])
    suppliers = query.getlist('suppliers', [])
    correction_statuses = query.getlist('correction_statuses', [])
    delivery_types = query.getlist('delivery_types', [])
    errors = query.getlist('errors', [])
    search = query.get('query', False)
    is_highlighted_by_admin = query.get('is_highlighted_by_admin', None)
    is_highlighted_by_auditor = query.get('is_highlighted_by_auditor', None)
    selection = query.getlist('selection', [])
    history = query.get('history', False)
    correction = query.get('correction', False)

    if history != 'true':
        lots = lots.exclude(lot_status__in=[CarbureLot.FROZEN, CarbureLot.ACCEPTED])
    if correction == 'true':
        lots = lots.filter(Q(correction_status__in=[CarbureLot.IN_CORRECTION, CarbureLot.FIXED]) | Q(lot_status=CarbureLot.REJECTED))
    if year and 'year' not in blacklist:
        lots = lots.filter(year=year)
    if len(selection) > 0:
        lots = lots.filter(pk__in=selection)
    if len(periods) > 0 and 'periods' not in blacklist:
        lots = lots.filter(period__in=periods)
    if len(production_sites) > 0 and 'production_sites' not in blacklist:
        lots = lots.filter(Q(carbure_production_site__name__in=production_sites) | Q(unknown_production_site__in=production_sites))
    if len(feedstocks) > 0 and 'feedstocks' not in blacklist:
        lots = lots.filter(feedstock__code__in=feedstocks)
    if len(biofuels) > 0 and 'biofuels' not in blacklist:
        lots = lots.filter(biofuel__code__in=biofuels)
    if len(countries_of_origin) > 0 and 'countries_of_origin' not in blacklist:
        lots = lots.filter(country_of_origin__code_pays__in=countries_of_origin)
    if len(delivery_sites) > 0 and 'delivery_sites' not in blacklist:
        lots = lots.filter(Q(carbure_delivery_site__name__in=delivery_sites) | Q(unknown_delivery_site__in=delivery_sites))
    if len(clients) > 0 and 'clients' not in blacklist:
        lots = lots.filter(Q(carbure_client__name__in=clients) | Q(unknown_client__in=clients))
    if len(suppliers) > 0 and 'suppliers' not in blacklist:
        lots = lots.filter(Q(carbure_supplier__name__in=suppliers) | Q(unknown_supplier__in=suppliers))
    if len(delivery_types) > 0 and 'delivery_types' not in blacklist:
        lots = lots.filter(delivery_type__in=delivery_types)
    if len(correction_statuses) > 0 and 'correction_statuses' not in blacklist:
        lots = lots.filter(correction_status__in=correction_statuses)

    if is_highlighted_by_admin is not None and 'is_highlighted_by_admin' not in blacklist:
        if is_highlighted_by_admin == 'true':
            lots = lots.filter(highlighted_by_admin=True)
        else:
            lots = lots.filter(highlighted_by_admin=False)
    if is_highlighted_by_auditor is not None and 'is_highlighted_by_auditor' not in blacklist:
        if is_highlighted_by_auditor == 'true':
            lots = lots.filter(is_highlighted_by_auditor=True)
        else:
            lots = lots.filter(is_highlighted_by_auditor=False)

    if len(errors) > 0 and 'errors' not in blacklist:
        lots = lots.filter(genericerror__error__in=errors)

    if search and 'query' not in blacklist:
        lots = lots.filter(
            Q(feedstock__name__icontains=search) |
            Q(biofuel__name__icontains=search) |
            Q(carbure_producer__name__icontains=search) |
            Q(unknown_producer__icontains=search) |
            Q(carbure_id__icontains=search) |
            Q(country_of_origin__name__icontains=search) |
            Q(carbure_client__name__icontains=search) |
            Q(unknown_client__icontains=search) |
            Q(carbure_delivery_site__name__icontains=search) |
            Q(unknown_delivery_site__icontains=search) |
            Q(free_field__icontains=search) |
            Q(transport_document_reference__icontains=search) |
            Q(production_site_double_counting_certificate__icontains=search)
        )

    invalid = query.get('invalid', False)
    deadline = query.get('deadline', False)

    if invalid == 'true':
        lots = get_lots_with_errors(lots, entity_id, will_aggregate)
    if deadline == 'true':
        lots = get_lots_with_deadline(lots)
    return lots


def count_lots_of_interest(lots, entity_id):
    error_lots = get_lots_with_errors(lots, entity_id)
    deadline_lots = get_lots_with_deadline(lots)
    return error_lots.count(), deadline_lots.count()


def sort_lots(lots, query):
    sort_by = query.get('sort_by', False)
    order = query.get('order', False)

    if not sort_by:
        lots = lots.order_by('-id')
    elif sort_by in sort_key_to_django_field:
        key = sort_key_to_django_field[sort_by]
        if order == 'desc':
            lots = lots.order_by('-%s' % key)
        else:
            lots = lots.order_by(key)
    elif sort_by == 'biofuel':
        if order == 'desc':
            lots = lots.order_by('-biofuel__name', '-volume')
        else:
            lots = lots.order_by('biofuel__name', 'volume')
    elif sort_by == 'client':
        lots = lots.annotate(client=Coalesce('carbure_client__name', 'unknown_client'))
        if order == 'desc':
            lots = lots.order_by('-client')
        else:
            lots = lots.order_by('client')
    elif sort_by == 'supplier':
        lots = lots.annotate(vendor=Coalesce('carbure_supplier__name', 'unknown_supplier'))
        if order == 'desc':
            lots = lots.order_by('-supplier')
        else:
            lots = lots.order_by('supplier')
    return lots


def normalize_filter(list, value=None, label=None):
    if value is None:
        return [{'value': item, 'label': item} for item in list if item]
    if label is None:
        return [{'value': item[value], 'label': item[value]} for item in list if item]
    else:
        return [{'value': item[value], 'label': item[label]} for item in list if item]


def get_lots_filters_data(lots, query, entity_id, field):
    lots = filter_lots(lots, query, entity_id=entity_id, blacklist=[field])

    if field == 'feedstocks':
        feedstocks = MatierePremiere.objects.filter(id__in=lots.values('feedstock__id').distinct()).values('code', 'name')
        return normalize_filter(feedstocks, 'code', 'name')

    if field == 'biofuels':
        biofuels = Biocarburant.objects.filter(id__in=lots.values('biofuel__id').distinct()).values('code', 'name')
        return normalize_filter(biofuels, 'code', 'name')

    if field == 'countries_of_origin':
        countries = Pays.objects.filter(id__in=lots.values('country_of_origin').distinct()).values('code_pays', 'name')
        return normalize_filter(countries, 'code_pays', 'name')

    if field == 'periods':
        periods = lots.values('period').distinct()
        return [{'value': str(v['period']), 'label': "%d-%02d" % (v['period']/100, v['period'] % 100)} for v in periods if v]

    if field == 'production_sites':
        production_sites = []
        for item in lots.values('carbure_production_site__name', 'unknown_production_site').distinct():
            if item['carbure_production_site__name'] not in ('', None):
                production_sites.append(item['carbure_production_site__name'])
            elif item['unknown_production_site'] not in ('', None):
                production_sites.append(item['unknown_production_site'])
        return normalize_filter(set(production_sites))

    if field == 'delivery_sites':
        delivery_sites = []
        for item in lots.values('carbure_delivery_site__name', 'unknown_delivery_site').distinct():
            if item['carbure_delivery_site__name'] not in ('', None):
                delivery_sites.append(item['carbure_delivery_site__name'])
            elif item['unknown_delivery_site'] not in ('', None):
                delivery_sites.append(item['unknown_delivery_site'])
        return normalize_filter(set(delivery_sites))

    if field == 'clients':
        clients = []
        for item in lots.values('carbure_client__name', 'unknown_client').distinct():
            if item['carbure_client__name'] not in ('', None):
                clients.append(item['carbure_client__name'])
            elif item['unknown_client'] not in ('', None):
                clients.append(item['unknown_client'])
        return normalize_filter(set(clients))

    if field == 'suppliers':
        suppliers = []
        for item in lots.values('carbure_supplier__name', 'unknown_supplier').distinct():
            if item['carbure_supplier__name'] not in ('', None):
                suppliers.append(item['carbure_supplier__name'])
            elif item['unknown_supplier'] not in ('', None):
                suppliers.append(item['unknown_supplier'])
        return normalize_filter(set(suppliers))

    if field == 'errors':
        generic_errors = lots.values('genericerror__error').distinct()
        return normalize_filter(generic_errors, 'genericerror__error')

    if field == 'added_by':
        added_by = lots.values('added_by__name').distinct()
        return normalize_filter(added_by, 'added_by__name')

def get_stock_filters_data(stock, query, entity_id, field):
    stock = filter_stock(stock, query, entity_id=entity_id, blacklist=[field])

    if field == 'feedstocks':
        feedstocks = MatierePremiere.objects.filter(id__in=stock.values('feedstock__id').distinct()).values('code', 'name')
        return normalize_filter(feedstocks, 'code', 'name')

    if field == 'biofuels':
        biofuels = Biocarburant.objects.filter(id__in=stock.values('biofuel__id').distinct()).values('code', 'name')
        return normalize_filter(biofuels, 'code', 'name')

    if field == 'countries_of_origin':
        countries = Pays.objects.filter(id__in=stock.values('country_of_origin').distinct()).values('code_pays', 'name')
        return normalize_filter(countries, 'code_pays', 'name')

    if field == 'periods':
        periods = stock.filter(parent_lot__isnull=False).values('parent_lot__period').distinct()
        return [{'value': str(v['parent_lot__period']), 'label': "%d-%02d" % (v['parent_lot__period']/100, v['parent_lot__period'] % 100)} for v in periods if v]

    if field == 'depots':
        depots = Depot.objects.filter(id__in=stock.values('depot__id').distinct()).values('name', 'depot_id')
        return normalize_filter(depots, 'name')

    if field == 'suppliers':
        suppliers = []
        for item in stock.values('carbure_supplier__name', 'unknown_supplier').distinct():
            if item['carbure_supplier__name'] not in ('', None):
                suppliers.append(item['carbure_supplier__name'])
            elif item['unknown_supplier'] not in ('', None):
                suppliers.append(item['unknown_supplier'])
        return normalize_filter(set(suppliers))

    if field == 'production_sites':
        production_sites = []
        for item in stock.values('carbure_production_site__name', 'unknown_production_site').distinct():
            if item['carbure_production_site__name'] not in ('', None):
                production_sites.append(item['carbure_production_site__name'])
            elif item['unknown_production_site'] not in ('', None):
                production_sites.append(item['unknown_production_site'])
        return normalize_filter(set(production_sites))


def get_stock_with_metadata(stock, entity_id, query, is_admin=False):
    export = query.get('export', False)
    limit = query.get('limit', None)
    from_idx = query.get('from_idx', "0")

    # filtering
    stock = filter_stock(stock, query, entity_id)
    # sorting
    stock = sort_stock(stock, query)

    # pagination
    from_idx = int(from_idx)
    returned = stock[from_idx:]
    if limit is not None:
        limit = int(limit)
        returned = returned[:limit]

    # enrich dataset with additional metadata
    serializer = CarbureStockPublicSerializer(returned, many=True)
    data = {}
    data['stocks'] = serializer.data
    data['total'] = stock.count()
    data['returned'] = returned.count()
    data['from'] = from_idx
    data['ids'] = list(stock.values_list('id', flat=True))

    if not export:
        return JsonResponse({'status': 'success', 'data': data})
    else:
        file_location = export_carbure_stock(entity_id, returned)
        with open(file_location, "rb") as excel:
            data = excel.read()
            ctype = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            response = HttpResponse(content=data, content_type=ctype)
            response['Content-Disposition'] = 'attachment; filename="%s"' % (file_location)
        return response


def filter_stock(stock, query, entity_id=None, blacklist=[]):
    year = query.get('year', False)
    periods = query.getlist('periods', [])
    depots = query.getlist('depots', [])
    feedstocks = query.getlist('feedstocks', [])
    countries_of_origin = query.getlist('countries_of_origin', [])
    biofuels = query.getlist('biofuels', [])
    suppliers = query.getlist('suppliers', [])
    production_sites = query.getlist('production_sites', [])
    search = query.get('query', False)
    selection = query.getlist('selection', [])
    history = query.get('history', False)

    if history != 'true':
        stock = stock.filter(remaining_volume__gt=0)
    if year and 'year' not in blacklist:
        stock = stock.filter(Q(parent_lot__year=year) | Q(parent_transformation__transformation_dt__year=year))
    if len(selection) > 0:
        stock = stock.filter(pk__in=selection)
    if len(periods) > 0 and 'periods' not in blacklist:
        stock = stock.filter(parent_lot__period__in=periods)
    if len(feedstocks) > 0 and 'feedstocks' not in blacklist:
        stock = stock.filter(feedstock__code__in=feedstocks)
    if len(biofuels) > 0 and 'biofuels' not in blacklist:
        stock = stock.filter(biofuel__code__in=biofuels)
    if len(countries_of_origin) > 0 and 'countries_of_origin' not in blacklist:
        stock = stock.filter(country_of_origin__code_pays__in=countries_of_origin)
    if len(depots) > 0 and 'depots' not in blacklist:
        stock = stock.filter(depot__name__in=depots)
    if len(suppliers) > 0 and 'suppliers' not in blacklist:
        stock = stock.filter(Q(carbure_supplier__name__in=suppliers) | Q(unknown_supplier__in=suppliers))
    if len(production_sites) > 0 and 'production_sites' not in blacklist:
        stock = stock.filter(Q(carbure_production_site__name__in=production_sites) | Q(unknown_production_site__in=production_sites))
    if search and 'query' not in blacklist:
        stock = stock.filter(
            Q(feedstock__name__icontains=search) |
            Q(biofuel__name__icontains=search) |
            Q(carbure_id__icontains=search) |
            Q(country_of_origin__name__icontains=search) |
            Q(depot__name__icontains=search) |
            Q(parent_lot__free_field__icontains=search) |
            Q(parent_lot__transport_document_reference__icontains=search)
        )
    return stock


def sort_stock(stock, query):
    sort_by = query.get('sort_by', False)
    order = query.get('order', False)

    if not sort_by:
        stock = stock.order_by('-id')
    elif sort_by in stock_sort_key_to_django_field:
        key = sort_key_to_django_field[sort_by]
        if order == 'desc':
            stock = stock.order_by('-%s' % key)
        else:
            stock = stock.order_by(key)
    elif sort_by == 'biofuel':
        if order == 'desc':
            stock = stock.order_by('-biofuel__name', '-remaining_volume')
        else:
            stock = stock.order_by('biofuel__name', 'remaining_volume')
    elif sort_by == 'vendor':
        stock = stock.annotate(vendor=Coalesce('carbure_supplier__name', 'unknown_supplier'))
        if order == 'desc':
            stock = stock.order_by('-vendor')
        else:
            stock = stock.order_by('vendor')
    return stock

def get_lot_errors(lot, entity_id):
    errors = []
    if entity_id == str(lot.carbure_supplier_id):
        errors = lot.genericerror_set.filter(display_to_creator=True)
    elif entity_id == str(lot.carbure_client_id):
        errors = lot.genericerror_set.filter(display_to_recipient=True)
    else:
        errors = lot.genericerror_set.all()
    return GenericErrorSerializer(errors, many=True, read_only=True).data

def get_lots_errors(lots, entity_id):
    lot_ids = list(lots.values_list('id', flat=True))
    errors = GenericError.objects.filter(lot_id__in=lot_ids)
    if entity_id is not None:
        errors = errors.filter(Q(lot__added_by_id=entity_id, display_to_creator=True) | Q(lot__carbure_client_id=entity_id, display_to_recipient=True))
    data = {}
    for error in errors.values('lot_id', 'error', 'is_blocking', 'field', 'value', 'extra', 'fields').iterator():
        if error['lot_id'] not in data:
            data[error['lot_id']] = []
        data[error['lot_id']].append(GenericErrorSerializer(error).data)
    return data

def get_lot_updates(lot, entity_id):
    if lot is None:
        return []
    return CarbureLotEventSerializer(lot.carburelotevent_set.all(), many=True).data

def get_stock_events(lot, entity_id):
    if lot is None:
        return []
    return CarbureStockEventSerializer(lot.carburelotevent_set.all(), many=True).data

def get_lot_comments(lot, entity_id):
    if lot is None:
        return []
    return CarbureLotCommentSerializer(lot.carburelotcomment_set.all(), many=True).data

def get_transaction_distance(lot):
    url_link = 'https://www.google.com/maps/dir/?api=1&origin=%s&destination=%s&travelmode=driving'
    res = {'distance': -1, 'link': '', 'error': None, 'source': None}

    if not lot.carbure_production_site:
        res['error'] = 'PRODUCTION_SITE_NOT_IN_CARBURE'
        return res
    if not lot.carbure_delivery_site:
        res['error'] = 'DELIVERY_SITE_NOT_IN_CARBURE'
        return res
    starting_point = lot.carbure_production_site.gps_coordinates
    delivery_point = lot.carbure_delivery_site.gps_coordinates
    if not starting_point:
        res['error'] = 'PRODUCTION_SITE_COORDINATES_NOT_IN_CARBURE'
        return res
    if not delivery_point:
        res['error'] = 'DELIVERY_SITE_COORDINATES_NOT_IN_CARBURE'
        return res
    try:
        td = TransactionDistance.objects.get(starting_point=starting_point, delivery_point=delivery_point)
        res['link'] = url_link % (starting_point, delivery_point)
        res['distance'] = td.distance
        res['source'] = 'DB'
        return res
    except:
        # not found, launch in background for next time
        p = Process(target=get_distance, args=(starting_point, delivery_point))
        p.start()
        res['error'] = 'DISTANCE_NOT_IN_CACHE'
        return res

def send_email_declaration_validated(declaration):
    email_subject = "Carbure - Votre Déclaration de Durabilité a été validée"
    cc = "carbure@beta.gouv.fr"
    text_message = """
    Bonjour,

    Votre Déclaration de Durabilité pour la période %s a bien été prise en compte.

    Merci,
    L'équipe CarbuRe
    """
    env = os.getenv('IMAGE_TAG', False)
    if env != 'prod':
        # send only to staff / superuser
        recipients = [r.user.email for r in UserRights.objects.filter(entity=declaration.entity, user__is_staff=True)]
    else:
        # PROD
        recipients = [r.user.email for r in UserRights.objects.filter(entity=declaration.entity, user__is_staff=False, user__is_superuser=False).exclude(role__in=[UserRights.AUDITOR, UserRights.RO])]

    msg = EmailMultiAlternatives(subject=email_subject, body=text_message, from_email=settings.DEFAULT_FROM_EMAIL, to=recipients, cc=cc)
    msg.send()

def send_email_declaration_invalidated(declaration):
    email_subject = "Carbure - Votre Déclaration de Durabilité a été annulée"
    cc = "carbure@beta.gouv.fr"
    text_message = """
    Bonjour,

    Votre Déclaration de Durabilité pour la période %s a bien été annulée.
    Vous pouvez désormais éditer ou demander des corrections sur les lots concernés avant de la soumettre une nouvelle fois.

    Merci,
    L'équipe CarbuRe
    """
    env = os.getenv('IMAGE_TAG', False)
    if env != 'prod':
        # send only to staff / superuser
        recipients = [r.user.email for r in UserRights.objects.filter(entity=declaration.entity, user__is_staff=True)]
    else:
        # PROD
        recipients = [r.user.email for r in UserRights.objects.filter(entity=declaration.entity, user__is_staff=False, user__is_superuser=False).exclude(role__in=[UserRights.AUDITOR, UserRights.RO])]

    msg = EmailMultiAlternatives(subject=email_subject, body=text_message, from_email=settings.DEFAULT_FROM_EMAIL, to=recipients, cc=cc)
    msg.send()


def get_lots_summary_data(lots, entity_id, short=False):
    data = {'count': lots.count(), 'total_volume': lots.aggregate(Sum('volume'))['volume__sum'] or 0}

    if short:
        return data

    pending_filter = Q(lot_status__in=[CarbureLot.PENDING, CarbureLot.REJECTED]) | Q(correction_status__in=[CarbureLot.IN_CORRECTION, CarbureLot.FIXED])

    lots_in = lots.filter(carbure_client_id=entity_id).annotate(
        supplier=Coalesce('carbure_supplier__name', 'unknown_supplier'),
        biofuel_code=F('biofuel__code')
    ).values(
        'supplier',
        'biofuel_code'
    ).annotate(
        volume_sum=Sum('volume'),
        avg_ghg_reduction=Sum(F('volume') * F('ghg_reduction')) / Sum('volume'),
        total=Count('id'),
        pending=Count('id', filter=pending_filter)
    ).order_by()

    lots_out = lots.filter(carbure_supplier=entity_id).exclude(carbure_client_id=entity_id).annotate(
        client=Coalesce('carbure_client__name', 'unknown_client'),
        biofuel_code=F('biofuel__code')
    ).values(
        'client',
        'biofuel_code'
    ).annotate(
        volume_sum=Sum('volume'),
        avg_ghg_reduction=Sum(F('volume') * F('ghg_reduction')) / Sum('volume'),
        total=Count('id'),
        pending=Count('id', filter=pending_filter)
    ).order_by()

    data['in'] = list(lots_in)
    data['out'] = list(lots_out)
    return data


def get_stocks_summary_data(stocks, entity_id, short=False):
    data = {
        'count': stocks.count(),
        'total_remaining_volume': stocks.aggregate(Sum('remaining_volume'))['remaining_volume__sum'] or 0
    }

    if short:
        return data

    stock_summary = stocks.filter(carbure_client_id=entity_id).annotate(
        supplier=Coalesce('carbure_supplier__name', 'unknown_supplier'),
        biofuel_code=F('biofuel__code')
    ).values(
        'supplier',
        'biofuel_code'
    ).annotate(
        # volume_sum=Sum('parent_lot__volume'),
        remaining_volume_sum=Sum('remaining_volume'),
        avg_ghg_reduction=Sum(F('remaining_volume') * F('ghg_reduction')) / Sum('remaining_volume'),
        total=Count('id'),
    ).order_by()

    # data['total_volume'] = stocks.aggregate(Sum('parent_lot__volume'))['parent_lot__volume__sum'] or 0,
    data['stock'] = list(stock_summary)
    return data


def handle_eth_to_etbe_transformation(user, stock, transformation):
    required_fields = ['volume_ethanol', 'volume_etbe', 'volume_denaturant', 'volume_etbe_eligible']
    for f in required_fields:
        if f not in transformation:
            return JsonResponse({'status': 'error', 'message': 'Could not find field %s' % (f)}, status=400)

    volume_ethanol = transformation['volume_ethanol']
    volume_etbe = transformation['volume_etbe']
    volume_denaturant = transformation['volume_denaturant']
    volume_etbe_eligible = transformation['volume_etbe_eligible']
    etbe = Biocarburant.objects.get(code='ETBE')

    # check if source stock is Ethanol
    if stock.biofuel.code != 'ETH':
        return JsonResponse({'status': 'error', 'message': 'Source stock is not Ethanol'}, status=400)

    volume_ethanol = round(float(volume_ethanol), 2)
    volume_etbe = round(float(volume_etbe), 2)
    volume_etbe_eligible = round(float(volume_etbe_eligible), 2)
    volume_denaturant = round(float(volume_denaturant), 2)


    # check available volume
    if stock.remaining_volume < volume_ethanol:
        return JsonResponse({'status': 'error', 'message': 'Volume Ethanol is higher than available volume'}, status=400)


    new_stock = stock.parent_lot
    new_stock.pk = None
    new_stock.biofuel = etbe
    new_stock.volume = volume_etbe
    new_stock.weight = new_stock.get_weight()
    new_stock.lhv_amount = new_stock.get_lhv_amount()
    new_stock.parent_lot = None
    new_stock.save()

    stock.remaining_volume = round(stock.remaining_volume - volume_ethanol)
    stock.remaining_weight = stock.get_weight()
    stock.remaining_lhv_amount = stock.get_lhv_amount()
    stock.save()

    cst = CarbureStockTransformation()
    cst.transformation_type = CarbureStockTransformation.ETH_ETBE
    cst.source_stock = stock
    cst.dest_stock = new_stock
    cst.volume_deducted_from_source = volume_ethanol
    cst.volume_destination = volume_etbe
    cst.transformed_by = user
    cst.entity = stock.carbure_client
    cst.metadata = {'volume_denaturant': volume_denaturant, 'volume_etbe_eligible': volume_etbe_eligible}
    cst.save()

    new_stock.parent_transformation = cst
    new_stock.carbure_id = '%sT%d' % (stock.carbure_id, new_stock.id)
    new_stock.save()

    # create events
    e = CarbureStockEvent()
    e.event_type = CarbureLotEvent.TRANSFORMED
    e.stock = stock
    e.user = user
    e.save()

def get_prefetched_data(entity=None):
    lastyear = datetime.date.today() - datetime.timedelta(days=365)
    d = {}
    d['countries'] = {p.code_pays: p for p in Pays.objects.all()}
    d['biofuels'] = {b.code: b for b in Biocarburant.objects.all()}
    d['feedstocks'] = {m.code: m for m in MatierePremiere.objects.all()}
    d['depots'] = {d.depot_id: d for d in Depot.objects.all()}
    d['depotsbyname'] = {d.name.upper(): d for d in d['depots'].values()}
    if entity:
        # get only my production sites
        d['my_production_sites'] = {ps.name.upper(): ps for ps in ProductionSite.objects.prefetch_related('productionsiteinput_set', 'productionsiteoutput_set', 'productionsitecertificate_set').filter(producer=entity)}
        # get all my linked certificates
        d['my_vendor_certificates'] = [c.certificate.certificate_id for c in EntityCertificate.objects.filter(entity=entity)]
    else:
        d['production_sites'] = {ps.name: ps for ps in ProductionSite.objects.prefetch_related('productionsiteinput_set', 'productionsiteoutput_set', 'productionsitecertificate_set').all()}
    entitydepots = dict()
    associated_depots = EntityDepot.objects.all()
    for obj in associated_depots:
        if obj.id in entitydepots:
            entitydepots[obj.id].append(obj.id)
        else:
            entitydepots[obj.id] = [obj.id]
    d['depotsbyentity'] = entitydepots
    d['clients'] = {c.id: c for c in Entity.objects.filter(entity_type__in=[Entity.PRODUCER, Entity.OPERATOR, Entity.TRADER])}
    d['certificates'] = {c.certificate_id.upper(): c for c in GenericCertificate.objects.filter(valid_until__gte=lastyear)}
    d['double_counting_certificates'] = {c.certificate_id: c for c in DoubleCountingRegistration.objects.all()}
    return d
