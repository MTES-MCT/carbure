import datetime
import calendar
from time import perf_counter
from dateutil.relativedelta import *
from django.db.models import Q, F, Case, When, Count, Sum
from django.db.models.functions import TruncMonth
from django.db.models.functions import Extract
from django.db.models.fields import NOT_PROVIDED
from django import db
from django.http import JsonResponse, HttpResponse
from core.models import LotV2, LotTransaction
from core.models import Entity, UserRights, MatierePremiere, Biocarburant, Pays, TransactionComment
from core.xlsx_v3 import template_producers_simple, template_producers_advanced, template_operators, template_traders
from core.xlsx_v3 import export_transactions
from core.common import validate_lots, load_excel_file, get_prefetched_data, check_duplicates
from api.v3.sanity_checks import bulk_sanity_checks
from django_otp.decorators import otp_required
from core.decorators import check_rights



sort_key_to_django_field = {'period': 'lot__period',
                            'biocarburant': 'lot__biocarburant__name',
                            'matiere_premiere': 'lot__matiere_premiere__name',
                            'ghg_reduction': 'lot__ghg_reduction',
                            'volume': 'lot__volume',
                            'pays_origine': 'lot__pays_origine__name',
                            'added_by': 'lot__added_by__name'}

def get_errors(tx):
    return [e.natural_key() for e in tx.genericerror_set.all()]


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
    tx_with_errors = txs.annotate(Count('genericerror')).filter(genericerror__count__gt=0)
    return tx_with_errors, tx_with_errors.count()


def get_lots_with_deadline(txs):
    now = datetime.datetime.now()
    (_, last_day) = calendar.monthrange(now.year, now.month)
    deadline_date = now.replace(day=last_day)
    affected_date = deadline_date - relativedelta(months=1)
    txs_with_deadline = txs.filter(lot__status='Draft', delivery_date__year=affected_date.year, delivery_date__month=affected_date.month)
    deadline_str = deadline_date.strftime("%Y-%m-%d")

    return txs_with_deadline, deadline_str, txs_with_deadline.count()


def filter_by_entities(txs, entities):
    return txs.filter(
        Q(carbure_client__name__in=entities) |
        Q(unknown_client__in=entities) |
        Q(carbure_vendor__name__in=entities) |
        Q(lot__unknown_supplier__in=entities) |
        Q(lot__added_by__name__in=entities)
    )


def filter_lots(txs, querySet):
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

    if year:
        try:
            year = int(year)
            date_from = datetime.date(year=year, month=1, day=1)
            date_until = datetime.date(year=year, month=12, day=31)
            txs = txs.filter(delivery_date__gte=date_from).filter(delivery_date__lte=date_until)
        except Exception:
            raise Exception('Incorrect format for year. Expected YYYY.')


    if periods:
        txs = txs.filter(lot__period__in=periods)
    if production_sites:
        txs = txs.filter(Q(lot__carbure_production_site__name__in=production_sites) | Q(lot__unknown_production_site__in=production_sites))
    if matieres_premieres:
        txs = txs.filter(lot__matiere_premiere__code__in=matieres_premieres)
    if biocarburants:
        txs = txs.filter(lot__biocarburant__code__in=biocarburants)
    if countries_of_origin:
        txs = txs.filter(lot__pays_origine__code_pays__in=countries_of_origin)
    if delivery_sites:
        txs = txs.filter(Q(carbure_delivery_site__name__in=delivery_sites) | Q(unknown_delivery_site__in=delivery_sites))
    if clients:
        txs = txs.filter(Q(carbure_client__name__in=clients) | Q(unknown_client__in=clients))
    if vendors:
        txs = txs.filter(Q(carbure_vendor__name__in=vendors) | Q(lot__unknown_supplier__in=vendors))
    if delivery_status:
        txs = txs.filter(delivery_status__in=delivery_status)

    if producers:
        txs = filter_by_entities(txs, producers)
    if operators:
        txs = filter_by_entities(txs, operators)
    if traders:
        txs = filter_by_entities(txs, traders)

    if added_by:
        txs = txs.filter(lot__added_by__name__in=added_by)

    if is_forwarded is not None:
        if is_forwarded == 'true':
            txs = txs.filter(is_forwarded=True)
        else:
            txs = txs.filter(is_forwarded=False)

    if is_mac is not None:
        if is_mac == 'true':
            txs = txs.filter(is_mac=True)
        else:
            txs = txs.filter(is_mac=False)

    if errors:
        txs = txs.filter(genericerror__error__in=errors)

    if query:
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
            Q(dae__icontains=query)
        )

    invalid = querySet.get('invalid', False)
    deadline = querySet.get('deadline', False)

    tx_with_errors, total_errors = get_lots_with_errors(txs)
    tx_with_deadline, deadline_str, total_deadline = get_lots_with_deadline(txs)

    if invalid == 'true':
        txs = tx_with_errors
    elif deadline == 'true':
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
    elif sort_by == 'client':
        txs = txs.annotate(client=Case(
            When(client_is_in_carbure=True, then=F('carbure_client__name')),
            default=F('unknown_client')
        ))

        if order == 'desc':
            txs = txs.order_by('-client')
        else:
            txs = txs.order_by('client')

    return txs


