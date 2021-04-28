import datetime
from dateutil.relativedelta import *

from django.http import JsonResponse
from django.db.models import Q
from django_otp.decorators import otp_required
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings

from core.models import Entity, UserRights, LotV2, Pays, MatierePremiere, Biocarburant, Depot, EntityDepot
from producers.models import ProductionSite, ProductionSiteInput, ProductionSiteOutput, ProducerCertificate
from core.decorators import check_rights, otp_or_403

from certificates.models import ISCCCertificate, DBSCertificate, REDCertCertificate
from certificates.models import EntityISCCTradingCertificate, EntityDBSTradingCertificate, EntityREDCertTradingCertificate
from certificates.models import ProductionSiteCertificate
from certificates.models import SNCategory, EntitySNTradingCertificate, SNCertificate

from core.models import UserRightsRequests
from api.v3.lots.views import get_entity_lots_by_status
from core.common import get_prefetched_data
from api.v3.sanity_checks import bulk_sanity_checks

@otp_or_403
def get_settings(request):
    # user-rights
    rights = UserRights.objects.filter(user=request.user)
    rights_sez = [{'entity': r.entity.natural_key(), 'rights': 'rw'} for r in rights]
    # requests
    requests = UserRightsRequests.objects.filter(user=request.user)
    requests_sez = [{'entity': r.entity.natural_key(), 'date': r.date_requested, 'status': r.status} for r in requests]
    return JsonResponse({'status': 'success', 'data': {'rights': rights_sez, 'email': request.user.email, 'requests': requests_sez}})


@check_rights('entity_id')
def update_entity(request, *args, **kwargs):
    context = kwargs['context']

    legal_name = request.POST.get('legal_name', False)
    registration_id = request.POST.get('registration_id', False)
    sustainability_officer_phone_number = request.POST.get('sustainability_officer_phone_number', False)
    sustainability_officer = request.POST.get('sustainability_officer', False)
    registered_address = request.POST.get('registered_address', False)

    entity = context['entity']
    if legal_name:
        entity.legal_name = legal_name
    if registration_id:
        entity.registration_id = registration_id
    if sustainability_officer_phone_number:
        entity.sustainability_officer_phone_number = sustainability_officer_phone_number
    if sustainability_officer:
        entity.sustainability_officer = sustainability_officer
    if registered_address:
        entity.registered_address = registered_address
    entity.save()
    return JsonResponse({'status': 'success'})


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

@check_rights('entity_id')
def add_production_site(request, *args, **kwargs):
    country = request.POST.get('country_code')
    name = request.POST.get('name')
    date_mise_en_service = request.POST.get('date_mise_en_service')
    ges_option = request.POST.get('ges_option')
    producer = request.POST.get('entity_id')

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


@otp_or_403
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


@otp_or_403
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

    # re-run sanity_checks on drafts
    entity = ps.producer
    drafts = get_entity_lots_by_status(entity, 'draft')
    prefetched_data = get_prefetched_data(entity)
    bulk_sanity_checks(drafts, prefetched_data, background=False)
    return JsonResponse({'status': 'success'})


@otp_or_403
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
    # re-run sanity_checks on drafts
    entity = ps.producer
    drafts = get_entity_lots_by_status(entity, 'draft')
    prefetched_data = get_prefetched_data(entity)
    bulk_sanity_checks(drafts, prefetched_data, background=False)
    return JsonResponse({'status': 'success'})


@check_rights('entity_id')
def get_delivery_sites(request, *args, **kwargs):
    entity = kwargs['context']['entity']

    try:
        ds = EntityDepot.objects.filter(entity=entity)
        ds = [d.natural_key() for d in ds]
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': "Could not find entity's delivery sites",
                             'extra': str(e)}, status=400)

    return JsonResponse({'status': 'success', 'data': ds})


@check_rights('entity_id')
def add_delivery_site(request, *args, **kwargs):
    entity = kwargs['context']['entity']
    delivery_site_id = request.POST.get('delivery_site_id', False)
    ownership_type = request.POST.get('ownership_type', False)

    blending_is_outsourced = request.POST.get('blending_outsourced', False)
    if blending_is_outsourced == "true":
        blending_is_outsourced = True
    else:
        blending_is_outsourced = False
    blending_entity_id = request.POST.get('blending_entity_id', False)

    if not delivery_site_id:
        return JsonResponse({'status': 'error', 'message': "Missing delivery site id"}, status=400)
    if not ownership_type:
        return JsonResponse({'status': 'error', 'message': "Missing ownership type"}, status=400)

    try:
        ds = Depot.objects.get(depot_id=delivery_site_id)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': "Could not find delivery site",
                             'extra': str(e)}, status=400)

    if entity.entity_type != 'Opérateur' and ds.depot_type == 'EFS':
        return JsonResponse({'status': 'error', 'message': "Only operators can register an EFS site"}, status=400)

    blender = None
    if blending_is_outsourced:
        try:
            blender = Entity.objects.get(id=blending_entity_id, entity_type='Opérateur')
        except:
            return JsonResponse({'status': 'error', 'message': "Could not find outsourcing blender"}, status=400)

    try:
        EntityDepot.objects.update_or_create(entity=entity, depot=ds, defaults={'ownership_type': ownership_type, 'blending_is_outsourced': blending_is_outsourced, 'blender': blender})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': "Could not link entity to delivery site",
                             'extra': str(e)}, status=400)

    return JsonResponse({'status': 'success'})


