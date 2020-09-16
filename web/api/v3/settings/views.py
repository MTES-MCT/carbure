from django.http import JsonResponse
from core.models import Entity, Biocarburant, MatierePremiere, Depot, GHGValues, Pays
from producers.models import ProductionSite, ProductionSiteInput, ProductionSiteOutput

def add_production_site(request):
    q = request.GET.get('query', False)
    mps = MatierePremiere.objects.all()
    if q:
        mps = mps.filter(Q(name__icontains=q) | Q(code__icontains=q))
    sez = [{'code': m.code, 'name': m.name} for m in mps]
    return JsonResponse({'status': 'success', 'data': sez})

def delete_production_site():
    pass

def get_production_sites():
    pass

def add_production_site_certificate():
    pass

def delete_production_site_certificate():
    pass

def add_production_site_mp():
    pass

def delete_production_site_mp():
    pass

def add_production_site_bc():
    pass

def delete_production_site_bc():
    pass

def enable_mac():
    pass

def disable_mac():
    pass

def enable_trading():
    pass

def disable_trading():
    pass
