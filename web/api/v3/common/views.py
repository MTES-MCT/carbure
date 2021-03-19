import datetime
from django.http import JsonResponse
from django.db.models import Q
from core.models import Entity, Biocarburant, MatierePremiere, Depot, Pays
from core.models import ISCCCertificate, DBSCertificate, REDCertCertificate
from core.models import Control, ControlMessages, UserRights
from producers.models import ProductionSite, ProductionSiteInput, ProductionSiteOutput
from core.decorators import check_rights
from django_otp.decorators import otp_required

def get_matieres_premieres(request):
    q = request.GET.get('query', False)
    mps = MatierePremiere.objects.filter(is_displayed=True).order_by('name')
    if q:
        mps = mps.filter(Q(name__icontains=q) | Q(code__icontains=q))
    sez = [{'code': m.code, 'name': m.name, 'description': m.description, 'compatible_alcool': m.compatible_alcool,
            'compatible_graisse': m.compatible_graisse, 'is_double_compte': m.is_double_compte} for m in mps]
    return JsonResponse({'status': 'success', 'data': sez})


def get_biocarburants(request):
    q = request.GET.get('query', False)
    bcs = Biocarburant.objects.filter(is_displayed=True).order_by('name')
    if q:
        bcs = bcs.filter(Q(name__icontains=q) | Q(code__icontains=q))
    sez = [{'code': b.code, 'name': b.name, 'description': b.description, 'pci_kg': b.pci_kg, 'pci_litre': b.pci_litre,
            'masse_volumique': b.masse_volumique, 'is_alcool': b.is_alcool, 'is_graisse': b.is_graisse} for b in bcs]
    return JsonResponse({'status': 'success', 'data': sez})


def get_countries(request):
    q = request.GET.get('query', False)
    countries = Pays.objects.all().order_by('name')
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
        if entity_id:
            entity = Entity.objects.get(pk=entity_id)
            if entity.entity_type in ['Producteur', 'Trader']:
                dsites = dsites.filter(Q(depot_type__in=['EFPE', 'Other']))
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': "Could not find delivery sites", 'extra': str(e)}, status=400)
    
    sez = [d.natural_key() for d in dsites]
    return JsonResponse({'status': 'success', 'data': sez})


def get_production_sites(request):
    q = request.GET.get('query', False)
    pid = request.GET.get('producer_id', False)
    psites = ProductionSite.objects.all().order_by('name')
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
    lastyear = datetime.date.today() - datetime.timedelta(days=365)
    cert = ISCCCertificate.objects.filter(valid_until__gte=lastyear)
    if q:
        cert = cert.filter(Q(certificate_id__icontains=q) | Q(certificate_holder__icontains=q))

    cert = cert[0:100]
    
    sez = [{'certificate_id': c.certificate_id, 'certificate_holder': c.certificate_holder,
            'valid_from': c.valid_from.strftime('%y-%m-%d'),
            'valid_until': c.valid_until.strftime('%y-%m-%d'),
            'issuing_cb': c.issuing_cb, 'location': c.location} for c in cert]
    return JsonResponse({'status': 'success', 'data': sez})


def get_2bs_certificates(request):
    q = request.GET.get('query', False)
    lastyear = datetime.date.today() - datetime.timedelta(days=365)
    cert = DBSCertificate.objects.filter(valid_until__gte=lastyear)
    if q:
        cert = cert.filter(Q(certificate_id__icontains=q) | Q(certificate_holder__icontains=q))

    cert = cert[0:100]

    sez = [{'certificate_id': c.certificate_id, 'certificate_holder': c.certificate_holder,
            'valid_from': c.valid_from.strftime('%y-%m-%d'),
            'valid_until': c.valid_until.strftime('%y-%m-%d'), 'holder_address': c.holder_address,
            'certification_type': c.certification_type} for c in cert]
    return JsonResponse({'status': 'success', 'data': sez})


