import datetime

from django.http import JsonResponse
from core.models import Entity, UserRights, LotV2, Pays, MatierePremiere, Biocarburant
from producers.models import ProductionSite, ProductionSiteInput, ProductionSiteOutput, ProducerCertificate


def get_settings(request):
    # user-rights
    rights = UserRights.objects.filter(user=request.user)
    rights_sez = [{'entity': r.entity.natural_key()} for r in rights]
    return JsonResponse({'status': 'success', 'data': {'rights': rights_sez}})


def add_production_site(request):
    country = request.POST.get('country_code')
    name = request.POST.get('name')
    date_mise_en_service = request.POST.get('date_mise_en_service')
    ges_option = request.POST.get('ges_option')
    producer = request.POST.get('producer_id')

    if country is None:
        return JsonResponse({'status': 'error', 'message': "Missing country_code"}, status=400)
    if name is None:
        return JsonResponse({'status': 'error', 'message': "Missing name"}, status=400)
    if date_mise_en_service is None:
        return JsonResponse({'status': 'error', 'message': "Missing date_mise_en_service"}, status=400)
    if ges_option is None:
        return JsonResponse({'status': 'error', 'message': "Missing ges_option"}, status=400)
    if producer is None:
        return JsonResponse({'status': 'error', 'message': "Missing producer"}, status=400)

    try:
        date_mise_en_service = datetime.datetime.strptime(date_mise_en_service, '%Y-%m-%d')
    except Exception:
        return JsonResponse({'status': 'error', 'message': "Date format should be YYYY-MM-DD"}, status=400)

    try:
        country = Pays.objects.get(code_pays=country)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': "Unknown country_code %s" % (country), 'extra': str(e)}, status=400)

    try:
        producer = Entity.objects.get(id=producer, entity_type='Producteur')
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': "Unknown producer %s" % (producer), 'extra': str(e)}, status=400)

    rights = [r.entity for r in UserRights.objects.filter(user=request.user)]
    if producer not in rights:
        return JsonResponse({'status': 'forbidden', 'message': "User not allowed to edit producer"}, status=403)

    try:
        obj, created = ProductionSite.objects.update_or_create(producer=producer, country=country, name=name,
                                                               defaults={'date_mise_en_service': date_mise_en_service, 'ges_option': ges_option})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': "Unknown error. Please contact an administrator",
                            'extra': str(e)}, status=400)
    return JsonResponse({'status': 'success'})


def delete_production_site(request):
    site = request.POST.get('production_site_id')
    try:
        ps = ProductionSite.objects.get(id=site)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': "Unknown Production Site", 'extra': str(e)}, status=400)

    # we have all the data, make sure we are allowed to delete it
    rights = [r.entity for r in UserRights.objects.filter(user=request.user)]
    if ps.producer not in rights:
        return JsonResponse({'status': 'forbidden', 'message': "User not allowed to edit production site %s" % (site)}, status=403)

    # make sure there is no impact by deleting this
    lots = LotV2.objects.filter(carbure_production_site=ps, status='Validated')
    if len(lots) > 0:
        return JsonResponse({'status': 'error', 'message': "Validated lots associated with this production site. Cannot delete"}, status=400)
    ps.delete()
    return JsonResponse({'status': 'success'})


def add_production_site_certificate(request):
    producer = request.POST.get('producer_id')
    certif_id = request.POST.get('certif_id')
    site = request.POST.get('production_site_id')
    form_file = request.FILES.get('file', None)
    form_exp_date = request.POST.get('expiration_date')

    if producer is None:
        return JsonResponse({'status': 'error', 'message': "Missing producer"}, status=400)
    try:
        producer = Entity.objects.get(id=producer, entity_type='Producteur')
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': "Unknown producer %s" % (producer), 'extra': str(e)}, status=400)

    rights = [r.entity for r in UserRights.objects.filter(user=request.user)]
    if producer not in rights:
        return JsonResponse({'status': 'forbidden', 'message': "User not allowed to edit producer"}, status=403)

    if certif_id is None:
        return JsonResponse({'status': 'error', 'message': "Missing certif_id"},
                            status=400)
    if form_exp_date is None:
        return JsonResponse({'status': 'error', 'message': "Missing expiration_date"},
                            status=400)
    try:
        exp_date = datetime.datetime.strptime(form_exp_date, '%Y-%m-%d')
    except Exception:
        return JsonResponse({'status': 'error', 'message': "Date format must be YYYY-MM-DD"},
                            status=400)

    if site is None:
        return JsonResponse({'status': 'error', 'message': "Missing production_site_id"},
                            status=400)
    try:
        site = ProductionSite.objects.get(producer=producer, id=site)
    except Exception:
        return JsonResponse({'status': 'error', 'message': "Unknown production_site"}, status=400)

    if form_file is None:
        return JsonResponse({'status': 'error', 'message': "Missing file"}, status=400)
    try:
        obj, c = ProducerCertificate.objects.update_or_create(producer=producer,
                                                              production_site=site, certificate_id=certif_id,
                                                              defaults={'expiration': exp_date,
                                                                        'certificate': form_file})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': "Unknown error. Please contact an administrator",
                             'extra': str(e)}, status=400)
    return JsonResponse({'status': 'success'})


