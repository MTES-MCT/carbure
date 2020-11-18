import datetime
from dateutil.relativedelta import *

from django.http import JsonResponse
from core.models import Entity, UserRights, LotV2, Pays, MatierePremiere, Biocarburant
from producers.models import ProductionSite, ProductionSiteInput, ProductionSiteOutput, ProducerCertificate
from core.decorators import check_rights
from core.models import ISCCCertificate, DBSCertificate, EntityISCCTradingCertificate, EntityDBSTradingCertificate


def get_settings(request):
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': "User is not authenticated"})

    # user-rights
    rights = UserRights.objects.filter(user=request.user)
    rights_sez = [{'entity': r.entity.natural_key(), 'rights': 'rw'} for r in rights]
    return JsonResponse({'status': 'success', 'data': {'rights': rights_sez, 'email': request.user.email}})


@check_rights('entity_id')
def get_production_sites(request, *args, **kwargs):
    context = kwargs['context']
    psites = ProductionSite.objects.filter(producer=context['entity'])

    psitesbyid = {p.id: p for p in psites}
    for k, v in psitesbyid.items():
        v.inputs = []
        v.outputs = []

    data = []

    for p in psites:
        psite_data = p.natural_key()
        psite_data['inputs'] = [i.natural_key() for i in p.productionsiteinput_set.all()]
        psite_data['outputs'] = [o.natural_key() for o in p.productionsiteoutput_set.all()]
        data.append(psite_data)

    return JsonResponse({'status': 'success', 'data': data})


def add_production_site(request):
    country = request.POST.get('country_code')
    name = request.POST.get('name')
    date_mise_en_service = request.POST.get('date_mise_en_service')
    ges_option = request.POST.get('ges_option')
    producer = request.POST.get('producer_id')

    eligible_dc = request.POST.get('eligible_dc')
    eligible_dc = eligible_dc == 'true'
    dc_reference = request.POST.get('dc_reference')

    site_id = request.POST.get('site_id')
    city = request.POST.get('city')
    postal_code = request.POST.get('postal_code')
    manager_name = request.POST.get('manager_name')
    manager_phone = request.POST.get('manager_phone')
    manager_email = request.POST.get('manager_email')

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
    if site_id is None:
        return JsonResponse({'status': 'error', 'message': "Missing site id"}, status=400)
    if postal_code is None:
        return JsonResponse({'status': 'error', 'message': "Missing postal code"}, status=400)
    if manager_name is None:
        return JsonResponse({'status': 'error', 'message': "Missing manager name"}, status=400)
    if manager_phone is None:
        return JsonResponse({'status': 'error', 'message': "Missing manager phone"}, status=400)
    if manager_email is None:
        return JsonResponse({'status': 'error', 'message': "Missing manager email"}, status=400)
    if city is None:
        return JsonResponse({'status': 'error', 'message': "Missing city"}, status=400)

    try:
        date_mise_en_service = datetime.datetime.strptime(date_mise_en_service, '%Y-%m-%d')
    except Exception:
        return JsonResponse({'status': 'error', 'message': "Date format should be YYYY-MM-DD"}, status=400)

    try:
        country = Pays.objects.get(code_pays=country)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': "Unknown country_code %s" % (country), 'extra': str(e)},
                            status=400)

    try:
        producer = Entity.objects.get(id=producer, entity_type='Producteur')
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': "Unknown producer %s" % (producer), 'extra': str(e)},
                            status=400)

    rights = [r.entity for r in UserRights.objects.filter(user=request.user)]
    if producer not in rights:
        return JsonResponse({'status': 'forbidden', 'message': "User not allowed to edit producer"}, status=403)

    try:
        obj, created = ProductionSite.objects.update_or_create(producer=producer, country=country, name=name, city=city,
            postal_code=postal_code, eligible_dc=eligible_dc, dc_reference=dc_reference, site_id=site_id, 
            manager_name=manager_name, manager_phone=manager_phone, manager_email=manager_email,
            date_mise_en_service=date_mise_en_service, ges_option=ges_option)

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': "Unknown error. Please contact an administrator",
                             'extra': str(e)}, status=400)
    return JsonResponse({'status': 'success', 'data': obj.natural_key() })