@check_rights('entity_id')
def delete_delivery_site(request, *args, **kwargs):
    entity = kwargs['context']['entity']
    delivery_site_id = request.POST.get('delivery_site_id', False)

    try:
        EntityDepot.objects.filter(entity=entity, depot__depot_id=delivery_site_id).delete()
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': "Could not delete entity's delivery site",
                             'extra': str(e)}, status=400)

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
    objects = EntityISCCTradingCertificate.objects.filter(entity=context['entity'], certificate__valid_until__gte=one_year_ago)[:100]
    sez = [o.natural_key() for o in objects]
    return JsonResponse({'status': 'success', 'data': sez})


@check_rights('entity_id')
def get_2bs_certificates(request, *args, **kwargs):
    context = kwargs['context']
    one_year_ago = datetime.datetime.now() - relativedelta(years=1)
    objects = EntityDBSTradingCertificate.objects.filter(entity=context['entity'], certificate__valid_until__gte=one_year_ago)[:100]
    sez = [o.natural_key() for o in objects]
    return JsonResponse({'status': 'success', 'data': sez})


@check_rights('entity_id')
def get_redcert_certificates(request, *args, **kwargs):
    context = kwargs['context']
    one_year_ago = datetime.datetime.now() - relativedelta(years=1)
    objects = EntityREDCertTradingCertificate.objects.filter(entity=context['entity'], certificate__valid_until__gte=one_year_ago)[:100]
    sez = [o.natural_key() for o in objects]
    return JsonResponse({'status': 'success', 'data': sez})


@check_rights('entity_id')
def get_sn_certificates(request, *args, **kwargs):
    context = kwargs['context']
    one_year_ago = datetime.datetime.now() - relativedelta(years=1)
    objects = EntitySNTradingCertificate.objects.filter(entity=context['entity'], certificate__valid_until__gte=one_year_ago)[:100]
    sez = [o.natural_key() for o in objects]
    return JsonResponse({'status': 'success', 'data': sez})


@check_rights('entity_id')
def add_iscc_certificate(request, *args, **kwargs):
    context = kwargs['context']
    certificate_id = request.POST.get('certificate_id', False)
    try:
        certificate = ISCCCertificate.objects.filter(certificate_id=certificate_id)[0]
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
def add_redcert_certificate(request, *args, **kwargs):
    context = kwargs['context']
    certificate_id = request.POST.get('certificate_id', False)
    try:
        certificate = REDCertCertificate.objects.get(certificate_id=certificate_id)
    except Exception as e:
        print(e)
        return JsonResponse({'status': 'error', 'message': "Could not find requested certificate"}, status=400)

    EntityREDCertTradingCertificate.objects.update_or_create(entity=context['entity'], certificate=certificate)
    return JsonResponse({'status': 'success'})


@check_rights('entity_id')
def add_sn_certificate(request, *args, **kwargs):
    context = kwargs['context']
    certificate_id = request.POST.get('certificate_id', False)
    try:
        certificate = SNCertificate.objects.get(certificate_id=certificate_id)
    except Exception as e:
        print(e)
        return JsonResponse({'status': 'error', 'message': "Could not find requested certificate"}, status=400)

    EntitySNTradingCertificate.objects.update_or_create(entity=context['entity'], certificate=certificate)
    return JsonResponse({'status': 'success'})


@check_rights('entity_id')
def delete_iscc_certificate(request, *args, **kwargs):
    entity = kwargs['context']['entity']
    certificate_id = request.POST.get('certificate_id', False)

    try:
        certificate = ISCCCertificate.objects.get(certificate_id=certificate_id)
        EntityISCCTradingCertificate.objects.get(entity=entity, certificate=certificate).delete()
        ProductionSiteCertificate.objects.filter(entity=entity, certificate_iscc__certificate=certificate).delete()
    except Exception:
        return JsonResponse({'status': 'error', 'message': "Could not delete requested certificate"}, status=400)

    return JsonResponse({'status': 'success'})


