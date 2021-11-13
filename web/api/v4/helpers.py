import datetime
import calendar
from dateutil.relativedelta import relativedelta
from django.db.models.aggregates import Count
from django.db.models.expressions import OuterRef, Subquery
from django.db.models.functions.comparison import Coalesce
from django.db.models.query_utils import Q
from django.http.response import HttpResponse, JsonResponse
from core.models import Biocarburant, CarbureLot, MatierePremiere, Pays
from core.models import GenericError
from core.serializers import CarbureLotPublicSerializer
from core.xlsx_v3 import export_carbure_lots


sort_key_to_django_field = {'period': 'period',
                            'feedstock': 'feedstock__name',
                            'ghg_reduction': 'ghg_reduction',
                            'volume': 'volume',
                            'country_of_origin': 'country_of_origin__name',
                            'added_by': 'added_by__name'}


def get_entity_lots_by_status(entity_id, status):
    if status not in ['DRAFTS', 'IN', 'OUT']:
        raise Exception('Unknown status %s' % (status))
    lots = CarbureLot.objects.select_related(
        'carbure_producer', 'carbure_supplier', 'carbure_client', 'added_by',
        'carbure_production_site', 'carbure_production_site__producer', 'carbure_production_site__country', 'production_country',
        'carbure_dispatch_site', 'carbure_dispatch_site__country', 'dispatch_site_country',
        'carbure_delivery_site', 'carbure_delivery_site__country', 'delivery_site_country',
        'feedstock', 'biofuel', 'country_of_origin',
        'parent_lot', 'parent_stock', 'parent_stock__carbure_client', 'parent_stock__carbure_supplier',
    ).prefetch_related('genericerror_set', 'carbure_production_site__productionsitecertificate_set')
    if status == 'DRAFTS':
        lots = lots.filter(carbure_supplier_id=entity_id, lot_status=CarbureLot.DRAFT)
    elif status == 'IN':
        lots = lots.filter(carbure_client_id=entity_id, lot_status__in=[CarbureLot.PENDING, CarbureLot.ACCEPTED, CarbureLot.FROZEN])
    elif status == 'OUT':
        lots = lots.filter(carbure_supplier_id=entity_id, lot_status__in=[CarbureLot.PENDING, CarbureLot.ACCEPTED, CarbureLot.FROZEN])
    else:
        raise Exception('Unknown status')
    return lots


def get_lots_with_metadata(lots, entity_id, querySet, is_admin=False):
    export = querySet.get('export', False)
    limit = querySet.get('limit', None)
    from_idx = querySet.get('from_idx', "0")

    # filtering
    lots, total_errors, total_deadline, deadline_str, tx_with_errors = filter_lots(lots, querySet, entity_id)
    # sorting
    lots = sort_lots(lots, querySet)

    # pagination
    from_idx = int(from_idx)
    returned = lots[from_idx:]
    if limit is not None:
        limit = int(limit)
        returned = returned[:limit]

    # enrich dataset with additional metadata
    serializer = CarbureLotPublicSerializer(returned, many=True)
    data = {}
    data['lots'] = serializer.data
    data['total'] = lots.count()
    data['total_errors'] = total_errors
    data['returned'] = returned.count()
    data['from'] = from_idx
    data['errors'] = {lot.id: lot.errors for lot in tx_with_errors}
    data['deadlines'] = {'date': deadline_str, 'total': total_deadline}

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


def get_lots_with_errors(lots, entity_id=None):
    if entity_id is None:
        filter = Q(tx=OuterRef('pk'))
    else:
        filter = Q(tx=OuterRef('pk')) & (Q(lot__added_by_id=entity_id, display_to_creator=True) | Q(lot__carbure_client_id=entity_id, display_to_recipient=True))
    tx_errors = GenericError.objects.filter(filter).values('lot').annotate(errors=Count('id')).values('errors')
    return lots.annotate(errors=Subquery(tx_errors)).filter(errors__gt=0)


