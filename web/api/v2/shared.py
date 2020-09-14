import datetime
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Q

from core.decorators import enrich_with_user_details

from core.models import Entity, Biocarburant, MatierePremiere, Depot, GHGValues, UserRights
from core.models import LotV2, LotTransaction, LotV2Error, TransactionError, TransactionComment, Pays
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


# not an http endpoint
def update_lot(lot, request, context):
    entity = context['user_entity']
    lot.data_origin_entity = entity
    lot.added_by = entity
    lot.added_by_user = request.user
    # easy fields first
    lot.unknown_producer = request.POST.get('unknown_producer_name', '')
    lot.unknown_production_site = request.POST.get('unknown_production_site_name', '')
    lot.unknown_production_site_reference = request.POST.get('unknown_production_site_reference', '')
    lot.unknown_production_site_dbl_counting = request.POST.get('unknown_production_site_dbl_counting', '')
    unknown_production_site_country_code = request.POST.get('unknown_production_site_country_code', '')
    try:
        country = Pays.objects.get(code_pays=unknown_production_site_country_code)
        lot.unknown_production_country = country
    except Exception:
        lot.unknown_production_country = None
    unknown_production_site_com_date = request.POST.get('unknown_production_site_com_date', '')
    if unknown_production_site_com_date == '':
        lot.unknown_production_site_com_date = None
    else:
        try:
            year = int(unknown_production_site_com_date[0:4])
            month = int(unknown_production_site_com_date[5:7])
            day = int(unknown_production_site_com_date[8:10])
            dd = datetime.date(year=year, month=month, day=day)
            lot.unknown_production_site_com_date = dd
            lot.period = dd.strftime('%Y-%m')
            LotV2Error.objects.filter(lot=lot, field='unknown_production_site_com_date').delete()
        except Exception as e:
            msg = "Format de date incorrect: veuillez entrer une date au format AAAA-MM-JJ"
            e, c = LotV2Error.objects.update_or_create(lot=lot, field='unknown_production_site_com_date',
                                                       error=msg,
                                                       defaults={'value': unknown_production_site_com_date})
    # producer
    producer_is_in_carbure = request.POST.get('producer_is_in_carbure', "no")
    if producer_is_in_carbure == "no":
        lot.producer_is_in_carbure = False
    else:
        lot.producer_is_in_carbure = True
    carbure_producer_id = request.POST.get('carbure_producer_id', None)
    carbure_producer_name = request.POST.get('carbure_producer_name', '')
    try:
        carbure_producer_id = int(carbure_producer_id)
        rights = [r.entity for r in UserRights.objects.filter(user=request.user)]
        producer = Entity.objects.get(id=carbure_producer_id, entity_type='Producteur')
        if producer in rights:
            lot.carbure_producer = producer
        else:
            lot.carbure_producer = None
            error, c = LotV2Error.objects.update_or_create(lot=lot, field='carbure_producer_name',
                                                           error='Producteur inconnu: %s' % (carbure_producer_name),
                                                           defaults={'value': carbure_producer_name})
    except Exception:
        lot.carbure_producer = None

    if lot.producer_is_in_carbure:
        lot.production_site_is_in_carbure = True
    else:
        lot.production_site_is_in_carbure = False

    carbure_production_site_id = request.POST.get('carbure_production_site_id', None)
    carbure_production_site_name = request.POST.get('carbure_production_site_name', '')
    if lot.producer_is_in_carbure:
        if carbure_production_site_id is not None and carbure_production_site_id != '':
            try:
                ps = ProductionSite.objects.get(id=int(carbure_production_site_id), producer=lot.carbure_producer)
                lot.carbure_production_site = ps
                LotV2Error.objects.filter(lot=lot, field='carbure_production_site_name').delete()
            except Exception:
                lot.carbure_production_site = None
                error, c = LotV2Error.objects.update_or_create(lot=lot, field='carbure_production_site_name',
                                                               error='Usine %s inconnue pour %s' % (carbure_production_site_name, lot.carbure_producer.name),
                                                               defaults={'value': carbure_production_site_name})
        else:
            lot.carbure_production_site = None
            error, c = LotV2Error.objects.update_or_create(lot=lot, field='carbure_production_site_name',
                                                           error='Veuillez renseigner une usine de production valide',
                                                           defaults={'value': carbure_production_site_name})

    biocarburant_code = request.POST.get('biocarburant_code', '')
    biocarburant_name = request.POST.get('biocarburant', '')
    if biocarburant_code == '':
        lot.biocarburant = None
        error, c = LotV2Error.objects.update_or_create(lot=lot, field='biocarburant',
                                                       error='Biocarburant inconnu',
                                                       defaults={'value': biocarburant_name})
    else:
        try:
            lot.biocarburant = Biocarburant.objects.get(code=biocarburant_code)
        except Exception:
            lot.biocarburant = None
            error, c = LotV2Error.objects.update_or_create(lot=lot, field='biocarburant',
                                                           error='Biocarburant inconnu',
                                                           defaults={'value': biocarburant_name})
    mp_code = request.POST.get('matiere_premiere_code', '')
    mp_name = request.POST.get('matiere_premiere', '')
    if mp_code == '':
        lot.matiere_premiere = None
        error, c = LotV2Error.objects.update_or_create(lot=lot, field='matiere_premiere',
                                                       error='Matière première inconnue',
                                                       defaults={'value': mp_name})
    else:
        try:
            lot.matiere_premiere = MatierePremiere.objects.get(code=mp_code)
        except Exception:
            lot.matiere_premiere = None
            error, c = LotV2Error.objects.update_or_create(lot=lot, field='matiere_premiere',
                                                           error='Matière Première inconnue',
                                                           defaults={'value': mp_name})

    volume = request.POST.get('volume', 0)
    try:
        lot.volume = float(volume)
        LotV2Error.objects.filter(lot=lot, field='volume').delete()
    except Exception:
        lot.volume = 0
        e, c = LotV2Error.objects.update_or_create(lot=lot, field='volume',
                                                   error='Format du volume incorrect', defaults={'value': volume})

    pays_origine = request.POST.get('pays_origine', '')
    pays_origine_code = request.POST.get('pays_origine_code', '')
    if pays_origine_code == '':
        lot.pays_origine = None
        error, c = LotV2Error.objects.update_or_create(lot=lot, field='pays_origine',
                                                       error="Merci de préciser le pays d'origine de la matière première",
                                                       defaults={'value': pays_origine})
    else:
        try:
            lot.pays_origine = Pays.objects.get(code_pays=pays_origine_code)
            LotV2Error.objects.filter(lot=lot, field='pays_origine_code').delete()
        except Exception:
            lot.pays_origine = None
            error, c = LotV2Error.objects.update_or_create(lot=lot, field='pays_origine',
                                                           error='Pays inconnu',
                                                           defaults={'value': pays_origine})
    lot.eec = 0
    eec = request.POST.get('eec', 0)
    try:
        lot.eec = float(eec)
    except Exception:
        error, c = LotV2Error.objects.update_or_create(lot=lot, field='eec',
                                                       error='Format non reconnu',
                                                       defaults={'value': eec})
    lot.el = 0
    el = request.POST.get('el', 0)
    try:
        lot.el = float(el)
    except Exception:
        error, c = LotV2Error.objects.update_or_create(lot=lot, field='el',
                                                       error='Format non reconnu',
                                                       defaults={'value': el})
    lot.ep = 0
    ep = request.POST.get('ep', 0)
    try:
        lot.ep = float(ep)
    except Exception:
        error, c = LotV2Error.objects.update_or_create(lot=lot, field='ep',
                                                       error='Format non reconnu',
                                                       defaults={'value': ep})
    lot.etd = 0
    etd = request.POST.get('etd', 0)
    try:
        lot.etd = float(etd)
    except Exception:
        error, c = LotV2Error.objects.update_or_create(lot=lot, field='etd',
                                                       error='Format non reconnu',
                                                       defaults={'value': etd})
    lot.eu = 0
    eu = request.POST.get('eu', 0)
    try:
        lot.eu = float(eu)
    except Exception:
        error, c = LotV2Error.objects.update_or_create(lot=lot, field='eu',
                                                       error='Format non reconnu',
                                                       defaults={'value': eu})
    lot.esca = 0
    esca = request.POST.get('esca', 0)
    try:
        lot.esca = float(esca)
    except Exception:
        error, c = LotV2Error.objects.update_or_create(lot=lot, field='esca',
                                                       error='Format non reconnu',
                                                       defaults={'value': esca})
    lot.eccs = 0
    eccs = request.POST.get('eccs', 0)
    try:
        lot.eccs = float(eccs)
    except Exception:
        error, c = LotV2Error.objects.update_or_create(lot=lot, field='eccs',
                                                       error='Format non reconnu',
                                                       defaults={'value': eccs})
    lot.eccr = 0
    eccr = request.POST.get('eccr', 0)
    try:
        lot.eccr = float(eccr)
    except Exception:
        error, c = LotV2Error.objects.update_or_create(lot=lot, field='eccr',
                                                       error='Format non reconnu',
                                                       defaults={'value': eccr})
    lot.eee = 0
    eee = request.POST.get('eee', 0)
    try:
        lot.eee = float(eee)
    except Exception:
        error, c = LotV2Error.objects.update_or_create(lot=lot, field='eee',
                                                       error='Format non reconnu',
                                                       defaults={'value': eee})
    # calculs ghg
    lot.ghg_total = round(lot.eec + lot.el + lot.ep + lot.etd + lot.eu - lot.esca - lot.eccs - lot.eccr - lot.eee, 2)
    lot.ghg_reference = 83.8
    lot.ghg_reduction = round((1.0 - (lot.ghg_total / lot.ghg_reference)) * 100.0, 2)
    lot.save()