def get_lots_with_metadata(txs, entity, querySet):
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
    data['lots'] = [t.natural_key() for t in returned]
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


def get_snapshot_filters(txs, whitelist):
    filters = {}
    p = Perf()

    # prefetch related lots and txs to speed up queries
    ids = txs.values('id', 'lot__id').distinct()
    lot_ids = set([tx['lot__id'] for tx in ids])
    tx_ids = set([tx['id'] for tx in ids])
    lots = LotV2.objects.filter(id__in=lot_ids)
    txs = LotTransaction.objects.filter(id__in=tx_ids)
    p.step('init')

    if 'matieres_premieres' in whitelist:
        mps = MatierePremiere.objects.filter(id__in=lots.values('matiere_premiere__id').distinct()).values('code', 'name')
        filters['matieres_premieres'] = [{'value': mp['code'], 'label': mp['name']} for mp in mps]
    p.step('matieres_premieres')

    if 'biocarburants' in whitelist:
        bcs = Biocarburant.objects.filter(id__in=lots.values('biocarburant__id').distinct()).values('code', 'name')
        filters['biocarburants'] = [{'value': b['code'], 'label': b['name']} for b in bcs]
    p.step('biocarburants')

    if 'countries_of_origin' in whitelist:
        countries = Pays.objects.filter(id__in=lots.values('pays_origine').distinct()).values('code_pays', 'name')
        filters['countries_of_origin'] = [{'value': c['code_pays'], 'label': c['name']} for c in countries]
    p.step('countries_of_origin')

    if 'periods' in whitelist:
        filters['periods'] = [p['period'] for p in lots.values('period').distinct() if p['period']]
    p.step('periods')

    if 'production_sites' in whitelist:
        filters['production_sites'] = []
        for ps in lots.values('carbure_production_site__name', 'unknown_production_site').distinct():
            if ps['carbure_production_site__name'] not in ('', None):
                filters['production_sites'].append(ps['carbure_production_site__name'])
            elif ps['unknown_production_site'] not in ('', None):
                filters['production_sites'].append(ps['unknown_production_site'])
    p.step('production_sites')

    if 'delivery_sites' in whitelist:
        filters['delivery_sites'] = []
        for ps in txs.values('carbure_delivery_site__name', 'unknown_delivery_site').distinct():
            if ps['carbure_delivery_site__name'] not in ('', None):
                filters['delivery_sites'].append(ps['carbure_delivery_site__name'])
            elif ps['unknown_delivery_site'] not in ('', None):
                filters['delivery_sites'].append(ps['unknown_delivery_site'])
    p.step('delivery_sites')

    if 'errors' in whitelist:
        generic_errors = [e['genericerror__error'] for e in txs.values('genericerror__error').distinct() if e['genericerror__error']]
        filters['errors'] = generic_errors
    p.step('errors')

    if 'clients' in whitelist:
        filters['clients'] = []
        for ps in txs.values('carbure_client__name', 'unknown_client').distinct():
            if ps['carbure_client__name'] not in ('', None):
                filters['clients'].append(ps['carbure_client__name'])
            elif ps['unknown_client'] not in ('', None):
                filters['clients'].append(ps['unknown_client'])
    p.step('clients')

    if 'vendors' in whitelist:
        v1 = [v['carbure_vendor__name'] for v in txs.values('carbure_vendor__name').distinct()]
        v2 = [v['unknown_supplier'] for v in lots.values('unknown_supplier').distinct()]
        filters['vendors'] = [v for v in set(v1 + v2) if v]
    p.step('vendors')

    if 'added_by' in whitelist:
        filters['added_by'] = [e['added_by__name'] for e in lots.values('added_by__name').distinct()]
    p.step('added_by')

    if 'delivery_status' in whitelist:
        filters['delivery_status'] = [{'value': s[0], 'label': s[1]} for s in LotTransaction.DELIVERY_STATUS]
    p.step('delivery_status')

    if 'is_forwarded' in whitelist:
        filters['is_forwarded'] = [{'value': True, 'label': 'Oui'}, {'value': False, 'label': 'Non'}]
    p.step('is_forwarded')

    if 'is_mac' in whitelist:
        filters['is_mac'] = [{'value': True, 'label': 'Oui'}, {'value': False, 'label': 'Non'}]
    p.step('is_mac')
    p.total('end')
    return filters


