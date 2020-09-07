import random
import csv
import datetime

from django.contrib.auth.decorators import login_required
from django.db.models import Max
from django.http import JsonResponse, HttpResponse

from core.decorators import enrich_with_user_details, restrict_to_producers
from core.models import Biocarburant, MatierePremiere, Pays, Entity, GHGValues
from producers.models import ProductionSite, ProductionSiteOutput, ProductionSiteInput, ProducerCertificate
from core.xlsx_template import create_template_xlsx


def get_random(model):
    max_id = model.objects.all().aggregate(max_id=Max("id"))['max_id']
    while True:
        pk = random.randint(1, max_id)
        element = model.objects.filter(pk=pk).first()
        if element:
            return element


@login_required
@enrich_with_user_details
@restrict_to_producers
def producers_import_excel_template(request, *args, **kwargs):
    context = kwargs['context']
    file_location = create_template_xlsx(context['user_entity'])
    try:
        with open(file_location, 'rb') as f:
            file_data = f.read()
            # sending response
            response = HttpResponse(file_data, content_type='application/vnd.ms-excel')
            response['Content-Disposition'] = 'attachment; filename="carbure_template.xlsx"'
            return response
    except Exception as e:
        return JsonResponse({'status': "error", 'message': "Error creating template file", 'error': str(e)}, status=500)


@login_required
@enrich_with_user_details
@restrict_to_producers
def producers_prod_site_autocomplete(request, *args, **kwargs):
    context = kwargs['context']
    q = request.GET['query']
    producer = context['user_entity']
    production_sites = ProductionSite.objects.filter(producer=producer, name__icontains=q)
    return JsonResponse({'suggestions': [{'value': s.name, 'data': s.id, 'country': s.country.natural_key()} for s in production_sites]})


@login_required
@enrich_with_user_details
@restrict_to_producers
def producers_biocarburant_autocomplete(request, *args, **kwargs):
    context = kwargs['context']
    q = request.GET['query']
    producer = context['user_entity']
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
@restrict_to_producers
def producers_mp_autocomplete(request, *args, **kwargs):
    context = kwargs['context']
    q = request.GET['query']
    producer = context['user_entity']
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


@login_required
@enrich_with_user_details
@restrict_to_producers
def producers_ges(request, *args, **kwargs):
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
@restrict_to_producers
def producers_settings_add_certif(request, *args, **kwargs):
    context = kwargs['context']

    certif_id = request.POST.get('certif_id')
    if certif_id is None:
        return JsonResponse({'status': 'error', 'message': "Veuillez entrer une valeur dans le champ Identifiant"},
                            status=400)
    form_exp_date = request.POST.get('expiration')
    if form_exp_date is None:
        return JsonResponse({'status': 'error', 'message': "Veuillez entrer une valeur dans le champ Expiration"},
                            status=400)
    try:
        exp_date = datetime.datetime.strptime(form_exp_date, '%d/%m/%Y')
    except Exception:
        return JsonResponse({'status': 'error', 'message': "Veuillez entrer une date valide au format DD/MM/YYYY"},
                            status=400)

    site = request.POST.get('site')
    if site is None:
        return JsonResponse({'status': 'error', 'message': "Veuillez entrer une valeur dans le champ  Site"},
                            status=400)
    try:
        site = ProductionSite.objects.get(producer=context['user_entity'], id=site)
    except Exception:
        return JsonResponse({'status': 'error', 'message': "Site de production inconnu"}, status=400)

    form_file = request.FILES.get('file', None)
    if form_file is None:
        return JsonResponse({'status': 'error', 'message': "Veuillez sélectionner un certificat (fichier PDF)"},
                            status=400)
    try:
        obj, c = ProducerCertificate.objects.update_or_create(producer=context['user_entity'],
                                                              production_site=site, certificate_id=certif_id,
                                                              defaults={'expiration': exp_date,
                                                                        'certificate': form_file})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': "Unknown error. Please contact an administrator",
                             'extra': str(e)}, status=400)
    return JsonResponse({'status': 'success', 'message': 'Certificate added'})


@login_required
@enrich_with_user_details
@restrict_to_producers
def producers_settings_delete_certif(request, *args, **kwargs):
    context = kwargs['context']

    certif_id = request.POST.get('certif_id')
    if certif_id is None:
        return JsonResponse({'status': 'error', 'message': "Veuillez entrer une valeur dans le champ Identifiant"},
                            status=400)

    try:
        crt = ProducerCertificate.objects.get(id=certif_id, producer=context['user_entity'])
        crt.delete()
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': "Unknown error. Please contact an administrator",
                             'extra': str(e)}, status=400)
    return JsonResponse({'status': 'success', 'message': 'Certificate deleted'})