@check_rights('entity_id')
def delete_2bs_certificate(request, *args, **kwargs):
    entity = kwargs['context']['entity']
    certificate_id = request.POST.get('certificate_id', False)

    try:
        certificate = DBSCertificate.objects.get(certificate_id=certificate_id)
        EntityDBSTradingCertificate.objects.get(entity=entity, certificate=certificate).delete()
        ProductionSiteCertificate.objects.filter(entity=entity, certificate_2bs__certificate=certificate).delete()
    except Exception:
        return JsonResponse({'status': 'error', 'message': "Could not delete requested certificate"}, status=400)

    return JsonResponse({'status': 'success'})


@check_rights('entity_id')
def delete_redcert_certificate(request, *args, **kwargs):
    entity = kwargs['context']['entity']
    certificate_id = request.POST.get('certificate_id', False)

    try:
        certificate = REDCertCertificate.objects.get(certificate_id=certificate_id)
        EntityREDCertTradingCertificate.objects.get(entity=entity, certificate=certificate).delete()
        ProductionSiteCertificate.objects.filter(entity=entity, certificate_redcert__certificate=certificate).delete()
    except Exception:
        return JsonResponse({'status': 'error', 'message': "Could not delete requested certificate"}, status=400)

    return JsonResponse({'status': 'success'})


@check_rights('entity_id')
def delete_sn_certificate(request, *args, **kwargs):
    entity = kwargs['context']['entity']
    certificate_id = request.POST.get('certificate_id', False)

    try:
        certificate = SNCertificate.objects.get(certificate_id=certificate_id)
        EntitySNTradingCertificate.objects.get(entity=entity, certificate=certificate).delete()
        ProductionSiteCertificate.objects.filter(entity=entity, certificate_sn__certificate=certificate).delete()
    except Exception:
        return JsonResponse({'status': 'error', 'message': "Could not delete requested certificate"}, status=400)

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

    certificates_redcert = EntityREDCertTradingCertificate.objects.filter(Q(entity=context['entity']), Q(certificate__valid_until__gte=today),
        Q(certificate__certificate_id__icontains=query) | Q(certificate__certificate_holder__icontains=query))

    sez_data = [{'certificate_id': c.certificate.certificate_id, 'holder': c.certificate.certificate_holder, 'type': 'ISCC'} for c in certificates_iscc]
    sez_data += [{'certificate_id': c.certificate.certificate_id, 'holder': c.certificate.certificate_holder, 'type': '2BS'} for c in certificates_2bs]
    sez_data += [{'certificate_id': c.certificate.certificate_id, 'holder': c.certificate.certificate_holder, 'type': 'REDcert'} for c in certificates_redcert]
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
def update_iscc_certificate(request, *args, **kwargs):
    context = kwargs['context']
    entity = context['entity']
    old_certificate_id = request.POST.get('old_certificate_id', False)
    new_certificate_id = request.POST.get('new_certificate_id', False)

    if not old_certificate_id:
        return JsonResponse({'status': 'error', 'message': 'Please provide an old_certificate_id'}, status=400)
    if not new_certificate_id:
        return JsonResponse({'status': 'error', 'message': 'Please provide an new_certificate_id'}, status=400)

    # first, add the new certificate to the account
    try:
        new_certificate = ISCCCertificate.objects.get(certificate_id=new_certificate_id)
    except Exception:
        return JsonResponse({'status': 'error', 'message': "Could not find new requested certificate"}, status=400)
    new_certificate, _ = EntityISCCTradingCertificate.objects.update_or_create(entity=entity, certificate=new_certificate)

    # find old certificate
    try:
        old_certificate = EntityISCCTradingCertificate.objects.get(certificate__certificate_id=old_certificate_id)
    except Exception:
        return JsonResponse({'status': 'error', 'message': "Could not find old requested certificate"}, status=400)

    # then update previously linked certificates
    old_certificate.has_been_updated = True
    old_certificate.save()
    ProductionSiteCertificate.objects.filter(entity=entity, type='ISCC', certificate_iscc=old_certificate).update(certificate_iscc=new_certificate)
    return JsonResponse({'status': 'success'})


