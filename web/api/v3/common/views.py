import datetime
from django.http import JsonResponse
from django.db.models import Q, Count, Sum
from core.models import CarbureLot, Entity, Biocarburant, MatierePremiere, Depot, Pays
from core.models import UserRights
from producers.models import ProductionSite, ProductionSiteInput, ProductionSiteOutput
from core.decorators import check_rights
from django_otp.decorators import otp_required


def get_matieres_premieres(request):
    q = request.GET.get('query', False)
    double_count_only = request.GET.get('double_count_only', False)
    mps = MatierePremiere.objects.filter(is_displayed=True).order_by('name')
    if double_count_only == 'true':
        mps = mps.filter(is_double_compte=True)
    if q:
        mps = mps.filter(Q(name__icontains=q) | Q(name_en__icontains=q) | Q(code__icontains=q))
    sez = [{'code': m.code, 'name': m.name, 'description': m.description, 'compatible_alcool': m.compatible_alcool,
            'compatible_graisse': m.compatible_graisse, 'is_double_compte': m.is_double_compte, 'category': m.category} for m in mps]
    return JsonResponse({'status': 'success', 'data': sez})


def get_biocarburants(request):
    q = request.GET.get('query', False)
    bcs = Biocarburant.objects.filter(is_displayed=True).order_by('name')
    if q:
        bcs = bcs.filter(Q(name__icontains=q) | Q(name_en__icontains=q) | Q(code__icontains=q))
    sez = [{'code': b.code, 'name': b.name, 'description': b.description, 'pci_kg': b.pci_kg, 'pci_litre': b.pci_litre,
            'masse_volumique': b.masse_volumique, 'is_alcool': b.is_alcool, 'is_graisse': b.is_graisse} for b in bcs]
    return JsonResponse({'status': 'success', 'data': sez})


def get_countries(request):
    q = request.GET.get('query', False)
    countries = Pays.objects.all().order_by('name')
    if q:
        countries = countries.filter(Q(name__icontains=q) | Q(name_en__icontains=q) | Q(code_pays__icontains=q))
    sez = [c.natural_key() for c in countries]
    return JsonResponse({'status': 'success', 'data': sez})


def get_entities(request):
    q = request.GET.get('query', False)
    entities = Entity.objects.all().order_by('name')
    if q:
        entities = entities.filter(name__icontains=q)
    sez = [{'entity_type': e.entity_type, 'name': e.name, 'id': e.id} for e in entities]
    return JsonResponse({'status': 'success', 'data': sez})


def get_producers(request):
    q = request.GET.get('query', False)
    entities = Entity.objects.filter(entity_type='Producteur').order_by('name')
    if q:
        entities = entities.filter(name__icontains=q)
    sez = [{'entity_type': e.entity_type, 'name': e.name, 'id': e.id} for e in entities]
    return JsonResponse({'status': 'success', 'data': sez})


def get_traders(request):
    q = request.GET.get('query', False)
    entities = Entity.objects.filter(entity_type='Trader').order_by('name')
    if q:
        entities = entities.filter(name__icontains=q)
    sez = [{'entity_type': e.entity_type, 'name': e.name, 'id': e.id} for e in entities]
    return JsonResponse({'status': 'success', 'data': sez})


def get_operators(request):
    q = request.GET.get('query', False)
    entities = Entity.objects.filter(entity_type='Opérateur').order_by('name')
    if q:
        entities = entities.filter(name__icontains=q)
    sez = [{'entity_type': e.entity_type, 'name': e.name, 'id': e.id} for e in entities]
    return JsonResponse({'status': 'success', 'data': sez})


def get_delivery_sites(request):
    q = request.GET.get('query', False)
    entity_id = request.GET.get('entity_id', False)

    try:
        dsites = Depot.objects.all().order_by('name')
        if q:
            dsites = dsites.filter(Q(name__icontains=q) | Q(depot_id__icontains=q) | Q(city__icontains=q))
    except Exception:
        return JsonResponse({'status': 'error', 'message': "Could not find delivery sites"}, status=400)

    sez = [d.natural_key() for d in dsites]
    return JsonResponse({'status': 'success', 'data': sez})


