import random
import openpyxl
import datetime
import io

from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Max, Min
from django.core import serializers
from django.db.models.fields import NOT_PROVIDED
from django.db.models import Q

from core.decorators import enrich_with_user_details, restrict_to_producers
from core.xlsx_template import create_template_xlsx_v2_simple, create_template_xlsx_v2_advanced, create_template_xlsx_v2_mb

from core.models import Entity, ProductionSite, Pays, Biocarburant, MatierePremiere, Depot
from core.models import LotV2, LotTransaction, TransactionError, LotV2Error, UserRights, TransactionComment


@login_required
@enrich_with_user_details
@restrict_to_producers
def delete_lots(request, *args, **kwargs):
    context = kwargs['context']
    lot_ids = request.POST.get('lots', None)
    errors = []
    if not lot_ids:
        return JsonResponse({'status': 'error', 'message': 'Missing lot ids'}, status=400)
    ids = lot_ids.split(',')
    for lotid in ids:
        lot = LotV2.objects.get(id=lotid, added_by=context['user_entity'], status='Draft')
        try:
            lot.delete()
        except Exception as e:
            errors.append({'message': 'Impossible de supprimer le lot %s: introuvable ou déjà validé' % (), 'extra': str(e)})
    return JsonResponse({'status': 'success', 'message': '%d lots supprimés' % (len(ids) - len(errors)), 'errors': errors})


@login_required
@enrich_with_user_details
@restrict_to_producers
def delete_mb_drafts_lots(request, *args, **kwargs):
    context = kwargs['context']
    lot_ids = request.POST.get('lots', None)
    errors = []
    if not lot_ids:
        return JsonResponse({'status': 'error', 'message': 'Missing lot ids'}, status=400)
    ids = lot_ids.split(',')
    for lotid in ids:
        try:
            lot = LotV2.objects.get(id=lotid)
            lot.delete()
        except Exception as e:
            errors.append({'message': 'Impossible de supprimer le lot %s: introuvable ou déjà validé' % (lotid), 'extra': str(e)})
    print(errors)
    return JsonResponse({'status': 'success', 'message': '%d lots supprimés' % (len(ids) - len(errors)), 'errors': errors})


@login_required
@enrich_with_user_details
@restrict_to_producers
def duplicate_lot(request, *args, **kwargs):
    context = kwargs['context']
    tx_id = request.POST.get('tx_id', None)
    try:
        tx = LotTransaction.objects.get(id=tx_id, carbure_vendor=context['user_entity'])
        lot = tx.lot
        lot.pk = None
        lot.save()
        tx.pk = None
        tx.lot = lot
        tx.save()
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': 'Could not find lot to duplicate', 'extra':str(e)})
    # hardcoded fields to remove
    lot_fields_to_remove = ['carbure_id', 'status']
    tx_fields_to_remove = ['dae', 'ea_delivery_status']
    # optional fields to remove (user configuration)
    lot_meta_fields = {f.name: f for f in LotV2._meta.get_fields()}
    tx_meta_fields = {f.name: f for f in LotTransaction._meta.get_fields()}
    for f in lot_fields_to_remove:
        if f in lot_meta_fields:
            meta_field = lot_meta_fields[f]
            if meta_field.default != NOT_PROVIDED:
                setattr(lot, f, meta_field.default)
            else:
                setattr(lot, f, '')
    lot.save()
    for f in tx_fields_to_remove:
        if f in tx_meta_fields:
            meta_field = tx_meta_fields[f]
            if meta_field.default != NOT_PROVIDED:
                setattr(tx, f, meta_field.default)
            else:
                setattr(tx, f, '')
    tx.save()
    return JsonResponse({'status': 'success', 'message': 'OK, lot %d created' % (lot.id)})


def tx_is_valid(tx):
    # make sure all mandatory fields are set
    if not tx.dae:
        return False, 'DAE manquant'
    if not tx.delivery_site_is_in_carbure and not tx.unknown_delivery_site:
        return False, 'Site de livraison manquant'
    if tx.delivery_site_is_in_carbure and not tx.carbure_delivery_site:
        return False, 'Site de livraison manquant'
    if not tx.delivery_date:
        return False, 'Date de livraison manquante'
    if tx.client_is_in_carbure and not tx.carbure_client:
        return False, 'Veuillez renseigner un client'
    if not tx.client_is_in_carbure and not tx.unknown_client:
        return False, 'Veuillez renseigner un client'
    return True, ''


