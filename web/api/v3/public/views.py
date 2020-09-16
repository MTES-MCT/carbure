from django.http import JsonResponse
from django.db.models import Q
from core.models import Entity, Biocarburant, MatierePremiere, Depot, Pays
from producers.models import ProductionSite, ProductionSiteInput, ProductionSiteOutput


def get_matieres_premieres(request):
    q = request.GET.get('query', False)
    mps = MatierePremiere.objects.all()
    if q:
        mps = mps.filter(Q(name__icontains=q) | Q(code__icontains=q))
    sez = [{'code': m.code, 'name': m.name, 'description': m.description, 'compatible_alcool': m.compatible_alcool, 'compatible_graisse': m.compatible_graisse} for m in mps]
    return JsonResponse({'status': 'success', 'data': sez})


def get_biocarburants(request):
    q = request.GET.get('query', False)
    bcs = Biocarburant.objects.all()
    if q:
        bcs = bcs.filter(Q(name__icontains=q) | Q(code__icontains=q))
    sez = [{'code': b.code, 'name': b.name, 'description': b.description, 'pci_kg': b.pci_kg, 'pci_litre': b.pci_litre,
            'masse_volumique': b.masse_volumique, 'is_alcool': b.is_alcool, 'is_graisse': b.is_graisse} for b in bcs]
    return JsonResponse({'status': 'success', 'data': sez})


def get_countries(request):
    q = request.GET.get('query', False)
    countries = Pays.objects.all()
    if q:
        countries = countries.filter(Q(name__icontains=q) | Q(code__icontains=q))
    sez = [c.natural_key() for c in countries]
    return JsonResponse({'status': 'success', 'data': sez})


def get_ges(request):
    # TODO
    return JsonResponse({'status': 'success', 'data': {'eec': 0.0, 'el': 0.0, 'ep': 0.0, 'etd': 0.0, 'eu': 0.0,
                         'esca': 0.0, 'eccs': 0.0, 'eccr': 0.0, 'eee': 0.0}})


def get_entities(request):
    q = request.GET.get('query', False)
    entities = Entity.objects.all()
    if q:
        entities = entities.filter(name__icontains=q)
    sez = [{'entity_type': e.entity_type, 'name': e.name, 'id': e.id} for e in entities]
    return JsonResponse({'status': 'success', 'data': sez})


def get_producers(request):
    q = request.GET.get('query', False)
    entities = Entity.objects.filter(entity_type='Producteur')
    if q:
        entities = entities.filter(name__icontains=q)
    sez = [{'entity_type': e.entity_type, 'name': e.name, 'id': e.id} for e in entities]
    return JsonResponse({'status': 'success', 'data': sez})


def get_traders(request):
    q = request.GET.get('query', False)
    entities = Entity.objects.filter(entity_type='Trader')
    if q:
        entities = entities.filter(name__icontains=q)
    sez = [{'entity_type': e.entity_type, 'name': e.name, 'id': e.id} for e in entities]
    return JsonResponse({'status': 'success', 'data': sez})


def get_operators(request):
    q = request.GET.get('query', False)
    entities = Entity.objects.filter(entity_type='Opérateur')
    if q:
        entities = entities.filter(name__icontains=q)
    sez = [{'entity_type': e.entity_type, 'name': e.name, 'id': e.id} for e in entities]
    return JsonResponse({'status': 'success', 'data': sez})


def get_delivery_sites(request):
    q = request.GET.get('query', False)
    dsites = Depot.objects.all()
    if q:
        dsites = dsites.filter(Q(name__icontains=q) | Q(depot_id__icontains=q))
    sez = [{'name': d.name, 'city': d.city, 'depot_id': d.depot_id, 'country': d.country.natural_key(), 'depot_type': d.depot_type} for d in dsites]
    return JsonResponse({'status': 'success', 'data': sez})


def get_production_sites(request):
    q = request.GET.get('query', False)
    pid = request.GET.get('producer_id', False)
    psites = ProductionSite.objects.all()
    if q:
        psites = psites.filter(name__icontains=q)
    if pid:
        psites = psites.filter(producer__id=pid)

    psitesbyid = {p.id: p for p in psites}
    for k, v in psitesbyid.items():
        v.inputs = []
        v.outputs = []

    inputs = ProductionSiteInput.objects.filter(production_site__in=psites)
    for i in inputs:
        psitesbyid[i.production_site.id].inputs.append(i.matiere_premiere.natural_key())

    outputs = ProductionSiteOutput.objects.filter(production_site__in=psites)
    for o in outputs:
        psitesbyid[o.production_site.id].outputs.append(o.biocarburant.natural_key())
    sez = [{'name': p.name, 'id': p.id, 'country': p.country.natural_key(), 'date_mise_en_service': p.date_mise_en_service,
            'ges_option': p.ges_option, 'eligible_dc': p.eligible_dc, 'dc_reference': p.dc_reference,
            'inputs': p.inputs, 'outputs': p.outputs, 'producer': p.producer.natural_key()} for p in psites]
    return JsonResponse({'status': 'success', 'data': sez})