def get_lots_with_deadline(lots, deadline):
    affected_date = deadline - relativedelta(months=1)
    lots_with_deadline = lots.filter(lot_status=CarbureLot.DRAFT, delivery_date__year=affected_date.year, delivery_date__month=affected_date.month)
    return lots_with_deadline


def filter_lots(lots, querySet, entity_id=None, blacklist=[]):
    year = querySet.get('year', False)
    periods = querySet.getlist('periods')
    production_sites = querySet.getlist('production_sites')
    delivery_sites = querySet.getlist('delivery_sites')
    feedstocks = querySet.getlist('feedstocks')
    countries_of_origin = querySet.getlist('countries_of_origin')
    biofuels = querySet.getlist('biofuels')
    clients = querySet.getlist('clients')
    suppliers = querySet.getlist('suppliers')
    correction_statuses = querySet.getlist('correction_statuses')
    delivery_types = querySet.getlist('delivery_types')
    errors = querySet.getlist('errors')
    query = querySet.get('query', False)
    is_highlighted_by_admin = querySet.get('is_highlighted_by_admin', None)
    is_highlighted_by_auditor = querySet.get('is_highlighted_by_auditor', None)
    selection = querySet.getlist('selection')

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

    if query and 'query' not in blacklist:
        lots = lots.filter(
            Q(feedstock__name__icontains=query) |
            Q(biofuel__name__icontains=query) |
            Q(carbure_producer__name__icontains=query) |
            Q(unknown_producer__icontains=query) |
            Q(carbure_id__icontains=query) |
            Q(country_of_origin__name__icontains=query) |
            Q(carbure_client__name__icontains=query) |
            Q(unknown_client__icontains=query) |
            Q(carbure_delivery_site__name__icontains=query) |
            Q(unknown_delivery_site__icontains=query) |
            Q(free_field__icontains=query) |
            Q(transport_document_reference__icontains=query) |
            Q(production_site_double_counting_certificate__icontains=query)
        )

    invalid = querySet.get('invalid', False)
    deadline = querySet.get('deadline', False)

    deadline_date = get_current_deadline()
    deadline_str = deadline_date.strftime("%Y-%m-%d")

    tx_with_errors = get_lots_with_errors(lots, entity_id)
    tx_with_deadline = get_lots_with_deadline(lots, deadline_date)

    total_errors = tx_with_errors.count()
    total_deadline = tx_with_deadline.count()

    if invalid == 'true':
        lots = tx_with_errors
    elif deadline == 'true' and 'deadline' not in blacklist:
        lots = tx_with_deadline
    return lots, total_errors, total_deadline, deadline_str, tx_with_errors


def sort_lots(lots, querySet):
    sort_by = querySet.get('sort_by', False)
    order = querySet.get('order', False)

    if not sort_by:
        lots = lots.order_by('-id')
    elif sort_by in sort_key_to_django_field:
        key = sort_key_to_django_field[sort_by]
        if order == 'desc':
            lots = lots.order_by('-%s' % key)
        else:
            lots = lots.order_by(key)
    elif sort_by == 'biocarburant':
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
    elif sort_by == 'vendor':
        lots = lots.annotate(vendor=Coalesce('carbure_supplier__name', 'unknown_supplier'))
        if order == 'desc':
            lots = lots.order_by('-vendor')
        else:
            lots = lots.order_by('vendor')
    return lots


def normalize_filter(list, value=None, label=None):
    if value is None:
        return [{'value': item, 'label': item} for item in list if item]
    if label is None:
        return [{'value': item[value], 'label': item[value]} for item in list if item]
    else:
        return [{'value': item[value], 'label': item[label]} for item in list if item]


def get_lots_filters(lots, querySet, entity_id, field):
    lots = filter_lots(lots, querySet, entity_id=entity_id, blacklist=[field])[0]

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
