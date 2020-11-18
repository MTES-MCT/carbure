import datetime
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q
from core.models import Entity, Biocarburant, MatierePremiere, Depot, Pays
from core.models import ISCCCertificate, DBSCertificate
from producers.models import ProductionSite, ProductionSiteInput, ProductionSiteOutput


def get_matieres_premieres(request):
    q = request.GET.get('query', False)
    mps = MatierePremiere.objects.all()
    if q:
        mps = mps.filter(Q(name__icontains=q) | Q(code__icontains=q))
    sez = [{'code': m.code, 'name': m.name, 'description': m.description, 'compatible_alcool': m.compatible_alcool,
            'compatible_graisse': m.compatible_graisse} for m in mps]
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
        countries = countries.filter(Q(name__icontains=q) | Q(code_pays__icontains=q))
    sez = [c.natural_key() for c in countries]
    return JsonResponse({'status': 'success', 'data': sez})


def get_ges(request):
    # TODO
    return JsonResponse({
        'status': 'success',
        'data': {'eec': 0.0, 'el': 0.0, 'ep': 0.0, 'etd': 0.0, 'eu': 0.0,
                 'esca': 0.0, 'eccs': 0.0, 'eccr': 0.0, 'eee': 0.0}
    })


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
        dsites = dsites.filter(Q(name__icontains=q) | Q(depot_id__icontains=q) | Q(city__icontains=q))
    sez = [d.natural_key() for d in dsites]
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
    sez = [{'name': p.name, 'id': p.id, 'country': p.country.natural_key(),
            'date_mise_en_service': p.date_mise_en_service,
            'ges_option': p.ges_option, 'eligible_dc': p.eligible_dc, 'dc_reference': p.dc_reference,
            'inputs': p.inputs, 'outputs': p.outputs, 'producer': p.producer.natural_key()} for p in psites]
    return JsonResponse({'status': 'success', 'data': sez})


def get_iscc_certificates(request):
    q = request.GET.get('query', False)
    today = datetime.date.today()
    cert = ISCCCertificate.objects.filter(valid_until__gte=today)
    if q:
        cert = cert.filter(Q(certificate_id__icontains=q) | Q(certificate_holder__icontains=q))
    sez = [{'certificate_id': c.certificate_id, 'certificate_holder': c.certificate_holder,
            'valid_from': c.valid_from.strftime('%y-%m-%d'),
            'valid_until': c.valid_until.strftime('%y-%m-%d'),
            'issuing_cb': c.issuing_cb, 'location': c.location} for c in cert]
    return JsonResponse({'status': 'success', 'data': sez})


def get_2bs_certificates(request):
    q = request.GET.get('query', False)
    today = datetime.date.today()
    cert = DBSCertificate.objects.filter(valid_until__gte=today)
    if q:
        cert = cert.filter(Q(certificate_id__icontains=q) | Q(certificate_holder__icontains=q))
    sez = [{'certificate_id': c.certificate_id, 'certificate_holder': c.certificate_holder,
            'valid_from': c.valid_from.strftime('%y-%m-%d'),
            'valid_until': c.valid_until.strftime('%y-%m-%d'), 'holder_address': c.holder_address,
            'certification_type': c.certification_type} for c in cert]
    return JsonResponse({'status': 'success', 'data': sez})


@login_required
def create_delivery_site(request):
    name = request.POST.get('name', False)
    city = request.POST.get('city', False)
    country = request.POST.get('country_code', False)
    depot_id = request.POST.get('depot_id', False)
    depot_type = request.POST.get('depot_type', False)
    
    address = request.POST.get('address', False)
    postal_code = request.POST.get('postal_code', False)
    ownership_type = request.POST.get('ownership_type', False)

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
    if not ownership_type:
        return JsonResponse({'status': 'error', 'message': 'Missing ownership type'}, status=400)                        

    try:
        country = Pays.objects.get(code_pays=country)
    except Exception as e:
        print(e)
        return JsonResponse({'status': 'error', 'message': 'Unknown country_code %s' % (country)}, status=400)                        

    if depot_type not in ['EFS', 'EFPE', 'OTHER']:
        return JsonResponse({'status': 'error', 'message': 'Unknown depot type %s' % (depot_type)}, status=400)                        
    if ownership_type not in ['OWN', 'THIRD_PARTY']:
        return JsonResponse({'status': 'error', 'message': 'Unknown ownership type %s' % (ownership_type)}, status=400)                        

    d = {'name': name, 'city': city, 'depot_type': depot_type, 'address': address, 
        'postal_code': postal_code, 'ownership_type': ownership_type}

    try:
        Depot.objects.update_or_create(depot_id=depot_id, country=country, defaults=d)
    except Exception as e:
        print(e)
        return JsonResponse({'status': 'error', 'message': 'Server error'}, status=500)
    return JsonResponse({'status': 'success'})