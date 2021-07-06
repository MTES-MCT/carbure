import datetime
import calendar
from time import perf_counter
from dateutil.relativedelta import relativedelta
from django.db.models import Q, F, Count, Sum
from django.db.models.expressions import OuterRef, Subquery, Value
from django.db.models.functions import Coalesce
from django.http import JsonResponse, HttpResponse
from core.models import GenericError, LotV2, LotTransaction, MatierePremiere, Biocarburant, Pays, Entity
from core.xlsx_v3 import export_transactions


sort_key_to_django_field = {'period': 'lot__period',
                            'matiere_premiere': 'lot__matiere_premiere__name',
                            'ghg_reduction': 'lot__ghg_reduction',
                            'volume': 'lot__volume',
                            'pays_origine': 'lot__pays_origine__name',
                            'added_by': 'lot__added_by__name'}


def get_errors(tx):
    return [e.natural_key() for e in tx.genericerror_set.all()]


def get_current_deadline():
    now = datetime.datetime.now()
    (_, last_day) = calendar.monthrange(now.year, now.month)
    deadline_date = now.replace(day=last_day)
    return deadline_date


def get_comments(tx):
    comments = []
    for c in tx.transactioncomment_set.all():
        comment = c.natural_key()
        if c.entity not in [tx.lot.added_by, tx.carbure_vendor, tx.carbure_client]:
            comment['entity'] = {'name': 'Anonyme'}
        comments.append(comment)

    return comments


def get_history(tx):
    return [c.natural_key() for c in tx.transactionupdatehistory_set.all().order_by('-datetime')]


def get_year_bounds(year):
    if year:
        year = int(year)
        date_from = datetime.date(year=year, month=1, day=1)
        date_until = datetime.date(year=year, month=12, day=31)
    else:
        today = datetime.date.today()
        date_from = today.replace(month=1, day=1)
        date_until = today.replace(month=12, day=31)

    return date_from, date_until


def get_entity_lots_by_status(entity, status):
    if entity.entity_type in ('Producteur', 'Trader'):
        txs = LotTransaction.objects.select_related(
            'lot', 'lot__carbure_producer', 'lot__carbure_production_site', 'lot__carbure_production_site__country',
            'lot__unknown_production_country', 'lot__matiere_premiere', 'lot__biocarburant', 'lot__pays_origine', 'lot__added_by', 'lot__data_origin_entity',
            'carbure_vendor', 'carbure_client', 'carbure_delivery_site', 'unknown_delivery_site_country', 'carbure_delivery_site__country',
        ).prefetch_related('genericerror_set', 'lot__carbure_production_site__productionsitecertificate_set')

        txs = txs.filter(carbure_vendor=entity)

        # filter by status
        if status == 'draft':
            txs = txs.filter(lot__status='Draft', lot__parent_lot=None)
        elif status == 'validated':
            txs = txs.filter(lot__status='Validated', delivery_status__in=['N', 'AA'])
        elif status == 'tofix':
            txs = txs.filter(lot__status='Validated', delivery_status__in=['AC', 'R'])
        elif status == 'accepted':
            txs = txs.filter(lot__status='Validated', delivery_status__in=['A', 'F'])
        else:
            raise Exception('Unknown status')

    elif entity.entity_type == 'Opérateur':
        txs = LotTransaction.objects.select_related(
            'lot', 'lot__carbure_producer', 'lot__carbure_production_site', 'lot__carbure_production_site__country',
            'lot__unknown_production_country', 'lot__matiere_premiere', 'lot__biocarburant', 'lot__pays_origine', 'lot__added_by', 'lot__data_origin_entity',
            'carbure_vendor', 'carbure_client', 'carbure_delivery_site', 'unknown_delivery_site_country', 'carbure_delivery_site__country'
        ).prefetch_related('genericerror_set', 'lot__carbure_production_site__productionsitecertificate_set')

        # filter by status
        if status == 'draft':
            txs = txs.filter(Q(lot__added_by=entity, lot__status='Draft'))
        elif status == 'in':
            txs = txs.filter(Q(carbure_client=entity))
            txs = txs.filter(delivery_status__in=['N', 'AC', 'AA'], lot__status="Validated", is_mac=False)
        elif status == 'accepted':
            txs = txs.filter(Q(carbure_client=entity) | Q(lot__added_by=entity, is_mac=True))
            txs = txs.filter(lot__status='Validated', delivery_status__in=['A', 'F'])
        else:
            raise Exception('Unknown status')

    else:
        raise Exception('Unknown entity type')

    return txs


