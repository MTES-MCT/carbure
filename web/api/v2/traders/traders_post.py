import datetime

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.db.models.fields import NOT_PROVIDED

from core.decorators import enrich_with_user_details, restrict_to_traders
from core.models import Entity, ProductionSite, Pays, Biocarburant, MatierePremiere, Depot
from core.models import LotV2, LotTransaction, TransactionError, LotV2Error, UserRights, TransactionComment

from api.v2 import common


@login_required
@enrich_with_user_details
@restrict_to_traders
def delete_lots(request, *args, **kwargs):
    context = kwargs['context']
    tx_ids = request.POST.get('lots', None)
    errors = []
    if not tx_ids:
        return JsonResponse({'status': 'error', 'message': 'Missing tx ids'}, status=400)
    ids = tx_ids.split(',')
    for txid in ids:
        tx = LotTransaction.objects.get(id=txid, lot__added_by=context['user_entity'], lot__status='Draft')
        try:
            tx.lot.delete()
            tx.delete()
        except Exception as e:
            errors.append({'message': 'Impossible de supprimer le lot: introuvable ou déjà validé', 'extra': str(e)})
    return JsonResponse({'status': 'success', 'message': '%d lots supprimés' % (len(ids) - len(errors)), 'errors': errors})


@login_required
@enrich_with_user_details
@restrict_to_traders
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
@restrict_to_traders
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
    tx_fields_to_remove = ['dae', 'delivery_status']
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


@login_required
@enrich_with_user_details
@restrict_to_traders
def validate_lots(request, *args, **kwargs):
    context = kwargs['context']
    tx_ids = request.POST.get('lots', None)
    results = []
    if not tx_ids:
        return JsonResponse({'status': 'error', 'message': 'Aucun lot sélectionné'}, status=400)

    ids = tx_ids.split(',')
    for txid in ids:
        try:
            tx = LotTransaction.objects.get(id=txid, lot__added_by=context['user_entity'], lot__status='Draft')
        except Exception as e:
            results.append({'tx_id': txid, 'status': 'error', 'message': 'Impossible de valider le lot: introuvable ou déjà validé', 'extra': str(e)})
            continue
        # make sure all mandatory fields are set
        tx_valid, error = common.tx_is_valid(tx)
        if not tx_valid:
            results.append({'tx_id': txid, 'status': 'error', 'message': error})
            continue
        lot_valid, error = common.lot_is_valid(tx.lot)
        if not lot_valid:
            results.append({'tx_id': txid, 'status': 'error', 'message': error})
            continue
        tx.lot.carbure_id = common.generate_carbure_id(tx.lot)
        tx.lot.status = "Validated"
        if tx.carbure_client == context['user_entity']:
            tx.delivery_status = 'A'
            tx.save()
        tx.lot.save()
        results.append({'tx_id': txid, 'status': 'success'})
    print(results)
    return JsonResponse({'status': 'success', 'message': results})


@login_required
@enrich_with_user_details
@restrict_to_traders
def fuse_mb_lots(request, *args, **kwargs):
    context = kwargs['context']
    txids = request.POST.get('txids', None)
    if not txids:
        return JsonResponse({'status': 'error', 'message': 'Aucune ligne sélectionnée'}, status=400)

    ids = txids.split(',')
    # on fusionne tout ce qu'il est possible de fusionner
    # 1 on recupere tous les lots
    txs = LotTransaction.objects.filter(id__in=ids, carbure_client=context['user_entity'], lot__status='Validated')

    groups = {}
    for t in txs:
        key = '%s-%s-%s-%s' % (t.lot.biocarburant.id, t.lot.matiere_premiere.id, str(t.lot.ghg_total), t.lot.pays_origine.id)
        if t.lot.producer_is_in_carbure:
            key += '%s' % (t.lot.carbure_producer.id)
        else:
            key += '%s' % (t.lot.unknown_production_site_reference)

        if t.delivery_site_is_in_carbure:
            key += '%s' % (t.carbure_delivery_site.id)
        else:
            key += '%s' % (t.unknown_delivery_site)

        if key not in groups:
            groups[key] = []
        groups[key].append(t)
    print(groups)
    fused = 0
    for k, v in groups.items():
        if len(v) > 1:
            # we can fuse something!
            common.fuse_lots(v)
            fused += len(v)
    if fused == 0:
        return JsonResponse({'status': 'error', 'message': "Aucune possibilité de fusion"}, status=400)
    else:
        return JsonResponse({'status': 'success', 'message': "%d lignes fusionnées" % (fused)}, status=400)


@login_required
@enrich_with_user_details
@restrict_to_traders
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
        tx_valid, error = common.tx_is_valid(tx)
        if not tx_valid:
            results.append({'txid': txid, 'status': 'error', 'message': error})
            continue
        lot_valid, error = common.lot_is_valid(lot)
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

        lot.carbure_id = common.generate_carbure_id(lot) + 'S'
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
@restrict_to_traders
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
@restrict_to_traders
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
    return JsonResponse({'status': 'success', 'tx_id': tx.id})


@login_required
@enrich_with_user_details
@restrict_to_traders
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
    return JsonResponse({'status': 'success'})


@login_required
@enrich_with_user_details
@restrict_to_traders
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