def lot_is_valid(lot):
    if not lot.volume:
        return False, 'Veuillez renseigner le volume'

    if not lot.parent_lot:
        if not lot.pays_origine:
            return False, 'Veuillez renseigner le pays d\'origine de la matière première'
        if lot.producer_is_in_carbure and lot.carbure_production_site is None:
            return False, 'Veuillez préciser le site de production'
    else:
        # no need to check lot info
        pass
    return True, ''


def generate_carbure_id(lot):
    today = datetime.date.today()
    # [PAYS][YYMM]P[IDProd]-[1....]-([S123])
    # FR2002P001-1
    country = 'XX'
    if lot.carbure_production_site and lot.carbure_production_site.country:
        country = lot.carbure_production_site.country.code_pays
    yymm = today.strftime('%y%m')
    idprod = 'XXX'
    if lot.carbure_producer:
        idprod = '%d' % (lot.carbure_producer.id)
    return "%s%sP%s-%d" % (country, yymm, idprod, lot.id)


def try_fuse_lots(context, tx):
    lot = tx.lot
    # if we are the client, check if we can fuse lots in the mass balance
    if tx.carbure_client == context['user_entity'] and tx.delivery_site_is_in_carbure:
        similar_lots_stored_there = LotTransaction.objects.filter(carbure_delivery_site=tx.carbure_delivery_site,
                                                                  lot__biocarburant=tx.lot.biocarburant,
                                                                  lot__matiere_premiere=tx.lot.matiere_premiere,
                                                                  lot__ghg_total=tx.lot.ghg_total,
                                                                  lot__status='Validated',
                                                                  delivery_status='A')
        if len(similar_lots_stored_there) > 1:
            new_lot = LotV2()
            new_lot.period = tx.lot.period
            new_lot.biocarburant = tx.lot.biocarburant
            new_lot.matiere_premiere = tx.lot.matiere_premiere
            new_lot.ghg_total = tx.lot.ghg_total
            new_lot.ghg_reference = tx.lot.ghg_reference
            new_lot.ghg_reduction = tx.lot.ghg_reduction
            new_lot.status = "Validated"
            new_lot.is_fused = True
            # save here to get the object id, needed for carbure_id
            new_lot.save()
            new_lot.carbure_id = generate_carbure_id(new_lot) + 'F'
            for tx in similar_lots_stored_there:
                tx.lot.is_fused = True
                tx.lot.fused_with = new_lot
                tx.lot.save()
                new_lot.volume += tx.lot.volume
            new_lot.save()
            new_tx = LotTransaction()
            new_tx.lot = new_lot
            new_tx.client_is_in_carbure = True
            new_tx.carbure_client = tx.carbure_client
            new_tx.carbure_delivery_site = tx.carbure_delivery_site
            new_tx.delivery_status = 'A'
            new_tx.ghg_total = new_lot.ghg_total
            new_tx.ghg_reduction = new_lot.ghg_reduction
            new_tx.champ_libre = 'FUSIONNÉ'
            new_tx.save()


@login_required
@enrich_with_user_details
@restrict_to_producers
def validate_lots(request, *args, **kwargs):
    context = kwargs['context']
    lot_ids = request.POST.get('lots', None)
    results = []
    if not lot_ids:
        return JsonResponse({'status': 'error', 'message': 'Aucun lot sélectionné'}, status=400)

    ids = lot_ids.split(',')
    for lotid in ids:
        try:
            lot = LotV2.objects.get(id=lotid, added_by=context['user_entity'], status='Draft')
            # we use .get() below because we should have a single transaction for this lot
            tx = LotTransaction.objects.get(lot=lot)
        except Exception as e:
            results.append({'lot_id': lotid, 'status': 'error', 'message': 'Impossible de valider le lot: introuvable ou déjà validé' % (), 'extra': str(e)})
            continue
        # make sure all mandatory fields are set
        tx_valid, error = tx_is_valid(tx)
        if not tx_valid:
            results.append({'lot_id': lotid, 'status': 'error', 'message': error})
            continue
        lot_valid, error = lot_is_valid(lot)
        if not lot_valid:
            results.append({'lot_id': lotid, 'status': 'error', 'message': error})
            continue
        lot.carbure_id = generate_carbure_id(lot)
        lot.status = "Validated"
        if tx.carbure_client == context['user_entity']:
            tx.delivery_status = 'A'
            tx.save()
        lot.save()
        try_fuse_lots(context, tx)
        results.append({'lot_id': lotid, 'status': 'success'})
    return JsonResponse({'status': 'success', 'message': results})