def get_lots_with_errors(txs):
    tx_errors = GenericError.objects.filter(tx=OuterRef('pk')).values('tx').annotate(errors=Count(Value(1))).values('errors')
    return txs.annotate(errors=Subquery(tx_errors)).filter(errors__gt=0)


def get_lots_with_deadline(txs, deadline):
    affected_date = deadline - relativedelta(months=1)
    txs_with_deadline = txs.filter(lot__status='Draft', delivery_date__year=affected_date.year, delivery_date__month=affected_date.month)
    return txs_with_deadline


def filter_by_entities(txs, entities):
    return txs.filter(
        Q(carbure_client__name__in=entities) |
        Q(unknown_client__in=entities) |
        Q(carbure_vendor__name__in=entities) |
        Q(lot__unknown_supplier__in=entities) |
        Q(lot__added_by__name__in=entities)
    )


def filter_lots(txs, querySet, blacklist=[]):
    is_forwarded = querySet.get('is_forwarded', None)
    is_mac = querySet.get('is_mac', None)
    year = querySet.get('year', False)
    periods = querySet.getlist('periods')
    production_sites = querySet.getlist('production_sites')
    delivery_sites = querySet.getlist('delivery_sites')
    matieres_premieres = querySet.getlist('matieres_premieres')
    countries_of_origin = querySet.getlist('countries_of_origin')
    biocarburants = querySet.getlist('biocarburants')
    clients = querySet.getlist('clients')
    vendors = querySet.getlist('vendors')
    producers = querySet.getlist('producers')
    traders = querySet.getlist('traders')
    operators = querySet.getlist('operators')
    delivery_status = querySet.getlist('delivery_status')
    added_by = querySet.getlist('added_by')
    errors = querySet.getlist('errors')
    query = querySet.get('query', False)
    is_hidden_by_admin = querySet.get('is_hidden_by_admin', None)
    is_hidden_by_auditor = querySet.get('is_hidden_by_auditor', None)
    is_highlighted_by_admin = querySet.get('is_highlighted_by_admin', None)
    is_highlighted_by_auditor = querySet.get('is_highlighted_by_auditor', None)
    selection = querySet.getlist('selection')
    client_types = querySet.getlist('client_types')

    if year and 'year' not in blacklist:
        txs = txs.filter(lot__year=year)

    if len(selection) > 0:
        txs = txs.filter(pk__in=selection)

    if len(periods) > 0 and 'periods' not in blacklist:
        txs = txs.filter(lot__period__in=periods)
    if len(production_sites) > 0 and 'production_sites' not in blacklist:
        txs = txs.filter(Q(lot__carbure_production_site__name__in=production_sites) | Q(lot__unknown_production_site__in=production_sites))
    if len(matieres_premieres) > 0 and 'matieres_premieres' not in blacklist:
        txs = txs.filter(lot__matiere_premiere__code__in=matieres_premieres)
    if len(biocarburants) > 0 and 'biocarburants' not in blacklist:
        txs = txs.filter(lot__biocarburant__code__in=biocarburants)
    if len(countries_of_origin) > 0 and 'countries_of_origin' not in blacklist:
        txs = txs.filter(lot__pays_origine__code_pays__in=countries_of_origin)
    if len(delivery_sites) > 0 and 'delivery_sites' not in blacklist:
        txs = txs.filter(Q(carbure_delivery_site__name__in=delivery_sites) | Q(unknown_delivery_site__in=delivery_sites))
    if len(clients) > 0 and 'clients' not in blacklist:
        txs = txs.filter(Q(carbure_client__name__in=clients) | Q(unknown_client__in=clients))
    if len(vendors) > 0 and 'vendors' not in blacklist:
        txs = txs.filter(Q(carbure_vendor__name__in=vendors) | Q(lot__unknown_supplier__in=vendors))
    if len(delivery_status) > 0 and 'delivery_status' not in blacklist:
        txs = txs.filter(delivery_status__in=delivery_status)

    if len(producers) > 0 and 'producers' not in blacklist:
        txs = filter_by_entities(txs, producers)
    if len(operators) > 0 and 'operators' not in blacklist:
        txs = filter_by_entities(txs, operators)
    if len(traders) > 0 and 'traders' not in blacklist:
        txs = filter_by_entities(txs, traders)

    if len(added_by) > 0 and 'added_by' not in blacklist:
        txs = txs.filter(lot__added_by__name__in=added_by)

    if len(client_types) > 0 and 'client_types' not in blacklist:
        if 'Inconnu' in client_types:
            types = [t for t in client_types if t != 'Inconnu']
            txs = txs.filter(Q(carbure_client__entity_type__in=types) | Q(carbure_client=None))
        else:
            txs = txs.filter(carbure_client__entity_type__in=client_types)

    if is_forwarded is not None and 'is_forwarded' not in blacklist:
        if is_forwarded == 'true':
            txs = txs.filter(is_forwarded=True)
        else:
            txs = txs.filter(is_forwarded=False)

    if is_mac is not None and 'is_mac' not in blacklist:
        if is_mac == 'true':
            txs = txs.filter(is_mac=True)
        else:
            txs = txs.filter(is_mac=False)

    if is_hidden_by_admin is not None and 'is_hidden_by_admin' not in blacklist:
        if is_hidden_by_admin == 'true':
            txs = txs.filter(hidden_by_admin=True)
        else:
            txs = txs.filter(hidden_by_admin=False)

    if is_hidden_by_auditor is not None and 'is_hidden_by_auditor' not in blacklist:
        if is_hidden_by_auditor == 'true':
            txs = txs.filter(hidden_by_auditor=True)
        else:
            txs = txs.filter(hidden_by_auditor=False)

    if is_highlighted_by_admin is not None and 'is_highlighted_by_admin' not in blacklist:
        if is_highlighted_by_admin == 'true':
            txs = txs.filter(highlighted_by_admin=True)
        else:
            txs = txs.filter(highlighted_by_admin=False)

    if is_highlighted_by_auditor is not None and 'is_highlighted_by_auditor' not in blacklist:
        if is_highlighted_by_auditor == 'true':
            txs = txs.filter(is_highlighted_by_auditor=True)
        else:
            txs = txs.filter(is_highlighted_by_auditor=False)

    if len(errors) > 0 and 'errors' not in blacklist:
        txs = txs.filter(genericerror__error__in=errors)

    if query and 'query' not in blacklist:
        txs = txs.filter(
            Q(lot__matiere_premiere__name__icontains=query) |
            Q(lot__biocarburant__name__icontains=query) |
            Q(lot__carbure_producer__name__icontains=query) |
            Q(lot__unknown_producer__icontains=query) |
            Q(lot__carbure_id__icontains=query) |
            Q(lot__pays_origine__name__icontains=query) |
            Q(carbure_client__name__icontains=query) |
            Q(unknown_client__icontains=query) |
            Q(carbure_delivery_site__name__icontains=query) |
            Q(unknown_delivery_site__icontains=query) |
            Q(champ_libre__icontains=query) |
            Q(dae__icontains=query) |
            Q(lot__carbure_production_site__dc_reference__icontains=query) |
            Q(lot__unknown_production_site_dbl_counting__icontains=query)
        )

    invalid = querySet.get('invalid', False)
    deadline = querySet.get('deadline', False)

    deadline_date = get_current_deadline()
    deadline_str = deadline_date.strftime("%Y-%m-%d")

    tx_with_errors = get_lots_with_errors(txs)
    tx_with_deadline = get_lots_with_deadline(txs, deadline_date)

    total_errors = tx_with_errors.count()
    total_deadline = tx_with_deadline.count()

    if invalid == 'true':
        txs = tx_with_errors
    elif deadline == 'true' and 'deadline' not in blacklist:
        txs = tx_with_deadline

    return txs, total_errors, total_deadline, deadline_str