def delete_production_site_certificate(request):
    certif_id = request.POST.get('certif_id')
    if certif_id is None:
        return JsonResponse({'status': 'error', 'message': "Veuillez entrer une valeur dans le champ Identifiant"},
                            status=400)

    try:
        crt = ProducerCertificate.objects.get(id=certif_id)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': "Unknown error. Please contact an administrator",
                             'extra': str(e)}, status=400)

    # we have all the data, make sure we are allowed to delete it
    rights = [r.entity for r in UserRights.objects.filter(user=request.user)]
    if crt.producer not in rights:
        return JsonResponse({'status': 'forbidden', 'message': "User not allowed"}, status=403)
    crt.delete()
    return JsonResponse({'status': 'success'})


def add_production_site_mp(request):
    site = request.POST.get('production_site_id')
    mp = request.POST.get('matiere_premiere_code')

    if site is None:
        return JsonResponse({'status': 'error', 'message': "Missing production_site_id"}, status=400)
    if mp is None:
        return JsonResponse({'status': 'error', 'message': "Missing matiere_premiere_code"}, status=400)

    try:
        mp = MatierePremiere.objects.get(code=mp)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': "Unknown MP %s" % (mp), 'extra': str(e)}, status=400)

    try:
        ps = ProductionSite.objects.get(id=site)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': "Unknown Production Site", 'extra': str(e)}, status=400)

    # we have all the data, make sure we are allowed to delete it
    rights = [r.entity for r in UserRights.objects.filter(user=request.user)]
    if ps.producer not in rights:
        return JsonResponse({'status': 'forbidden', 'message': "User not allowed to edit production site %s" % (site)}, status=403)

    try:
        obj, created = ProductionSiteInput.objects.update_or_create(production_site=site, matiere_premiere=mp)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': "Unknown error. Please contact an administrator",
                             'extra': str(e)}, status=400)
    return JsonResponse({'status': 'success'})


def delete_production_site_mp(request):
    site = request.POST.get('production_site_id')
    mp = request.POST.get('matiere_premiere_code')

    if site is None:
        return JsonResponse({'status': 'error', 'message': "Missing production_site_id"}, status=400)
    if mp is None:
        return JsonResponse({'status': 'error', 'message': "Missing matiere_premiere_code"}, status=400)

    try:
        mp = MatierePremiere.objects.get(code=mp)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': "Unknown matiere_premiere_code %s" % (mp), 'extra': str(e)}, status=400)

    try:
        ps = ProductionSite.objects.get(id=site)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': "Unknown Production Site", 'extra': str(e)}, status=400)

    # we have all the data, make sure we are allowed to delete it
    rights = [r.entity for r in UserRights.objects.filter(user=request.user)]
    if ps.producer not in rights:
        return JsonResponse({'status': 'forbidden', 'message': "User not allowed to edit production site %s" % (site)}, status=403)

    try:
        obj = ProductionSiteInput.objects.get(production_site=ps, matiere_premiere=mp)
        obj.delete()
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': "Unknown error. Please contact an administrator",
                             'extra': str(e)}, status=400)
    return JsonResponse({'status': 'success'})