@check_rights('entity_id')
def update_production_site(request, *args, **kwargs):
    production_site_id = request.POST.get('production_site_id', False)

    if not production_site_id:
        return JsonResponse({'status': 'error', 'message': "Missing field production_site_id"}, status=400)

    psite = ProductionSite.objects.get(id=production_site_id)

    country_code = request.POST.get('country_code')
    name = request.POST.get('name')
    date_mise_en_service = request.POST.get('date_mise_en_service')
    ges_option = request.POST.get('ges_option')

    eligible_dc = request.POST.get('eligible_dc')
    eligible_dc = eligible_dc == 'true'
    dc_reference = request.POST.get('dc_reference')

    site_id = request.POST.get('site_id')
    city = request.POST.get('city')
    postal_code = request.POST.get('postal_code')
    manager_name = request.POST.get('manager_name')
    manager_phone = request.POST.get('manager_phone')
    manager_email = request.POST.get('manager_email')

    if name:
        psite.name = name
    if ges_option:
        psite.ges_option = ges_option
    if date_mise_en_service:
        psite.date_mise_en_service = date_mise_en_service
    if eligible_dc is not None:
        psite.eligible_dc = eligible_dc
    if dc_reference:
        psite.dc_reference = dc_reference
    if site_id:
        psite.site_id = site_id
    if city:
        psite.city = city
    if postal_code:
        psite.postal_code = postal_code
    if manager_name:
        psite.manager_name = manager_name
    if manager_phone:
        psite.manager_phone = manager_phone
    if manager_email:
        psite.manager_email = manager_email
    if country_code:
        try:
            country = Pays.objects.get(code_pays=country_code)
            psite.country = country
        except Exception:
            return JsonResponse({'status': 'error', 'message': "Unknown country"}, status=400)

    psite.save()
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
        return JsonResponse({'status': 'forbidden', 'message': "User not allowed to edit production site %s" % (site)},
                            status=403)

    # make sure there is no impact by deleting this
    lots = LotV2.objects.filter(carbure_production_site=ps, status='Validated')
    if len(lots) > 0:
        msg = "Validated lots associated with this production site. Cannot delete"
        return JsonResponse({'status': 'error', 'message': msg}, status=400)
    ps.delete()
    return JsonResponse({'status': 'success'})


def set_production_site_mp(request):
    site = request.POST.get('production_site_id')
    mp_list = request.POST.getlist('matiere_premiere_codes')

    if site is None:
        return JsonResponse({'status': 'error', 'message': "Missing production_site_id"}, status=400)
    if mp_list is None:
        return JsonResponse({'status': 'error', 'message': "Missing matiere_premiere_codes"}, status=400)

    try:
        mp_list = MatierePremiere.objects.filter(code__in=mp_list)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': "Unknown MP_list %s" % (mp_list), 'extra': str(e)}, status=400)

    try:
        ps = ProductionSite.objects.get(id=site)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': "Unknown Production Site", 'extra': str(e)}, status=400)

    # we have all the data, make sure we are allowed to delete it
    rights = [r.entity for r in UserRights.objects.filter(user=request.user)]
    if ps.producer not in rights:
        return JsonResponse({'status': 'forbidden', 'message': "User not allowed to edit production site %s" % (site)},
                            status=403)

    try:
        ProductionSiteInput.objects.filter(production_site=ps).delete()
        for mp in mp_list:
            obj, created = ProductionSiteInput.objects.update_or_create(production_site=ps, matiere_premiere=mp)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': "Unknown error. Please contact an administrator",
                             'extra': str(e)}, status=400)

    return JsonResponse({'status': 'success'})