def sort_lots(txs, querySet):
    sort_by = querySet.get('sort_by', False)
    order = querySet.get('order', False)

    if not sort_by:
        txs = txs.order_by('-id')
    elif sort_by in sort_key_to_django_field:
        key = sort_key_to_django_field[sort_by]
        if order == 'desc':
            txs = txs.order_by('-%s' % key)
        else:
            txs = txs.order_by(key)
    elif sort_by == 'biocarburant':
        if order == 'desc':
            txs = txs.order_by('-lot__biocarburant__name', '-lot__volume')
        else:
            txs = txs.order_by('lot__biocarburant__name', 'lot__volume')
    elif sort_by == 'client':
        txs = txs.annotate(client=Coalesce('carbure_client__name', 'unknown_client'))
        if order == 'desc':
            txs = txs.order_by('-client')
        else:
            txs = txs.order_by('client')
    elif sort_by == 'vendor':
        txs = txs.annotate(vendor=Coalesce('carbure_vendor__name', 'lot__unknown_supplier'))
        if order == 'desc':
            txs = txs.order_by('-vendor')
        else:
            txs = txs.order_by('vendor')

    return txs


def get_lots_with_metadata(txs, entity, querySet, admin=False):
    if txs is None:
        return JsonResponse({'status': 'error', 'message': 'Could not fetch stock list'})

    export = querySet.get('export', False)

    limit = querySet.get('limit', None)
    from_idx = querySet.get('from_idx', "0")

    txs, total_errors, total_deadline, deadline_str = filter_lots(txs, querySet)
    txs = sort_lots(txs, querySet)

    from_idx = int(from_idx)
    returned = txs[from_idx:]

    if limit is not None:
        limit = int(limit)
        returned = returned[:limit]

    errors = {}

    for tx in returned:
        grouped_errors = get_errors(tx)
        if len(grouped_errors) > 0:
            errors[tx.id] = grouped_errors

    data = {}
    data['lots'] = [t.natural_key(admin) for t in returned]
    data['total'] = txs.count()
    data['total_errors'] = total_errors
    data['returned'] = returned.count()
    data['from'] = from_idx
    data['errors'] = errors
    data['deadlines'] = {'date': deadline_str, 'total': total_deadline}

    if not export:
        return JsonResponse({'status': 'success', 'data': data})
    else:
        file_location = export_transactions(entity, returned)
        with open(file_location, "rb") as excel:
            data = excel.read()
            ctype = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            response = HttpResponse(content=data, content_type=ctype)
            response['Content-Disposition'] = 'attachment; filename="%s"' % (file_location)
        return response


