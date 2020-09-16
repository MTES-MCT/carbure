from django.http import JsonResponse
from core.models import Entity, Biocarburant, MatierePremiere, Depot, GHGValues, Pays
from producers.models import ProductionSite, ProductionSiteInput, ProductionSiteOutput

def get_matieres_premieres(request):
    q = request.GET.get('query', False)
    mps = MatierePremiere.objects.all()
    if q:
        mps = mps.filter(Q(name__icontains=q) | Q(code__icontains=q))
    sez = [{'code': m.code, 'name': m.name} for m in mps]
    return JsonResponse({'status': 'success', 'data': sez})

def get_biocarburants():
    pass

def get_countries():
    pass

def get_ges():
    pass

def get_producers():
    pass

def get_operators():
    pass

def get_delivery_sites():
    pass

def get_production_sites():
    pass