def add_production_site_bc(request):
    site = request.POST.get('production_site_id')
    biocarburant = request.POST.get('biocarburant_code')

    if site is None:
        return JsonResponse({'status': 'error', 'message': "Missing production_site_id"}, status=400)
    if biocarburant is None:
        return JsonResponse({'status': 'error', 'message': "Missing biocarburant_code"}, status=400)

    try:
        biocarburant = Biocarburant.objects.get(code=biocarburant)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': "Unknown biocarburant_code %s" % (biocarburant), 'extra': str(e)}, status=400)

    try:
        site = ProductionSite.objects.get(id=site)
    except Exception:
        return JsonResponse({'status': 'error', 'message': "Unknown production site"}, status=400)

    # we have all the data, make sure we are allowed to delete it
    rights = [r.entity for r in UserRights.objects.filter(user=request.user)]
    if site.producer not in rights:
        return JsonResponse({'status': 'forbidden', 'message': "User not allowed to edit production site %s" % (site)}, status=403)

    try:
        obj, created = ProductionSiteOutput.objects.update_or_create(production_site=site, biocarburant=biocarburant)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': "Unknown error. Please contact an administrator",
                             'extra': str(e)}, status=400)
    return JsonResponse({'status': 'success'})


def delete_production_site_bc(request):
    site = request.POST.get('production_site_id')
    biocarburant = request.POST.get('biocarburant_code')

    if site is None:
        return JsonResponse({'status': 'error', 'message': "Missing production_site_id"}, status=400)
    if biocarburant is None:
        return JsonResponse({'status': 'error', 'message': "Missing biocarburant_code"}, status=400)

    try:
        biocarburant = Biocarburant.objects.get(code=biocarburant)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': "Unknown biocarburant_code %s" % (biocarburant), 'extra': str(e)}, status=400)

    try:
        ps = ProductionSite.objects.get(id=site)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': "Unknown Production Site %s" % (site), 'extra': str(e)}, status=400)

    # we have all the data, make sure we are allowed to delete it
    rights = [r.entity for r in UserRights.objects.filter(user=request.user)]
    if ps.producer not in rights:
        return JsonResponse({'status': 'forbidden', 'message': "User not allowed to edit production site %s" % (site)}, status=403)

    try:
        obj = ProductionSiteOutput.objects.get(production_site=ps, biocarburant=biocarburant)
        obj.delete()
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': "Unknown error. Please contact an administrator",
                             'extra': str(e)}, status=400)
    return JsonResponse({'status': 'success'})


def enable_mac(request, *args, **kwargs):
    producer = request.POST.get('producer_id')

    try:
        producer = Entity.objects.get(id=producer, entity_type='Producteur')
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': "Unknown Producer %s" % (producer), 'extra': str(e)}, status=400)

    # we have all the data, make sure we are allowed to delete it
    rights = [r.entity for r in UserRights.objects.filter(user=request.user)]
    if producer not in rights:
        return JsonResponse({'status': 'forbidden', 'message': "User not allowed to edit producer"}, status=403)

    producer.producer_with_mac = True
    producer.save()
    return JsonResponse({'status': 'success'})


def disable_mac(request, *args, **kwargs):
    producer = request.POST.get('producer_id')

    try:
        producer = Entity.objects.get(id=producer, entity_type='Producteur')
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': "Unknown Producer %s" % (producer), 'extra': str(e)}, status=400)

    # we have all the data, make sure we are allowed to delete it
    rights = [r.entity for r in UserRights.objects.filter(user=request.user)]
    if producer not in rights:
        return JsonResponse({'status': 'forbidden', 'message': "User not allowed to edit producer"}, status=403)

    producer.producer_with_mac = False
    producer.save()
    return JsonResponse({'status': 'success'})


def enable_trading(request, *args, **kwargs):
    producer = request.POST.get('producer_id')

    try:
        producer = Entity.objects.get(id=producer, entity_type='Producteur')
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': "Unknown Producer %s" % (producer), 'extra': str(e)}, status=400)

    # we have all the data, make sure we are allowed to delete it
    rights = [r.entity for r in UserRights.objects.filter(user=request.user)]
    if producer not in rights:
        return JsonResponse({'status': 'forbidden', 'message': "User not allowed to edit producer"}, status=403)

    producer.producer_with_trading = True
    producer.save()
    return JsonResponse({'status': 'success'})


def disable_trading(request, *args, **kwargs):
    producer = request.POST.get('producer_id')

    try:
        producer = Entity.objects.get(id=producer, entity_type='Producteur')
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': "Unknown Producer %s" % (producer), 'extra': str(e)}, status=400)

    # we have all the data, make sure we are allowed to delete it
    rights = [r.entity for r in UserRights.objects.filter(user=request.user)]
    if producer not in rights:
        return JsonResponse({'status': 'forbidden', 'message': "User not allowed to edit producer"}, status=403)

    producer.producer_with_trading = True
    producer.save()
    return JsonResponse({'status': 'success'})