def set_production_site_bc(request):
    site = request.POST.get('production_site_id')
    bc_list = request.POST.getlist('biocarburant_codes')

    if site is None:
        return JsonResponse({'status': 'error', 'message': "Missing production_site_id"}, status=400)
    if bc_list is None:
        return JsonResponse({'status': 'error', 'message': "Missing biocarburant_codes"}, status=400)

    try:
        bc_list = Biocarburant.objects.filter(code__in=bc_list)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': "Unknown BC_list %s" % (bc_list), 'extra': str(e)}, status=400)

    try:
        ps = ProductionSite.objects.get(id=site)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': "Unknown Production Site", 'extra': str(e)}, status=400)

    # we have all the data, make sure we are allowed to delete it
    rights = [r.entity for r in UserRights.objects.filter(user=request.user)]
    if ps.producer not in rights:
        return JsonResponse({'status': 'forbidden', 'message': "User not allowed to edit production site %s" % (site)},
                            status=403)

    try:
        ProductionSiteOutput.objects.filter(production_site=ps).delete()
        for bc in bc_list:
            obj, created = ProductionSiteOutput.objects.update_or_create(production_site=ps, biocarburant=bc)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': "Unknown error. Please contact an administrator",
                             'extra': str(e)}, status=400)

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
        return JsonResponse({'status': 'forbidden', 'message': "User not allowed to edit production site %s" % (site)},
                            status=403)

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
        return JsonResponse({'status': 'error', 'message': "Unknown matiere_premiere_code %s" % (mp), 'extra': str(e)},
                            status=400)

    try:
        ps = ProductionSite.objects.get(id=site)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': "Unknown Production Site", 'extra': str(e)}, status=400)

    # we have all the data, make sure we are allowed to delete it
    rights = [r.entity for r in UserRights.objects.filter(user=request.user)]
    if ps.producer not in rights:
        return JsonResponse({'status': 'forbidden', 'message': "User not allowed to edit production site %s" % (site)},
                            status=403)

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
        return JsonResponse({'status': 'error', 'message': "Unknown biocarburant_code %s" % (biocarburant),
                            'extra': str(e)}, status=400)

    try:
        site = ProductionSite.objects.get(id=site)
    except Exception:
        return JsonResponse({'status': 'error', 'message': "Unknown production site"}, status=400)

    # we have all the data, make sure we are allowed to delete it
    rights = [r.entity for r in UserRights.objects.filter(user=request.user)]
    if site.producer not in rights:
        return JsonResponse({'status': 'forbidden', 'message': "User not allowed to edit production site %s" % (site)},
                            status=403)

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
        return JsonResponse({'status': 'error', 'message': "Unknown biocarburant_code %s" % (biocarburant),
                            'extra': str(e)}, status=400)

    try:
        ps = ProductionSite.objects.get(id=site)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': "Unknown Production Site %s" % (site), 'extra': str(e)},
                            status=400)

    # we have all the data, make sure we are allowed to delete it
    rights = [r.entity for r in UserRights.objects.filter(user=request.user)]
    if ps.producer not in rights:
        return JsonResponse({'status': 'forbidden', 'message': "User not allowed to edit production site %s" % (site)},
                            status=403)

    try:
        obj = ProductionSiteOutput.objects.get(production_site=ps, biocarburant=biocarburant)
        obj.delete()
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': "Unknown error. Please contact an administrator",
                             'extra': str(e)}, status=400)
    return JsonResponse({'status': 'success'})


def enable_mac(request, *args, **kwargs):
    entity = request.POST.get('entity_id')

    try:
        entity = Entity.objects.get(id=entity, entity_type='Producteur')
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': "Unknown entity %s" % (entity), 'extra': str(e)},
                            status=400)

    # we have all the data, make sure we are allowed to delete it
    rights = [r.entity for r in UserRights.objects.filter(user=request.user)]
    if entity not in rights:
        return JsonResponse({'status': 'forbidden', 'message': "User not allowed to edit entity"}, status=403)

    entity.has_mac = True
    entity.save()
    return JsonResponse({'status': 'success'})


def disable_mac(request, *args, **kwargs):
    entity = request.POST.get('entity_id')

    try:
        entity = Entity.objects.get(id=entity, entity_type='Producteur')
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': "Unknown entity %s" % (entity), 'extra': str(e)},
                            status=400)

    # we have all the data, make sure we are allowed to delete it
    rights = [r.entity for r in UserRights.objects.filter(user=request.user)]
    if entity not in rights:
        return JsonResponse({'status': 'forbidden', 'message': "User not allowed to edit entity"}, status=403)

    entity.has_mac = False
    entity.save()
    return JsonResponse({'status': 'success'})