@login_required
@enrich_with_user_details
@restrict_to_producers
def validate_mb_drafts_lots(request, *args, **kwargs):
    context = kwargs['context']
    txids = request.POST.get('txids', None)
    results = []
    if not txids:
        return JsonResponse({'status': 'error', 'message': 'Aucun lot sélectionné'}, status=400)

    ids = txids.split(',')
    for txid in ids:
        tx = LotTransaction.objects.get(id=txid)
        lot = tx.lot
        if tx.lot.added_by != context['user_entity']:
            results.append({'txid': txid, 'status': 'error', 'message': 'Ce lot ne vous appartient pas'})
            continue
        if tx.lot.status != 'Draft':
            results.append({'txid': txid, 'status': 'error', 'message': 'Ce lot a déjà été validé'})
            continue
        # make sure all mandatory fields are set
        tx_valid, error = tx_is_valid(tx)
        if not tx_valid:
            results.append({'txid': txid, 'status': 'error', 'message': error})
            continue
        lot_valid, error = lot_is_valid(lot)
        if not lot_valid:
            results.append({'txid': txid, 'status': 'error', 'message': error})
            continue

        # check if we can extract the lot from the parent
        if not lot.parent_lot:
            results.append({'txid': txid, 'status': 'error', 'message': 'Missing source_lot'})
            continue

        if lot.biocarburant != lot.parent_lot.biocarburant:
            results.append({'txid': txid, 'status': 'error', 'message': 'Biocarburants différents: ligne de mass balance %s, lot %s' % (lot.parent_lot.biocarburant.name, lot.biocarburant.name)})
            continue

        if lot.matiere_premiere != lot.parent_lot.matiere_premiere:
            results.append({'txid': txid, 'status': 'error', 'message': 'Matières premières différentes: ligne de mass balance %s, lot %s' % (lot.parent_lot.matiere_premiere.name, lot.matiere_premiere.name)})
            continue

        if lot.ghg_total != lot.parent_lot.ghg_total:
            results.append({'txid': txid, 'status': 'error', 'message': 'Informations de durabilité différentes: ligne de mass balance %s, lot %s' % (lot.parent_lot.ghg_total, lot.ghg_total)})
            continue

        if lot.volume > lot.parent_lot.volume:
            results.append({'txid': txid, 'status': 'error', 'message': 'Quantité disponible dans la mass balance insuffisante: Dispo %d litres, lot %d litres' % (lot.parent_lot.volume, lot.volume)})
            continue

        lot.carbure_id = generate_carbure_id(lot) + 'S'
        lot.status = "Validated"
        if tx.carbure_client == context['user_entity']:
            tx.delivery_status = 'A'
            tx.save()
        lot.save()
        lot.parent_lot.volume -= lot.volume
        lot.parent_lot.save()
        results.append({'txid': txid, 'status': 'success'})
    print(results)
    return JsonResponse({'status': 'success', 'message': results})


@login_required
@enrich_with_user_details
@restrict_to_producers
def reject_lot(request, *args, **kwargs):
    context = kwargs['context']
    # new lot or edit?
    tx_id = request.POST.get('tx_id', None)
    tx_comment = request.POST.get('comment', '')
    if tx_id is None:
        return JsonResponse({'status': 'error', 'message': "Missing TX ID from POST data"}, status=400)
    if tx_comment == '':
        return JsonResponse({'status': 'error', 'message': "Un commentaire est obligatoire en cas de refus"}, status=400)
    try:
        tx = LotTransaction.objects.get(carbure_client=context['user_entity'], delivery_status__in=['N', 'AC', 'AA'], id=tx_id)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': "Transaction inconnue", 'extra': str(e)}, status=400)
    tx.delivery_status = 'R'
    tx.save()
    txerr = TransactionComment()
    txerr.entity = context['user_entity']
    txerr.tx = tx
    txerr.comment = tx_comment
    txerr.save()
    return JsonResponse({'status': 'success', 'tx_id': tx.id})


@login_required
@enrich_with_user_details
@restrict_to_producers
def accept_lot(request, *args, **kwargs):
    context = kwargs['context']
    # new lot or edit?
    tx_id = request.POST.get('tx_id', None)
    if tx_id is None:
        return JsonResponse({'status': 'error', 'message': "Missing TX ID from POST data"}, status=400)
    try:
        tx = LotTransaction.objects.get(carbure_client=context['user_entity'], delivery_status__in=['N', 'AC', 'AA'], id=tx_id)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': "Transaction inconnue", 'extra': str(e)}, status=400)
    tx.delivery_status = 'A'
    tx.save()
    try_fuse_lots(context, tx)
    return JsonResponse({'status': 'success', 'tx_id': tx.id})