def filter_entity_transactions(entity, querySet):
    status = querySet.get('status', False)

    if not status:
        raise Exception("Status is not specified")

    txs = get_entity_lots_by_status(entity, status)
    return filter_lots(txs, querySet)

def get_summary(txs, entity):
    tx_ids = [t['id'] for t in txs.values('id')]
    total_volume = 0
    txs_in = txs.filter(carbure_client=entity)
    total_volume_in = 0
    data_in = {}
    for t in txs_in:
        vendor = ''
        if t.lot.added_by == entity:
            vendor = t.lot.unknown_supplier if t.lot.unknown_supplier else t.lot.unknown_supplier_certificate
        else:
            vendor = t.carbure_vendor.name if t.carbure_vendor else t.carbure_vendor_certificate
        if vendor not in data_in:
            data_in[vendor] = {}
        if t.lot.biocarburant.name not in data_in[vendor]:
            data_in[vendor][t.lot.biocarburant.name] = {'volume': 0, 'avg_ghg_reduction': 0, 'lots': 0}
        line = data_in[vendor][t.lot.biocarburant.name]
        total = (line['volume'] + t.lot.volume)
        line['avg_ghg_reduction'] = (line['volume'] * line['avg_ghg_reduction'] +
                                     t.lot.volume * t.lot.ghg_reduction) / total if total != 0 else 0
        line['volume'] += t.lot.volume
        total_volume_in += t.lot.volume
        total_volume += t.lot.volume
        line['lots'] += 1

    txs_out = txs.filter(carbure_vendor=entity).exclude(carbure_client=entity)
    total_volume_out = 0
    data_out = {}
    for t in txs_out:
        client_name = t.carbure_client.name if t.client_is_in_carbure and t.carbure_client else t.unknown_client
        if client_name not in data_out:
            data_out[client_name] = {}
        if t.lot.biocarburant.name not in data_out[client_name]:
            data_out[client_name][t.lot.biocarburant.name] = {'volume': 0, 'avg_ghg_reduction': 0, 'lots': 0}
        line = data_out[client_name][t.lot.biocarburant.name]
        total = (line['volume'] + t.lot.volume)
        line['avg_ghg_reduction'] = (line['volume'] * line['avg_ghg_reduction'] +
                                     t.lot.volume * t.lot.ghg_reduction) / total if total != 0 else 0
        line['volume'] += t.lot.volume
        total_volume_out += t.lot.volume
        total_volume += t.lot.volume
        line['lots'] += 1

    return {'in': data_in, 'out': data_out, 'tx_ids': tx_ids,
            'total_volume': total_volume, 'total_volume_in': total_volume_in, 'total_volume_out': total_volume_out}


# little helper to help measure elapsed time
class Perf:
    steps = []

    def __init__(self):
        t0 = perf_counter()
        self.steps.append(t0)

    def step(self, message):
        t = perf_counter()
        dt = t - self.steps[-1]
        self.steps.append(t)
        print("[%f] %s" % (dt, message))

    def total(self, message):
        dt = self.steps[-1] - self.steps[0]
        print("[%f] %s" % (dt, message))