def get_production_sites(request):
    q = request.GET.get('query', False)
    pid = request.GET.get('producer_id', False)
    psites = ProductionSite.objects.select_related('country', 'producer').prefetch_related('productionsiteinput_set', 'productionsiteoutput_set').all().order_by('name')
    if q:
        psites = psites.filter(name__icontains=q)
    if pid:
        psites = psites.filter(producer__id=pid)

    psitesbyid = {p.id: p for p in psites}
    for k, v in psitesbyid.items():
        v.inputs = []
        v.outputs = []

    inputs = ProductionSiteInput.objects.select_related('matiere_premiere').filter(production_site__in=psites)
    for i in inputs:
        psitesbyid[i.production_site.id].inputs.append(i.matiere_premiere.natural_key())

    outputs = ProductionSiteOutput.objects.select_related('biocarburant').filter(production_site__in=psites)
    for o in outputs:
        psitesbyid[o.production_site.id].outputs.append(o.biocarburant.natural_key())
    sez = [{'name': p.name, 'id': p.id, 'country': p.country.natural_key(),
            'date_mise_en_service': p.date_mise_en_service,
            'ges_option': p.ges_option, 'eligible_dc': p.eligible_dc, 'dc_reference': p.dc_reference,
            'inputs': p.inputs, 'outputs': p.outputs, 'producer': p.producer.natural_key()} for p in psites]
    return JsonResponse({'status': 'success', 'data': sez})

@otp_required
def create_delivery_site(request):
    name = request.POST.get('name', False)
    city = request.POST.get('city', False)
    country = request.POST.get('country_code', False)
    depot_id = request.POST.get('depot_id', False)
    depot_type = request.POST.get('depot_type', False)

    address = request.POST.get('address', False)
    postal_code = request.POST.get('postal_code', False)

    if not name:
        return JsonResponse({'status': 'error', 'message': 'Missing name'}, status=400)
    if not city:
        return JsonResponse({'status': 'error', 'message': 'Missing city'}, status=400)
    if not country:
        return JsonResponse({'status': 'error', 'message': 'Missing country'}, status=400)
    if not depot_id:
        return JsonResponse({'status': 'error', 'message': 'Missing depot id'}, status=400)
    if not depot_type:
        return JsonResponse({'status': 'error', 'message': 'Missing depot type'}, status=400)
    if not address:
        return JsonResponse({'status': 'error', 'message': 'Missing address'}, status=400)
    if not postal_code:
        return JsonResponse({'status': 'error', 'message': 'Missing postal code'}, status=400)

    try:
        country = Pays.objects.get(code_pays=country)
    except Exception:
        return JsonResponse({'status': 'error', 'message': 'Unknown country_code %s' % (country)}, status=400)

    if depot_type not in [Depot.EFS, Depot.EFPE, Depot.OTHER, Depot.BIOFUELDEPOT, Depot.OILDEPOT]:
        return JsonResponse({'status': 'error', 'message': 'Unknown depot type %s' % (depot_type)}, status=400)

    d = {'name': name, 'city': city, 'depot_type': depot_type, 'address': address,
        'postal_code': postal_code}

    try:
        Depot.objects.update_or_create(depot_id=depot_id, country=country, defaults=d)
    except Exception:
        return JsonResponse({'status': 'error', 'message': 'Server error'}, status=500)
    return JsonResponse({'status': 'success'})



def get_stats(request):
    try:
        today = datetime.date.today()
        year = str(today.year)
        total_volume = CarbureLot.objects.filter(lot_status__in=[CarbureLot.ACCEPTED, CarbureLot.FROZEN], year=year, delivery_type=CarbureLot.BLENDING).aggregate(Sum('volume'))
        entity_count = Entity.objects.filter(entity_type__in=[Entity.PRODUCER, Entity.TRADER, Entity.OPERATOR]).values('entity_type').annotate(count=Count('id'))
        entities = {}
        for r in entity_count:
            entities[r['entity_type']] = r['count']
        total = total_volume['volume__sum']
        if total is None:
            total = 1000
        return JsonResponse({'status': 'success', 'data': {'total_volume': total / 1000, 'entities': entities}})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': 'Could not compute statistics'})