@login_required
@enrich_with_user_details
@restrict_to_producers
def accept_lots(request, *args, **kwargs):
    context = kwargs['context']
    # new lot or edit?
    tx_ids = request.POST.get('tx_ids', None)
    if tx_ids is None:
        return JsonResponse({'status': 'error', 'message': "Missing TX IDs from POST data"}, status=400)

    ids = tx_ids.split(',')
    for txid in ids:
        try:
            tx = LotTransaction.objects.get(carbure_client=context['user_entity'], delivery_status__in=['N', 'AC', 'AA'], id=txid)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': "Transaction inconnue", 'extra': str(e)}, status=400)
        tx.delivery_status = 'A'
        tx.save()
        try_fuse_lots(context, tx)
    return JsonResponse({'status': 'success'})


@login_required
@enrich_with_user_details
@restrict_to_producers
def accept_lot_with_correction(request, *args, **kwargs):
    context = kwargs['context']
    # new lot or edit?
    tx_id = request.POST.get('tx_id', None)
    tx_comment = request.POST.get('comment', '')
    if tx_id is None:
        return JsonResponse({'status': 'error', 'message': "Missing TX ID from POST data"}, status=400)
    if tx_comment == '':
        return JsonResponse({'status': 'error', 'message': "Un commentaire est obligatoire"}, status=400)
    try:
        tx = LotTransaction.objects.get(carbure_client=context['user_entity'], delivery_status__in=['N', 'AC', 'AA'], id=tx_id)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': "Transaction inconnue", 'extra': str(e)}, status=400)
    tx.delivery_status = 'AC'
    tx.save()
    txc = TransactionComment()
    txc.entity = context['user_entity']
    txc.tx = tx
    txc.comment = tx_comment
    txc.save()
    return JsonResponse({'status': 'success', 'tx_id': tx.id})


@login_required
@enrich_with_user_details
@restrict_to_producers
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
        tx = LotTransaction.objects.get(carbure_vendor=context['user_entity'], delivery_status__in=['N', 'AC', 'AA', 'R'], id=tx_id)
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


@login_required
@enrich_with_user_details
@restrict_to_producers
def save_lot(request, *args, **kwargs):
    context = kwargs['context']
    # new lot or edit?
    lot_id = request.POST.get('lot_id', None)
    existing_lot = True
    if lot_id:
        try:
            lot = LotV2.objects.get(id=lot_id)
            if lot.added_by != context['user_entity']:
                return JsonResponse({'status': 'error', 'message': "Permission denied"}, status=403)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': "Lot inconnu", 'extra': str(e)}, status=400)
    else:
        # create empty lot
        lot = LotV2()
        lot.source = 'MANUAL'
        existing_lot = False
        lot.save()

    entity = context['user_entity']
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
            LotV2Error.objects.filter(tx=lot, field='unknown_production_site_com_date').delete()
        except Exception:
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
    try:
        ps = ProductionSite.objects.get(id=carbure_production_site_id, producer=lot.carbure_producer)
        lot.carbure_production_site = ps
    except Exception:
        lot.carbure_production_site = None
        if lot.carbure_producer is None:
            error, c = LotV2Error.objects.update_or_create(lot=lot, field='carbure_production_site_name',
                                                           error='Le site de production ne peut être renseigné sans le producteur',
                                                           defaults={'value': carbure_production_site_name})
        else:
            error, c = LotV2Error.objects.update_or_create(lot=lot, field='carbure_production_site_name',
                                                           error='Usine %s inconnue pour %s' % (carbure_production_site_name, lot.carbure_producer.name),
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

    if existing_lot is False:
        transaction = LotTransaction()
        transaction.lot = lot
        transaction.save()
    else:
        transaction = LotTransaction.objects.get(lot=lot)

    transaction.unknown_client = request.POST.get('unknown_client', '')
    transaction.unknown_delivery_site = request.POST.get('unknown_delivery_site', '')
    unknown_delivery_site_country_code = request.POST.get('unknown_delivery_site_country_code', '')
    try:
        country = Pays.objects.get(code_pays=unknown_delivery_site_country_code)
        transaction.unknown_delivery_site_country = country
    except Exception:
        transaction.unknown_delivery_site_country = None

    transaction.vendor_is_in_carbure = True
    transaction.carbure_vendor = entity
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
    transaction.save()
    lot.save()
    return JsonResponse({'status': 'success', 'lot_id': lot.id, 'transaction_id': transaction.id})