# not an http endpoint
def update_tx(transaction, lot, request, context):
    transaction.unknown_client = request.POST.get('unknown_client', '')
    transaction.unknown_delivery_site = request.POST.get('unknown_delivery_site', '')
    unknown_delivery_site_country_code = request.POST.get('unknown_delivery_site_country_code', '')
    try:
        country = Pays.objects.get(code_pays=unknown_delivery_site_country_code)
        transaction.unknown_delivery_site_country = country
    except Exception:
        transaction.unknown_delivery_site_country = None

    transaction.dae = request.POST.get('dae', '')
    if transaction.dae == '':
        e, c = TransactionError.objects.update_or_create(tx=transaction, field='dae', error="Merci de préciser le numéro douanier (DAE/DAU..)",
                                                         defaults={'value': None})
    else:
        TransactionError.objects.filter(tx=transaction, field='dae').delete()

    client_is_in_carbure = request.POST.get('client_is_in_carbure', 'no')
    if client_is_in_carbure == 'no':
        transaction.client_is_in_carbure = False
    else:
        transaction.client_is_in_carbure = True
    carbure_client_id = request.POST.get('carbure_client_id', None)
    carbure_client_name = request.POST.get('carbure_client_name', '')
    try:
        client = Entity.objects.get(id=carbure_client_id)
        transaction.carbure_client = client
        TransactionError.objects.filter(tx=transaction, field='carbure_client_name').delete()
    except Exception:
        transaction.carbure_client = None
        e, c = TransactionError.objects.update_or_create(tx=transaction, field='carbure_client_name', error="%s introuvable dans Carbure" % (carbure_client_name),
                                                         defaults={'value': carbure_client_name})

    delivery_date = request.POST.get('delivery_date', '')
    if delivery_date == '':
        transaction.delivery_date = None
        lot.period = ''
        e, c = TransactionError.objects.update_or_create(tx=transaction, field='delivery_date',
                                                         error="Merci de préciser la date de livraison",
                                                         defaults={'value': None})
    else:
        try:
            year = int(delivery_date[0:4])
            month = int(delivery_date[5:7])
            day = int(delivery_date[8:10])
            dd = datetime.date(year=year, month=month, day=day)
            transaction.delivery_date = dd
            lot.period = dd.strftime('%Y-%m')
            TransactionError.objects.filter(tx=transaction, field='delivery_date').delete()
        except Exception:
            transaction.delivery_date = None
            msg = "Format de date incorrect: veuillez entrer une date au format AAAA-MM-JJ"
            e, c = TransactionError.objects.update_or_create(tx=transaction, field='delivery_date',
                                                             error=msg,
                                                             defaults={'value': delivery_date})

    transaction.champ_libre = request.POST.get('champ_libre', '')
    transaction.is_mac = True if request.POST.get('is_mac', False) == "yes" else False

    delivery_site_is_in_carbure = request.POST.get('delivery_site_is_in_carbure', 'no')
    if delivery_site_is_in_carbure == 'no':
        transaction.delivery_site_is_in_carbure = False
    else:
        transaction.delivery_site_is_in_carbure = True
    carbure_delivery_site_id = request.POST.get('carbure_delivery_site_id', None)
    carbure_delivery_site_name = request.POST.get('carbure_delivery_site_name', '')
    if carbure_delivery_site_id is None:
        transaction.carbure_delivery_site = None
    else:
        try:
            delivery_site = Depot.objects.get(depot_id=carbure_delivery_site_id)
            transaction.carbure_delivery_site = delivery_site
            TransactionError.objects.filter(tx=transaction, field='carbure_delivery_site_name').delete()

        except Exception:
            transaction.carbure_delivery_site = None
            e, c = TransactionError.objects.update_or_create(tx=transaction, field='carbure_delivery_site_name',
                                                             defaults={'value': carbure_delivery_site_name, 'error': "Site de livraison inconnu"})
    transaction.ghg_total = lot.ghg_total
    transaction.ghg_reduction = lot.ghg_reduction
    transaction.champ_libre = request.POST.get('champ_libre', '')


