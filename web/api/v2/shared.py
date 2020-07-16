from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Q

from core.decorators import enrich_with_user_details, restrict_to_producers

from core.models import Entity, Biocarburant, MatierePremiere, Depot, GHGValues, UserRights
from producers.models import ProductionSite, ProductionSiteInput, ProductionSiteOutput


@login_required
@enrich_with_user_details
def get_producers_autocomplete(request, *args, **kwargs):
    q = request.GET['query']
    rights = UserRights.objects.filter(user=request.user)
    ids = [r.entity.id for r in rights]
    entities = Entity.objects.filter(entity_type='Producteur', name__icontains=q, id__in=ids)
    return JsonResponse({'suggestions': [{'value': p.name, 'id': p.id} for p in entities]})


@login_required
@enrich_with_user_details
def get_clients_autocomplete(request, *args, **kwargs):
    q = request.GET['query']
    entities = Entity.objects.filter(entity_type__in=['Producteur', 'Trader', 'Opérateur'], name__icontains=q)
    return JsonResponse({'suggestions': [{'value': p.name, 'id': p.id} for p in entities]})


@login_required
@enrich_with_user_details
def get_depots_autocomplete(request, *args, **kwargs):
    q = request.GET['query']
    depots = Depot.objects.filter(Q(name__icontains=q) | Q(city__icontains=q) | Q(depot_id__icontains=q))
    results = [{'value': '%s - %s - %s' % (i.name, i.depot_id, i.city), 'name': i.name, 'depot_id': i.depot_id, 'city': i.city, 'country_code': i.country.code_pays, 'country_name': i.country.name} for i in depots]
    return JsonResponse({'suggestions': results})


@login_required
@enrich_with_user_details
def get_ges(request, *args, **kwargs):
    mp = request.GET.get('mp', None)
    bc = request.GET.get('bc', None)
    if not mp or not bc:
        return JsonResponse({'status': 'error', 'message': 'Missing matiere premiere or biocarburant'}, status=400)
    mp = MatierePremiere.objects.get(code=mp)
    bc = Biocarburant.objects.get(code=bc)
    default_values = {'eec': 0, 'el': 0, 'ep': 0, 'etd': 0, 'eu': 0.0, 'esca': 0, 'eccs': 0, 'eccr': 0, 'eee': 0,
                      'ghg_reference': 83.8}
    try:
        ges = GHGValues.objects.filter(matiere_premiere=mp, biocarburant=bc).order_by('-ep_default')[0]
        default_values['eec'] = ges.eec_default
        default_values['ep'] = ges.ep_default
        default_values['etd'] = ges.etd_default
    except Exception as e:
        # no default values
        print(e)
        pass
    return JsonResponse(default_values)


@login_required
@enrich_with_user_details
def get_prod_site_autocomplete(request, *args, **kwargs):
    context = kwargs['context']
    q = request.GET['query']
    producer = context['user_entity']
    production_sites = ProductionSite.objects.filter(producer=producer, name__icontains=q)
    return JsonResponse({'suggestions': [{'value': s.name, 'data': s.id, 'country': s.country.natural_key()} for s in production_sites]})


@login_required
@enrich_with_user_details
def get_biocarburants_autocomplete(request, *args, **kwargs):
    context = kwargs['context']
    q = request.GET['query']
    producer = context['user_entity']
    if producer.entity_type == 'Trader':
        bcs = Biocarburant.objects.all()
    else:

        production_site = request.GET.get('production_site', None)
        if production_site is None:
            ps = ProductionSite.objects.filter(producer=producer)
            outputs = ProductionSiteOutput.objects.filter(production_site__in=ps, biocarburant__name__icontains=q)\
                                                  .values('biocarburant').distinct()
        else:
            outputs = ProductionSiteOutput.objects.filter(production_site=production_site, biocarburant__name__icontains=q)\
                                                  .values('biocarburant').distinct()
        bcs = Biocarburant.objects.filter(id__in=outputs)
    return JsonResponse({'suggestions': [{'value': s.name, 'data': s.code} for s in bcs]})


@login_required
@enrich_with_user_details
def get_mps_autocomplete(request, *args, **kwargs):
    context = kwargs['context']
    q = request.GET['query']
    producer = context['user_entity']
    if producer.entity_type == 'Trader':
        mps = MatierePremiere.objects.all()
    else:
        production_site = request.GET.get('production_site', None)
        if production_site is None:
            ps = ProductionSite.objects.filter(producer=producer)
            inputs = ProductionSiteInput.objects.filter(production_site__in=ps, matiere_premiere__name__icontains=q)\
                                                .values('matiere_premiere').distinct()
        else:
            inputs = ProductionSiteInput.objects.filter(production_site=ps, matiere_premiere__name__icontains=q)\
                                                .values('matiere_premiere').distinct()
        mps = MatierePremiere.objects.filter(id__in=inputs)
    return JsonResponse({'suggestions': [{'value': s.name, 'data': s.code} for s in mps]})