def enable_trading(request, *args, **kwargs):
    entity = request.POST.get('entity_id')

    try:
        entity = Entity.objects.get(id=entity, entity_type__in=['Producteur', 'Trader'])
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': "Unknown entity %s" % (entity), 'extra': str(e)},
                            status=400)

    # we have all the data, make sure we are allowed to delete it
    rights = [r.entity for r in UserRights.objects.filter(user=request.user)]
    if entity not in rights:
        return JsonResponse({'status': 'forbidden', 'message': "User not allowed to edit entity"}, status=403)

    entity.has_trading = True
    entity.save()
    return JsonResponse({'status': 'success'})


def disable_trading(request, *args, **kwargs):
    entity = request.POST.get('entity_id')

    try:
        entity = Entity.objects.get(id=entity, entity_type__in=['Producteur', 'Trader'])
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': "Unknown entity %s" % (entity), 'extra': str(e)},
                            status=400)

    # we have all the data, make sure we are allowed to delete it
    rights = [r.entity for r in UserRights.objects.filter(user=request.user)]
    if entity not in rights:
        return JsonResponse({'status': 'forbidden', 'message': "User not allowed to edit entity"}, status=403)

    entity.has_trading = False
    entity.save()
    return JsonResponse({'status': 'success'})


@check_rights('entity_id')
def get_iscc_certificates(request, *args, **kwargs):
    context = kwargs['context']
    one_year_ago = datetime.datetime.now() - relativedelta(years=1)
    objects = EntityISCCTradingCertificate.objects.filter(entity=context['entity'], certificate__valid_until__gte=one_year_ago)
    sez = [o.certificate.natural_key() for o in objects]
    return JsonResponse({'status': 'success', 'data': sez})


@check_rights('entity_id')
def get_2bs_certificates(request, *args, **kwargs):
    context = kwargs['context']
    one_year_ago = datetime.datetime.now() - relativedelta(years=1)
    objects = EntityDBSTradingCertificate.objects.filter(entity=context['entity'], certificate__valid_until__gte=one_year_ago)
    sez = [o.certificate.natural_key() for o in objects]
    return JsonResponse({'status': 'success', 'data': sez})


@check_rights('entity_id')
def add_iscc_certificate(request, *args, **kwargs):
    context = kwargs['context']
    certificate_id = request.POST.get('certificate_id', False)
    try:
        certificate = ISCCCertificate.objects.get(certificate_id=certificate_id)
    except Exception:
        return JsonResponse({'status': 'error', 'message': "Could not find requested certificate"}, status=400)

    EntityISCCTradingCertificate.objects.update_or_create(entity=context['entity'], certificate=certificate)
    return JsonResponse({'status': 'success'})


@check_rights('entity_id')
def add_2bs_certificate(request, *args, **kwargs):
    context = kwargs['context']
    certificate_id = request.POST.get('certificate_id', False)
    try:
        certificate = DBSCertificate.objects.get(certificate_id=certificate_id)
    except Exception:
        return JsonResponse({'status': 'error', 'message': "Could not find requested certificate"}, status=400)

    EntityDBSTradingCertificate.objects.update_or_create(entity=context['entity'], certificate=certificate)
    return JsonResponse({'status': 'success'})


@check_rights('entity_id')
def delete_iscc_certificate(request, *args, **kwargs):
    context = kwargs['context']
    certificate_id = request.POST.get('certificate_id', False)
    try:
        certificate = ISCCCertificate.objects.get(certificate_id=certificate_id)
    except Exception:
        return JsonResponse({'status': 'error', 'message': "Could not find requested certificate"}, status=400)

    EntityISCCTradingCertificate.objects.get(entity=context['entity'], certificate=certificate).delete()
    return JsonResponse({'status': 'success'})


@check_rights('entity_id')
def delete_2bs_certificate(request, *args, **kwargs):
    context = kwargs['context']
    certificate_id = request.POST.get('certificate_id', False)
    try:
        certificate = DBSCertificate.objects.get(certificate_id=certificate_id)
    except Exception:
        return JsonResponse({'status': 'error', 'message': "Could not find requested certificate"}, status=400)

    EntityDBSTradingCertificate.objects.get(entity=context['entity'], certificate=certificate).delete()
    return JsonResponse({'status': 'success'})