@login_required
@enrich_with_user_details
@restrict_to_producers
def producers_settings_add_site(request, *args, **kwargs):
    context = kwargs['context']

    country = request.POST.get('country')
    name = request.POST.get('name')
    date_mise_en_service = request.POST.get('date_mise_en_service')
    ges_option = request.POST.get('ges_option')

    if country is None:
        return JsonResponse({'status': 'error', 'message': "Veuillez entrer une valeur dans le champ Pays"}, status=400)
    if name is None:
        return JsonResponse({'status': 'error', 'message': "Veuillez entrer une valeur dans le champ Nom"}, status=400)
    if date_mise_en_service is None:
        return JsonResponse({'status': 'error',
                            'message': "Veuillez entrer une date dans le champ Date de mise en service"}, status=400)

    try:
        date_mise_en_service = datetime.datetime.strptime(date_mise_en_service, '%d/%m/%Y')
    except Exception:
        return JsonResponse({'status': 'error', 'message': "Veuillez entrer une date valide au format DD/MM/YYYY"},
                            status=400)

    try:
        country = Pays.objects.get(name__icontains=country)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': "Veuillez choisir un Pays dans la liste", 'extra': str(e)},
                            status=400)

    try:
        obj, created = ProductionSite.objects.update_or_create(producer=context['user_entity'], country=country,
                                                               name=name,
                                                               defaults={'date_mise_en_service': date_mise_en_service, 'ges_option': ges_option})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': "Unknown error. Please contact an administrator",
                            'extra': str(e)}, status=400)
    return JsonResponse({'status': 'success', 'message': 'Site added'})


@login_required
@enrich_with_user_details
@restrict_to_producers
def producers_settings_add_mp(request, *args, **kwargs):
    context = kwargs['context']

    site = request.POST.get('site')
    mp = request.POST.get('matiere_premiere')

    if site is None:
        return JsonResponse({'status': 'error', 'message': "Please provide a value in field Site"}, status=400)
    if mp is None:
        return JsonResponse({'status': 'error', 'message': "Please provide a value in field Matiere Premiere"},
                            status=400)

    try:
        mp = MatierePremiere.objects.get(code=mp)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': "Please provide a valid Matiere Premiere from the list",
                             'extra': str(e)}, status=400)

    try:
        site = ProductionSite.objects.get(producer=context['user_entity'], id=site)
    except Exception:
        return JsonResponse({'status': 'error', 'message': "Could not find production site in database"}, status=400)

    try:
        obj, created = ProductionSiteInput.objects.update_or_create(production_site=site, matiere_premiere=mp)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': "Unknown error. Please contact an administrator",
                             'extra': str(e)}, status=400)
    return JsonResponse({'status': 'success', 'message': 'MP added'})


@login_required
@enrich_with_user_details
@restrict_to_producers
def producers_settings_add_biocarburant(request, *args, **kwargs):
    context = kwargs['context']
    site = request.POST.get('site')
    biocarburant = request.POST.get('biocarburant')

    if site is None:
        return JsonResponse({'status': 'error', 'message': "Please provide a value in field Site"}, status=400)
    if biocarburant is None:
        return JsonResponse({'status': 'error', 'message': "Please provide a value in field Biocarburant"}, status=400)

    try:
        biocarburant = Biocarburant.objects.get(code=biocarburant)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': "Please provide a valid Biocarburant from the list",
                             'extra': str(e)}, status=400)

    try:
        site = ProductionSite.objects.get(producer=context['user_entity'], id=site)
    except Exception:
        return JsonResponse({'status': 'error', 'message': "Could not find production site in database"}, status=400)

    try:
        obj, created = ProductionSiteOutput.objects.update_or_create(production_site=site, biocarburant=biocarburant)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': "Unknown error. Please contact an administrator",
                             'extra': str(e)}, status=400)
    return JsonResponse({'status': 'success', 'message': 'Biocarburant added'})


@login_required
@enrich_with_user_details
@restrict_to_producers
def producers_settings_delete_mp(request, *args, **kwargs):
    context = kwargs['context']
    site = request.POST.get('site')
    mp = request.POST.get('matiere_premiere')

    if site is None:
        return JsonResponse({'status': 'error', 'message': "Missing Site"}, status=400)
    if mp is None:
        return JsonResponse({'status': 'error', 'message': "Missing MP"}, status=400)

    try:
        mp = MatierePremiere.objects.get(code=mp)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': "Unknown MP", 'extra': str(e)}, status=400)

    try:
        ps = ProductionSite.objects.get(id=site, producer=context['user_entity'])
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': "Unknown Production Site", 'extra': str(e)}, status=400)

    try:
        obj = ProductionSiteInput.objects.get(production_site=ps, matiere_premiere=mp)
        obj.delete()
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': "Unknown error. Please contact an administrator",
                             'extra': str(e)}, status=400)
    return JsonResponse({'status': 'success', 'message': 'MP deleted'})


@login_required
@enrich_with_user_details
@restrict_to_producers
def producers_settings_delete_biocarburant(request, *args, **kwargs):
    context = kwargs['context']
    site = request.POST.get('site')
    biocarburant = request.POST.get('biocarburant')

    if site is None:
        return JsonResponse({'status': 'error', 'message': "Missing Site"}, status=400)
    if biocarburant is None:
        return JsonResponse({'status': 'error', 'message': "Missing BC"}, status=400)

    try:
        biocarburant = Biocarburant.objects.get(code=biocarburant)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': "Unknown BC", 'extra': str(e)}, status=400)

    try:
        ps = ProductionSite.objects.get(id=site, producer=context['user_entity'])
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': "Unknown Production Site", 'extra': str(e)}, status=400)

    try:
        obj = ProductionSiteOutput.objects.get(production_site=ps, biocarburant=biocarburant)
        obj.delete()
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': "Unknown error. Please contact an administrator",
                             'extra': str(e)}, status=400)
    return JsonResponse({'status': 'success', 'message': 'BC deleted'})