def get_snapshot_filters(txs, entity, whitelist):
    filters = {}

    # prefetch related lots and txs to speed up queries
    ids = txs.values('id', 'lot__id').distinct()
    lot_ids = set([tx['lot__id'] for tx in ids])
    tx_ids = set([tx['id'] for tx in ids])
    lots = LotV2.objects.filter(id__in=lot_ids)
    txs = LotTransaction.objects.filter(id__in=tx_ids)

    if 'matieres_premieres' in whitelist:
        mps = MatierePremiere.objects.filter(id__in=lots.values('matiere_premiere__id').distinct()).values('code', 'name')
        filters['matieres_premieres'] = [{'value': mp['code'], 'label': mp['name']} for mp in mps]

    if 'biocarburants' in whitelist:
        bcs = Biocarburant.objects.filter(id__in=lots.values('biocarburant__id').distinct()).values('code', 'name')
        filters['biocarburants'] = [{'value': b['code'], 'label': b['name']} for b in bcs]

    if 'countries_of_origin' in whitelist:
        countries = Pays.objects.filter(id__in=lots.values('pays_origine').distinct()).values('code_pays', 'name')
        filters['countries_of_origin'] = [{'value': c['code_pays'], 'label': c['name']} for c in countries]

    if 'periods' in whitelist:
        filters['periods'] = [p['period'] for p in lots.values('period').distinct() if p['period']]

    if 'production_sites' in whitelist:
        filters['production_sites'] = []
        for ps in lots.values('carbure_production_site__name', 'unknown_production_site').distinct():
            if ps['carbure_production_site__name'] not in ('', None):
                filters['production_sites'].append(ps['carbure_production_site__name'])
            elif ps['unknown_production_site'] not in ('', None):
                filters['production_sites'].append(ps['unknown_production_site'])

    if 'delivery_sites' in whitelist:
        filters['delivery_sites'] = []
        for ps in txs.values('carbure_delivery_site__name', 'unknown_delivery_site').distinct():
            if ps['carbure_delivery_site__name'] not in ('', None):
                filters['delivery_sites'].append(ps['carbure_delivery_site__name'])
            elif ps['unknown_delivery_site'] not in ('', None):
                filters['delivery_sites'].append(ps['unknown_delivery_site'])

    if 'errors' in whitelist:
        generic_errors = [e['genericerror__error'] for e in txs.values('genericerror__error').distinct() if e['genericerror__error']]
        filters['errors'] = generic_errors

    if 'clients' in whitelist:
        filters['clients'] = []
        for ps in txs.values('carbure_client__name', 'unknown_client').distinct():
            if ps['carbure_client__name'] not in ('', None):
                filters['clients'].append(ps['carbure_client__name'])
            elif ps['unknown_client'] not in ('', None):
                filters['clients'].append(ps['unknown_client'])

    if 'vendors' in whitelist:
        v1 = [v['carbure_vendor__name'] for v in txs.values('carbure_vendor__name').distinct()]
        if entity is not None:
            v2 = [v['lot__unknown_supplier'] for v in txs.filter(Q(carbure_vendor=entity) | Q(lot__added_by=entity)).values('lot__unknown_supplier').distinct()]
        else:
            v2 = [v['unknown_supplier'] for v in lots.values('unknown_supplier').distinct()]
        filters['vendors'] = [v for v in set(v1 + v2) if v]

    if 'added_by' in whitelist:
        filters['added_by'] = [e['added_by__name'] for e in lots.values('added_by__name').distinct()]

    if 'delivery_status' in whitelist:
        filters['delivery_status'] = [{'value': s[0], 'label': s[1]} for s in LotTransaction.DELIVERY_STATUS]

    if 'is_forwarded' in whitelist:
        filters['is_forwarded'] = [{'value': True, 'label': 'Oui'}, {'value': False, 'label': 'Non'}]

    if 'is_mac' in whitelist:
        filters['is_mac'] = [{'value': True, 'label': 'Oui'}, {'value': False, 'label': 'Non'}]

    if 'is_hidden_by_admin' in whitelist:
        filters['is_hidden_by_admin'] = [{'value': True, 'label': 'Oui'}, {'value': False, 'label': 'Non'}]

    if 'is_hidden_by_auditor' in whitelist:
        filters['is_hidden_by_auditor'] = [{'value': True, 'label': 'Oui'}, {'value': False, 'label': 'Non'}]

    if 'is_highlighted_by_admin' in whitelist:
        filters['is_highlighted_by_admin'] = [{'value': True, 'label': 'Oui'}, {'value': False, 'label': 'Non'}]

    if 'is_highlighted_by_auditor' in whitelist:
        filters['is_highlighted_by_auditor'] = [{'value': True, 'label': 'Oui'}, {'value': False, 'label': 'Non'}]

    if 'client_types' in whitelist:
        filters['client_types'] = [Entity.OPERATOR, Entity.PRODUCER, Entity.TRADER, 'Inconnu']

    return filters


