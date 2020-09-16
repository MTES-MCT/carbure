from django.http import JsonResponse
from django.db.models import Q
from core.models import Entity, Biocarburant, MatierePremiere, Depot, GHGValues, Pays
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
    sez = [{'code_pays': c.code_pays, 'name': c.name, 'name_en': c.name_en, 'is_in_europe': c.is_in_europe} for c in countries]
    return JsonResponse({'status': 'success', 'data': sez})


def get_ges(request):
    pass


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
    pass


def get_production_sites(request):
    pass
