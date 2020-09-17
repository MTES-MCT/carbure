import io
import datetime
import calendar
import dateutil.relativedelta
from django.db.models import Q
from django.db.models.functions import TruncMonth
from django.db.models import Count
from django.http import JsonResponse, HttpResponse
from core.models import LotTransaction, Entity, UserRights, MatierePremiere, Biocarburant, Pays
from core.xlsx_template import create_xslx_from_transactions


def get_lots(request):
    status = request.GET.get('status', False)
    producer = request.GET.get('producer_id', False)
    year = request.GET.get('year', False)
    periods = request.GET.getlist('periods', False)
    production_sites = request.GET.getlist('production_sites', False)
    matieres_premieres = request.GET.getlist('matieres_premieres', False)
    countries_of_origin = request.GET.getlist('countries_of_origin', False)
    biocarburants = request.GET.getlist('biocarburants', False)
    clients = request.GET.getlist('clients', False)
    limit = request.GET.get('limit', "100")
    from_idx = request.GET.get('from_idx', "0")
    export = request.GET.get('export', False)

    if not status:
        return JsonResponse({'status': 'error', 'message': 'Missing status'}, status=400)
    if producer is None:
        return JsonResponse({'status': 'error', 'message': "Missing producer_id"}, status=400)
    try:
        producer = Entity.objects.get(id=producer, entity_type='Producteur')
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': "Unknown producer %s" % (producer), 'extra': str(e)}, status=400)

    rights = [r.entity for r in UserRights.objects.filter(user=request.user)]
    if producer not in rights:
        return JsonResponse({'status': 'forbidden', 'message': "User not allowed"}, status=403)

    txs = LotTransaction.objects.filter(lot__carbure_producer=producer)

    # apply filters
    date_from = datetime.date.today().replace(month=1, day=1)
    date_until = datetime.date.today().replace(month=12, day=31)
    if year:
        try:
            year = int(year)
            date_from = datetime.date(year=year, month=1, day=1)
            date_until = datetime.date(year=year, month=12, day=31)
        except Exception:
            return JsonResponse({'status': 'error', 'message': 'Incorrect format for year. Expected YYYY'}, status=400)
    txs = txs.filter(delivery_date__gte=date_from).filter(delivery_date__lte=date_until)

    if periods:
        txs = txs.filter(lot__period__in=periods)
    if production_sites:
        txs = txs.filter(Q(lot__carbure_production_site__name__in=production_sites) | Q(lot__unknown_production_site__in=production_sites))
    if matieres_premieres:
        txs = txs.filter(lot__matiere_premiere__code__in=matieres_premieres)
    if biocarburants:
        txs = txs.filter(lot__biocarburant__code__in=matieres_premieres)
    if countries_of_origin:
        txs = txs.filter(lot__pays_origine__code_pays__in=countries_of_origin)
    if clients:
        txs = txs.filter(Q(carbure_client__name__in=clients) | Q(unknown_client__in=clients))

    limit = int(limit)
    from_idx = int(from_idx)
    returned = txs[from_idx:from_idx+limit]

    data = {}
    data['lots'] = [t.natural_key() for t in txs]
    data['total'] = len(txs)
    data['returned'] = len(returned)
    data['from'] = from_idx
    if not export:
        return JsonResponse({'status': 'success', 'data': data})
    else:
        file_location = create_xslx_from_transactions(producer, returned)
        with open(file_location, "rb") as excel:
            data = excel.read()
            response = HttpResponse(data=data, content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            response['Content-Disposition'] = 'attachment; filename="%s"' % (file_location)
        return response


def get_snapshot(request):
    data = {}
    today = datetime.date.today()

    producer = request.GET.get('producer_id', False)
    if producer is None:
        return JsonResponse({'status': 'error', 'message': "Missing producer_id"}, status=400)
    try:
        producer = Entity.objects.get(id=producer, entity_type='Producteur')
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': "Unknown producer %s" % (producer), 'extra': str(e)}, status=400)

    rights = [r.entity for r in UserRights.objects.filter(user=request.user)]
    if producer not in rights:
        return JsonResponse({'status': 'forbidden', 'message': "User not allowed"}, status=403)

    txs = LotTransaction.objects.filter(lot__carbure_producer=producer)

    drafts = len(txs.filter(lot__status='Draft'))
    validated = len(txs.filter(lot__status='Validated', delivery_status__in=['N', 'AA']))
    tofix = len(txs.filter(lot__status='Validated', delivery_status='AC'))
    accepted = len(txs.filter(lot__status='Validated', delivery_status='A'))
    data['lots'] = {'drafts': drafts, 'validated': validated, 'tofix': tofix, 'accepted': accepted}

    mps = [m.natural_key() for m in MatierePremiere.objects.filter(id__in=txs.values('lot__matiere_premiere').distinct())]
    bcs = [b.natural_key() for b in Biocarburant.objects.filter(id__in=txs.values('lot__biocarburant').distinct())]
    periods = [p for p in txs.values('lot__period').distinct()]
    countries = [c.natural_key() for c in Pays.objects.filter(id__in=txs.values('lot__pays_origine').distinct())]
    c1 = txs.values('carbure_client__name').distinct()
    c2 = txs.values('unknown_client').distinct()
    clients = [c['carbure_client__name'] for c in c1]+[c['unknown_client'] for c in c2]

    ps1 = txs.values('lot__carbure_production_site__name').distinct()
    ps2 = txs.values('lot__unknown_production_site').distinct()
    psites = list(ps1) + list(ps2)
    data['filters'] = {'matieres_premieres': mps, 'biocarburants': bcs, 'periods': periods, 'production_sites': psites, 'countries_of_origin': countries, 'clients': clients}

    deadlines = txs.filter(lot__status='Draft').annotate(month=TruncMonth('delivery_date')).values('month').annotate(total=Count('id'))
    for d in deadlines:
        if d['month'] is None:
            d['deadline'] = None
        else:
            nextmonth = d['month'] + dateutil.relativedelta.relativedelta(months=+1)
            (_, day) = calendar.monthrange(nextmonth.year, nextmonth.month)
            d['deadline'] = d['month'].replace(month=nextmonth.month, day=day)
            d['delta'] = (d['deadline'] - today).days
    data['deadlines'] = list(deadlines)
    return JsonResponse({'status': 'success', 'data': data})


def add_lot(request):
    pass


def update_lot(request):
    pass


def delete_lot(request):
    pass


def duplicate_lot(request):
    pass


def validate_lot(request):
    pass


def accept_lot(request):
    pass


def reject_lot(request):
    pass


def comment_lot(request):
    pass


def check_lot(request):
    pass


def batch_delete(request):
    pass


def batch_validate(request):
    pass


def batch_accept(request):
    pass


def batch_reject(request):
    pass


def delete_all_drafts(request):
    pass


def upload(request):
    pass


def template_simple(request):
    pass


def template_advanced(request):
    pass