def get_summary(txs, entity):
    txs_in = txs.filter(carbure_client=entity).annotate(
        vendor=Coalesce('carbure_vendor__name', 'lot__unknown_supplier'),
    ).values(
        'vendor',
        'lot__biocarburant__code'
    ).annotate(
        volume=Sum('lot__volume'),
        avg_ghg_reduction=Sum(F('lot__volume') * F('lot__ghg_reduction')) / Sum('lot__volume'),
        lots=Count('id')
    ).order_by()

    data_in = {}
    for t in txs_in.iterator():
        if t['vendor'] not in data_in:
            data_in[t['vendor']] = {}

        data_in[t['vendor']][t['lot__biocarburant__code']] = {
            'volume': t['volume'] or 0,
            'avg_ghg_reduction': t['avg_ghg_reduction'] or 0,
            'lots': t['lots']
        }

    txs_out = txs.filter(carbure_vendor=entity).exclude(carbure_client=entity).annotate(
        client=Coalesce('carbure_client__name', 'unknown_client'),
    ).values(
        'client',
        'lot__biocarburant__code'
    ).annotate(
        volume=Sum('lot__volume'),
        avg_ghg_reduction=Sum(F('lot__volume') * F('lot__ghg_reduction')) / Sum('lot__volume'),
        lots=Count('id')
    ).order_by()

    data_out = {}
    for t in txs_out.iterator():
        if t['client'] not in data_out:
            data_out[t['client']] = {}

        data_out[t['client']][t['lot__biocarburant__code']] = {
            'volume': t['volume'] or 0,
            'avg_ghg_reduction': t['avg_ghg_reduction'] or 0,
            'lots': t['lots']
        }

    tx_ids = [t['id'] for t in txs.values('id')]
    total_volume = txs.aggregate(Sum('lot__volume'))['lot__volume__sum']
    return {'in': data_in, 'out': data_out, 'tx_ids': tx_ids, 'total_volume': total_volume}