@check_rights('entity_id')
def update_2bs_certificate(request, *args, **kwargs):
    context = kwargs['context']
    entity = context['entity']
    old_certificate_id = request.POST.get('old_certificate_id', False)
    new_certificate_id = request.POST.get('new_certificate_id', False)

    if not old_certificate_id:
        return JsonResponse({'status': 'error', 'message': 'Please provide an old_certificate_id'}, status=400)
    if not new_certificate_id:
        return JsonResponse({'status': 'error', 'message': 'Please provide an new_certificate_id'}, status=400)

    # first, add the new certificate to the account
    try:
        new_certificate = DBSCertificate.objects.get(certificate_id=new_certificate_id)
    except Exception:
        return JsonResponse({'status': 'error', 'message': "Could not find new requested certificate"}, status=400)
    new_certificate, _ = EntityDBSTradingCertificate.objects.update_or_create(entity=entity, certificate=new_certificate)

    # find old certificate
    try:
        old_certificate = EntityDBSTradingCertificate.objects.get(certificate__certificate_id=old_certificate_id)
    except Exception:
        return JsonResponse({'status': 'error', 'message': "Could not find old requested certificate"}, status=400)

    # then update previously linked certificates
    old_certificate.has_been_updated = True
    old_certificate.save()
    ProductionSiteCertificate.objects.filter(entity=entity, type='2BS', certificate_2bs=old_certificate).update(certificate_2bs=new_certificate)
    return JsonResponse({'status': 'success'})


@check_rights('entity_id')
def update_redcert_certificate(request, *args, **kwargs):
    context = kwargs['context']
    entity = context['entity']
    old_certificate_id = request.POST.get('old_certificate_id', False)
    new_certificate_id = request.POST.get('new_certificate_id', False)

    if not old_certificate_id:
        return JsonResponse({'status': 'error', 'message': 'Please provide an old_certificate_id'}, status=400)
    if not new_certificate_id:
        return JsonResponse({'status': 'error', 'message': 'Please provide an new_certificate_id'}, status=400)

    # first, add the new certificate to the account
    try:
        new_certificate = REDCertCertificate.objects.get(certificate_id=new_certificate_id)
    except Exception:
        return JsonResponse({'status': 'error', 'message': "Could not find new requested certificate"}, status=400)
    new_certificate, _ = EntityREDCertTradingCertificate.objects.update_or_create(entity=entity, certificate=new_certificate)

    # find old certificate
    try:
        old_certificate = EntityREDCertTradingCertificate.objects.get(certificate__certificate_id=old_certificate_id)
    except Exception:
        return JsonResponse({'status': 'error', 'message': "Could not find old requested certificate"}, status=400)

    # then update previously linked certificates
    old_certificate.has_been_updated = True
    old_certificate.save()
    ProductionSiteCertificate.objects.filter(entity=entity, type='REDCERT', certificate_redcert=old_certificate).update(certificate_redcert=new_certificate)
    return JsonResponse({'status': 'success'})


@check_rights('entity_id')
def update_sn_certificate(request, *args, **kwargs):
    context = kwargs['context']
    entity = context['entity']
    old_certificate_id = request.POST.get('old_certificate_id', False)
    new_certificate_id = request.POST.get('new_certificate_id', False)

    if not old_certificate_id:
        return JsonResponse({'status': 'error', 'message': 'Please provide an old_certificate_id'}, status=400)
    if not new_certificate_id:
        return JsonResponse({'status': 'error', 'message': 'Please provide an new_certificate_id'}, status=400)

    # first, add the new certificate to the account
    try:
        new_certificate = SNCertificate.objects.get(certificate_id=new_certificate_id)
    except Exception:
        return JsonResponse({'status': 'error', 'message': "Could not find new requested certificate"}, status=400)
    new_certificate, _ = EntitySNTradingCertificate.objects.update_or_create(entity=entity, certificate=new_certificate)

    # find old certificate
    try:
        old_certificate = EntitySNTradingCertificate.objects.get(certificate__certificate_id=old_certificate_id)
    except Exception:
        return JsonResponse({'status': 'error', 'message': "Could not find old requested certificate"}, status=400)

    # then update previously linked certificates
    old_certificate.has_been_updated = True
    old_certificate.save()
    ProductionSiteCertificate.objects.filter(entity=entity, type='SN', certificate_sn=old_certificate).update(certificate_sn=new_certificate)
    return JsonResponse({'status': 'success'})


@otp_or_403
def request_entity_access(request):
    entity_id = request.POST.get('entity_id', False)
    comment = request.POST.get('comment', '')

    if not entity_id:
        return JsonResponse({'status': 'error', 'message': "Missing entity_id"}, status=400)

    try:
        entity = Entity.objects.get(id=entity_id)
    except Exception:
        return JsonResponse({'status': 'error', 'message': "Could not find entity"}, status=400)

    UserRightsRequests.objects.update_or_create(user=request.user, entity=entity, defaults={'comment': comment})

    email_subject = "Carbure - Demande d'accès"
    message = """ 
    Bonjour,
    Un utilisateur vient de faire une demande d'accès à CarbuRe

    Utilisateur: %s
    Société: %s
    Commentaire: %s
    """ % (request.user.email, entity.name, comment)

    send_mail(
        subject=email_subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=["carbure@beta.gouv.fr"],
        fail_silently=False,
    )
    return JsonResponse({'status': 'success'})
