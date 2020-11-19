import datetime
from dateutil.relativedelta import *

from django.http import JsonResponse
from django.db.models import Q
from core.models import Entity, UserRights, LotV2, Pays, MatierePremiere, Biocarburant
from producers.models import ProductionSite, ProductionSiteInput, ProductionSiteOutput, ProducerCertificate
from core.decorators import check_rights
from core.models import ISCCCertificate, DBSCertificate, EntityISCCTradingCertificate, EntityDBSTradingCertificate
from core.models import ProductionSiteCertificate


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

    for ps in psites:
        psite_data = ps.natural_key()
        psite_data['inputs'] = [i.natural_key() for i in ps.productionsiteinput_set.all()]
        psite_data['outputs'] = [o.natural_key() for o in ps.productionsiteoutput_set.all()]
        certificates = []
        for pc in ps.productionsitecertificate_set.all():
            c = pc.certificate_iscc.certificate if pc.type == 'ISCC' else pc.certificate_2bs.certificate
            certificates.append({'certificate_id': c.certificate_id, 'holder': c.certificate_holder, 'type': pc.type})
        psite_data['certificates'] = certificates 
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


@check_rights('entity_id')
def set_national_system_certificate(request, *args, **kwargs):
    entity = kwargs['context']['entity']
    national_system_certificate = request.POST.get('national_system_certificate', False)

    if entity.entity_type != 'Opérateur':
        return JsonResponse({'status': 'error', 'message': "Only operators can be given a national system certificate"}, status=400)

    if not national_system_certificate:
        return JsonResponse({'status': 'error', 'message': "Missing national system certificate"}, status=400)
    
    entity.national_system_certificate = national_system_certificate
    entity.save()
    return JsonResponse({'status': 'success'})


@check_rights('entity_id')
def enable_mac(request, *args, **kwargs):
    entity = kwargs['context']['entity']
    entity.has_mac = True
    entity.save()
    return JsonResponse({'status': 'success'})


@check_rights('entity_id')
def disable_mac(request, *args, **kwargs):
    entity = kwargs['context']['entity']
    entity.has_mac = False
    entity.save()
    return JsonResponse({'status': 'success'})

@check_rights('entity_id')
def enable_trading(request, *args, **kwargs):
    entity = kwargs['context']['entity']

    if entity.entity_type not in ['Producteur', 'Trader']:
        return JsonResponse({'status': 'error', 'message': "This entity cannot have a trading activity"}, status=400)

    entity.has_trading = True
    entity.save()
    return JsonResponse({'status': 'success'})

@check_rights('entity_id')
def disable_trading(request, *args, **kwargs):
    entity = kwargs['context']['entity']

    if entity.entity_type not in ['Producteur', 'Trader']:
        return JsonResponse({'status': 'error', 'message': "This entity cannot have a trading activity"}, status=400)

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


@check_rights('entity_id')
def get_my_certificates(request, *args, **kwargs):
    context = kwargs['context']
    query = request.GET.get('query', '')
    today = datetime.date.today()

    certificates_iscc = EntityISCCTradingCertificate.objects.filter(Q(entity=context['entity']), Q(certificate__valid_until__gte=today), 
        Q(certificate__certificate_id__icontains=query) | Q(certificate__certificate_holder__icontains=query))

    certificates_2bs = EntityDBSTradingCertificate.objects.filter(Q(entity=context['entity']), Q(certificate__valid_until__gte=today), 
        Q(certificate__certificate_id__icontains=query) | Q(certificate__certificate_holder__icontains=query))

    sez_data = [{'certificate_id': c.certificate.certificate_id, 'holder': c.certificate.certificate_holder, 'type': 'ISCC'} for c in certificates_iscc]
    sez_data += [{'certificate_id': c.certificate.certificate_id, 'holder': c.certificate.certificate_holder, 'type': '2BS'} for c in certificates_2bs]
    return JsonResponse({'status': 'success', 'data': sez_data})


@check_rights('entity_id')
def set_production_site_certificates(request, *args, **kwargs):
    context = kwargs['context']
    certificate_ids = request.POST.getlist('certificate_ids')
    production_site_id = request.POST.get('production_site_id', False)

    try:
        psite = ProductionSite.objects.get(pk=production_site_id)
    except Exception:
        return JsonResponse({'status': 'error', 'message': "Could not find requested production site"}, status=400)
 
    try:
        certificates_iscc = EntityISCCTradingCertificate.objects.filter(certificate__certificate_id__in=certificate_ids)
        certificate_2bs = EntityDBSTradingCertificate.objects.filter(certificate__certificate_id__in=certificate_ids)
    except Exception:
        return JsonResponse({'status': 'error', 'message': "Could not find requested certificates"}, status=400)

    try:
        ProductionSiteCertificate.objects.filter(entity=context['entity'], production_site=psite).delete()
        psc_iscc = [ProductionSiteCertificate(entity=context['entity'], production_site=psite, type='ISCC', certificate_2bs=None, certificate_iscc=c) for c in certificates_iscc]
        psc_2bs = [ProductionSiteCertificate(entity=context['entity'], production_site=psite, type='2BS', certificate_2bs=c, certificate_iscc=None) for c in certificate_2bs]
        ProductionSiteCertificate.objects.bulk_create(psc_iscc + psc_2bs)
    except Exception:
        return JsonResponse({'status': 'error', 'message': "Could not update production site certificates"}, status=400)
        
    return JsonResponse({'status': 'success'})

@check_rights('entity_id')
def add_production_site_certificate(request, *args, **kwargs):
    context = kwargs['context']
    certificate_id = request.POST.get('certificate_id', False)
    certificate_type = request.POST.get('certificate_type', False)

    certificate_iscc = None
    certificate_2bs = None
    try:
        if certificate_type == 'ISCC':
            certificate_iscc = EntityISCCTradingCertificate.objects.get(certificate_id=certificate_id)
        else:
            certificate_2bs = EntityDBSTradingCertificate.objects.get(certificate_id=certificate_id)
    except Exception:
        return JsonResponse({'status': 'error', 'message': "Could not find requested certificate"}, status=400)

    ProductionSiteCertificate.objects.update_or_create(entity=context['entity'], type=certificate_type, certificate_2bs=certificate_2bs, certificate_iscc=certificate_iscc)
    return JsonResponse({'status': 'success'})



@check_rights('entity_id')
def delete_production_site_certificate(request, *args, **kwargs):
    context = kwargs['context']
    certificate_id = request.POST.get('certificate_id', False)
    certificate_type = request.POST.get('certificate_type', False)

    if not certificate_id:
        return JsonResponse({'status': 'error', 'message': 'Please provide a certificate_id'}, status=400)
    if not certificate_type:
        return JsonResponse({'status': 'error', 'message': 'Please provide a certificate_type'}, status=400)

    try:
        if certificate_type == 'ISCC':
            ProductionSiteCertificate.objects.get(entity=context['entity'], type=certificate_type, certificate_iscc__certificate_id=certificate_id).delete()
        else:
            ProductionSiteCertificate.objects.get(entity=context['entity'], type=certificate_type, certificate_2bs__certificate_id=certificate_id).delete()
    except Exception:
        return JsonResponse({'status': 'error', 'message': "Could not find requested certificate"}, status=400)

    return JsonResponse({'status': 'success'})