def get_redcert_certificates(request):
    q = request.GET.get('query', False)
    lastyear = datetime.date.today() - datetime.timedelta(days=365)
    cert = REDCertCertificate.objects.filter(valid_until__gte=lastyear)
    if q:
        cert = cert.filter(Q(certificate_id__icontains=q) | Q(certificate_holder__icontains=q))

    cert = cert[0:100]

    sez = [{'certificate_id': c.certificate_id, 'certificate_holder': c.certificate_holder,
            'valid_from': c.valid_from.strftime('%y-%m-%d'),
            'valid_until': c.valid_until.strftime('%y-%m-%d'), 'city': c.city, 'zip_code': c.zip_code,
            'certification_type': c.certification_type} for c in cert]
    return JsonResponse({'status': 'success', 'data': sez})


def get_certificates(request):
    q = request.GET.get('query', False)
    entity_id = request.GET.get('entity_id', None)
    production_site = request.GET.get('production_site', None)

    lastyear = datetime.date.today() - datetime.timedelta(days=365)
    
    iscc = ISCCCertificate.objects.filter(valid_until__gte=lastyear)
    dbs = DBSCertificate.objects.filter(valid_until__gte=lastyear)
    red = REDCertCertificate.objects.filter(valid_until__gte=lastyear)
    
    if q:
        iscc = iscc.filter(Q(certificate_id__icontains=q) | Q(certificate_holder__icontains=q))
        dbs = dbs.filter(Q(certificate_id__icontains=q) | Q(certificate_holder__icontains=q))
        red = red.filter(Q(certificate_id__icontains=q) | Q(certificate_holder__icontains=q))
    if entity_id:
        iscc = iscc.filter(entityiscctradingcertificate__entity__id=entity_id)
        dbs = dbs.filter(entitydbstradingcertificate__entity__id=entity_id)
        red = red.filter(entityredcerttradingcertificate__entity__id=entity_id)
    if production_site:
        iscc = iscc.filter(entityiscctradingcertificate__productionsitecertificate__production_site__id=production_site)
        dbs = dbs.filter(entitydbstradingcertificate__productionsitecertificate__production_site__id=production_site)
        red = red.filter(entityredcerttradingcertificate__productionsitecertificate__production_site__id=production_site)

    iscc = iscc[0:100]
    dbs = dbs[0:100]
    red = red[0:100]
    
    sez = [c.certificate_id for c in iscc]
    sez += [c.certificate_id for c in dbs]
    sez += [c.certificate_id for c in red]

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
    except Exception as e:
        print(e)
        return JsonResponse({'status': 'error', 'message': 'Unknown country_code %s' % (country)}, status=400)                        

    if depot_type not in ['EFS', 'EFPE', 'OTHER']:
        return JsonResponse({'status': 'error', 'message': 'Unknown depot type %s' % (depot_type)}, status=400)                        

    d = {'name': name, 'city': city, 'depot_type': depot_type, 'address': address, 
        'postal_code': postal_code}

    try:
        Depot.objects.update_or_create(depot_id=depot_id, country=country, defaults=d)
    except Exception as e:
        print(e)
        return JsonResponse({'status': 'error', 'message': 'Server error'}, status=500)
    return JsonResponse({'status': 'success'})


@otp_required
@check_rights('entity_id')
def get_controls(request, *args, **kwargs):
    context = kwargs['context']
    entity = context['entity']
    controls = Control.objects.filter(tx__lot__data_origin_entity=entity)
    sez = [c.natural_key() for c in controls]
    return JsonResponse({'status': 'success', 'data': sez})

@otp_required
def controls_upload_file(request):
    return JsonResponse({'status': 'success'})

@otp_required
def controls_add_message(request):
    control_id = request.POST.get('control_id', False)
    message = request.POST.get('message', False)

    if not control_id:
        return JsonResponse({'status': 'error', 'message': 'Please submit a control_id'}, status=400)
    if not message:
        return JsonResponse({'status': 'error', 'message': 'Please submit a message'}, status=400)

    try:
        control = Control.objects.get(id=control_id)
    except:
        return JsonResponse({'status': 'error', 'message': 'Could not find control'}, status=400)

    rights = {r.entity for r in UserRights.objects.filter(user=request.user)}
    if control.tx.lot.data_origin_entity not in rights:
        return JsonResponse({'status': 'error', 'message': 'Permission denied'}, status=403)

    # all good
    msg = ControlMessages()
    msg.control = control
    msg.user = request.user
    msg.entity = control.tx.lot.data_origin_entity
    msg.message = message
    msg.save()
    return JsonResponse({'status': 'success'})