@login_required
@enrich_with_user_details
def save_lot(request, *args, **kwargs):
    context = kwargs['context']
    # new lot or edit?
    lot_id = request.POST.get('lot_id', None)
    tx_id = request.POST.get('tx_id', None)
    existing_lot = True
    can_edit_lot = False
    can_edit_tx = False

    if lot_id:
        try:
            lot = LotV2.objects.get(id=lot_id)
            if lot.data_origin_entity == context['user_entity'] or lot.added_by == context['user_entity']:
                can_edit_lot = True
            else:
                # user not allowed to modify Lot
                can_edit_lot = False
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': "Lot inconnu", 'extra': str(e)}, status=400)
    else:
        # create empty lot
        lot = LotV2()
        lot.source = 'MANUAL'
        existing_lot = False
        lot.save()
        can_edit_lot = True

    if can_edit_lot:
        update_lot(lot, request, context)

    if existing_lot is False:
        # create new TX
        transaction = LotTransaction()
        transaction.lot = lot
        transaction.vendor_is_in_carbure = True
        transaction.carbure_vendor = context['user_entity']
        transaction.save()
        can_edit_tx = True
    else:
        transaction = LotTransaction.objects.get(id=tx_id)
        # check rights
        if transaction.carbure_vendor == context['user_entity']:
            can_edit_tx = True
        else:
            can_edit_tx = False

    if can_edit_tx:
        update_tx(transaction, lot, request, context)

    transaction.save()
    lot.blocking_sanity_checked_passed = False
    lot.nonblocking_sanity_checked_passed = False
    lot.save()

    if not can_edit_tx and not can_edit_lot:
        return JsonResponse({'status': 'error', 'message': "Permission denied"}, status=403)
    return JsonResponse({'status': 'success', 'lot_id': lot.id, 'transaction_id': transaction.id})


@login_required
@enrich_with_user_details
def add_lot_correction(request, *args, **kwargs):
    context = kwargs['context']
    # new lot or edit?
    tx_id = request.POST.get('tx_id', None)
    tx_comment = request.POST.get('comment', '')
    if tx_id is None:
        return JsonResponse({'status': 'error', 'message': "Missing TX ID from POST data"}, status=400)
    if tx_comment == '':
        return JsonResponse({'status': 'error', 'message': "Un commentaire est obligatoire"}, status=400)
    try:
        tx = LotTransaction.objects.get(delivery_status__in=['N', 'AC', 'AA', 'R'], id=tx_id)
        if tx.lot.data_origin_entity != context['user_entity'] and tx.carbure_vendor != context['user_entity']:
            return JsonResponse({'status': 'error', 'message': "Permission Denied"}, status=403)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': "Transaction inconnue", 'extra': str(e)}, status=400)
    tx.delivery_status = 'AA'
    tx.save()
    txc = TransactionComment()
    txc.entity = context['user_entity']
    txc.tx = tx
    txc.comment = tx_comment
    txc.save()
    return JsonResponse({'status': 'success', 'tx_id': tx.id})