def get_general_summary(txs):
    data = {}

    txs_aggregation = txs.annotate(
        vendor=Coalesce('carbure_vendor__name', 'lot__unknown_supplier'),
        client=Coalesce('carbure_client__name', 'unknown_client'),
    ).values(
        'vendor',
        'client',
        'lot__biocarburant__code'
    ).annotate(
        volume=Sum('lot__volume'),
        avg_ghg_reduction=Sum(F('lot__volume') * F('lot__ghg_reduction')) / Sum('lot__volume'),
        lots=Count('id')
    ).order_by()  # remove order by

    for t in txs_aggregation.iterator():
        if t['vendor'] not in data:
            data[t['vendor']] = {}
        if t['client'] not in data[t['vendor']]:
            data[t['vendor']][t['client']] = {}

        data[t['vendor']][t['client']][t['lot__biocarburant__code']] = {
            'volume': t['volume'] or 0,
            'avg_ghg_reduction': t['avg_ghg_reduction'] or 0,
            'lots': t['lots']
        }

    tx_ids = [t['id'] for t in txs.values('id')]
    total_volume = txs.aggregate(Sum('lot__volume'))['lot__volume__sum']
    return {'transactions': data, 'tx_ids': tx_ids, 'total_volume': total_volume}


# little helper to help measure elapsed time
class Perf:
    def __init__(self):
        t0 = perf_counter()
        self.steps = [t0]

    def step(self, message):
        t = perf_counter()
        dt = t - self.steps[-1]
        self.steps.append(t)
        print("[%f] %s" % (dt, message))

    def total(self, message):
        dt = self.steps[-1] - self.steps[0]
        print("[%f] %s" % (dt, message))
