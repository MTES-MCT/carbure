import random
import openpyxl
import datetime

from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Max, Min
from django.core import serializers
from django.db.models.fields import NOT_PROVIDED

from core.decorators import enrich_with_user_details, restrict_to_producers
from core.xlsx_template import create_template_xlsx_v2_simple, create_template_xlsx_v2_advanced

from core.models import Entity, ProductionSite, Pays, Biocarburant, MatierePremiere, Depot
from core.models import LotV2, LotTransaction, TransactionError, LotV2Error


def get_random(model):
    max_id = model.objects.all().aggregate(max_id=Max("id"))['max_id']
    while True:
        pk = random.randint(1, max_id)
        element = model.objects.filter(pk=pk).first()
        if element:
            return element


# not an API call. helper function
def load_excel_lot(context, lot_row):
    entity = context['user_entity']
    lot = LotV2()
    lot.added_by = entity
    if 'producer' in lot_row and lot_row['producer'] is not None:
        # this should be a bought or imported lot
        # check if we know the producer
        # producer_is_in_carbure = models.BooleanField(default=True)
        # carbure_producer = models.ForeignKey(Entity, null=True, blank=True, on_delete=models.SET_NULL, related_name='producer_lotv2')
        # unknown_producer = models.CharField(max_length=64, blank=True, default='')
        if lot_row['producer'] == entity.name:
            # redundant information. by default we assume the producer is the entity logged in
            lot.producer_is_in_carbure = True
            lot.carbure_producer = entity
            lot.unknown_producer = ''
        else:
            # do we know this producer ?
            matches = Entity.objects.filter(name=lot_row['producer']).count()
            if matches == 1:
                # yes we do
                # in this case, the producer should declare its production directly in Carbure
                # we cannot allow someone else to declare for them
                raise Exception("Vous ne pouvez pas déclarer des lots d'un producteur déjà inscrit sur Carbure")
            else:
                # ok, unknown producer. allow importation
                lot.producer_is_in_carbure = False
                lot.carbure_producer = None
                lot.unknown_producer = lot_row['producer']
    else:
        # print('No producer in excel sheet. ')
        # default, current entity is the producer
        lot.producer_is_in_carbure = False
        lot.carbure_producer = None
        lot.unknown_producer = ''
    lot.save()

    if 'production_site' in lot_row:
        production_site = lot_row['production_site']
        # production_site_is_in_carbure = models.BooleanField(default=True)
        # carbure_production_site = models.ForeignKey(ProductionSite, null=True, blank=True, on_delete=models.SET_NULL)
        # unknown_production_site = models.CharField(max_length=64, blank=True, default='')
        if lot.producer_is_in_carbure:
            try:
                lot.carbure_production_site = ProductionSite.objects.get(producer=lot.carbure_producer, name=production_site)
                lot.production_site_is_in_carbure = True
                lot.unknown_production_site = ''
                LotV2Error.objects.filter(lot=lot, field='production_site').delete()
            except Exception:
                # do not allow the use of an unknown production site if the producer is registered in Carbure
                lot.carbure_production_site = None
                lot.production_site_is_in_carbure = False
                lot.unknown_production_site = ''
                error, c = LotV2Error.objects.update_or_create(lot=lot, field='production_site',
                                                               error='Site de production %s inconnu pour %s' % (production_site, lot.carbure_producer.name),
                                                               defaults={'value': production_site})
        else:
            # producer not in carbure
            # accept any value
            lot.production_site_is_in_carbure = False
            lot.carbure_production_site = None
            if production_site is not None:
                lot.unknown_production_site = production_site
            else:
                lot.unknown_production_site = ''
    else:
        lot.production_site_is_in_carbure = False
        lot.carbure_production_site = None
        lot.unknown_production_site = ''
        error, c = LotV2Error.objects.update_or_create(lot=lot, field='production_site',
                                                       error='Champ production_site introuvable dans le fichier excel',
                                                       defaults={'value': None})
    if lot.producer_is_in_carbure is False:
        if 'production_site_country' in lot_row:
            production_site_country = lot_row['production_site_country']
            if production_site_country is None:
                lot.unknown_production_country = None
            else:
                try:
                    country = Pays.objects.get(code_pays=production_site_country)
                except Exception:
                    error, c = LotV2Error.objects.update_or_create(lot=lot, field='unknown_production_country',
                                                                   error='Champ production_site_country incorrect',
                                                                   defaults={'value': production_site_country})
        else:
            lot.unknown_production_country = None

    if 'biocarburant_code' in lot_row:
        biocarburant = lot_row['biocarburant_code']
        try:
            lot.biocarburant = Biocarburant.objects.get(code=biocarburant)
            LotV2Error.objects.filter(lot=lot, field='biocarburant_code').delete()
        except Exception as e:
            lot.biocarburant = None
            error, c = LotV2Error.objects.update_or_create(lot=lot, field='biocarburant_code',
                                                           error='Biocarburant inconnu',
                                                           defaults={'value': biocarburant})
    else:
        biocarburant = None
        lot.biocarburant = None
        error, c = LotV2Error.objects.update_or_create(lot=lot, field='biocarburant_code',
                                                       error='Merci de préciser le Biocarburant',
                                                       defaults={'value': biocarburant})
    if 'matiere_premiere_code' in lot_row:
        matiere_premiere = lot_row['matiere_premiere_code']
        try:
            lot.matiere_premiere = MatierePremiere.objects.get(code=matiere_premiere)
            LotV2Error.objects.filter(lot=lot, field='matiere_premiere_code').delete()
        except Exception:
            lot.matiere_premiere = None
            error, c = LotV2Error.objects.update_or_create(lot=lot, field='matiere_premiere_code',
                                                           error='Matière Première inconnue',
                                                           defaults={'value': matiere_premiere})
    else:
        matiere_premiere = None
        lot.matiere_premiere = None
        error, c = LotV2Error.objects.update_or_create(lot=lot, field='matiere_premiere_code',
                                                       error='Merci de préciser la matière première',
                                                       defaults={'value': matiere_premiere})

    if 'volume' in lot_row:
        volume = lot_row['volume']
        try:
            lot.volume = float(volume)
            LotV2Error.objects.filter(lot=lot, field='volume').delete()
        except Exception:
            lot.volume = 0
            e, c = LotV2Error.objects.update_or_create(lot=lot, field='volume',
                                                       error='Format du volume incorrect', defaults={'value': volume})
    else:
        e, c = LotV2Error.objects.update_or_create(lot=lot, field='volume',
                                                   error='Merci de préciser un volume', defaults={'value': volume})

    if 'pays_origine_code' in lot_row:
        pays_origine = lot_row['pays_origine_code']
        try:
            lot.pays_origine = Pays.objects.get(code_pays=pays_origine)
            LotV2Error.objects.filter(lot=lot, field='pays_origine_code').delete()
        except Exception:
            lot.pays_origine = None
            error, c = LotV2Error.objects.update_or_create(lot=lot, field='pays_origine_code',
                                                           error='Pays inconnu',
                                                           defaults={'value': pays_origine})
    else:
        pays_origine = None
        lot.pays_origine = None
        error, c = LotV2Error.objects.update_or_create(lot=lot, field='pays_origine_code',
                                                       error='Merci de préciser le pays',
                                                       defaults={'value': pays_origine})
    lot.eec = 0
    if 'eec' in lot_row:
        eec = lot_row['eec']
        try:
            lot.eec = float(eec)
        except:
            error, c = LotV2Error.objects.update_or_create(lot=lot, field='eec',
                                                           error='Format non reconnu',
                                                           defaults={'value': eec})
    lot.el = 0
    if 'el' in lot_row:
        el = lot_row['el']
        try:
            lot.el = float(el)
        except:
            error, c = LotV2Error.objects.update_or_create(lot=lot, field='el',
                                                           error='Format non reconnu',
                                                           defaults={'value': el})
    lot.ep = 0
    if 'ep' in lot_row:
        ep = lot_row['ep']
        try:
            lot.ep = float(ep)
        except:
            error, c = LotV2Error.objects.update_or_create(lot=lot, field='ep',
                                                           error='Format non reconnu',
                                                           defaults={'value': ep})
    lot.etd = 0
    if 'etd' in lot_row:
        etd = lot_row['etd']
        try:
            lot.etd = float(etd)
        except:
            error, c = LotV2Error.objects.update_or_create(lot=lot, field='etd',
                                                           error='Format non reconnu',
                                                           defaults={'value': etd})
    lot.eu = 0
    if 'eu' in lot_row:
        eu = lot_row['eu']
        try:
            lot.eu = float(eu)
        except:
            error, c = LotV2Error.objects.update_or_create(lot=lot, field='eu',
                                                           error='Format non reconnu',
                                                           defaults={'value': eu})
    lot.esca = 0
    if 'esca' in lot_row:
        esca = lot_row['esca']
        try:
            lot.esca = float(esca)
        except:
            error, c = LotV2Error.objects.update_or_create(lot=lot, field='esca',
                                                           error='Format non reconnu',
                                                           defaults={'value': esca})
    lot.eccs = 0
    if 'eccs' in lot_row:
        eccs = lot_row['eccs']
        try:
            lot.eccs = float(eccs)
        except:
            error, c = LotV2Error.objects.update_or_create(lot=lot, field='eccs',
                                                           error='Format non reconnu',
                                                           defaults={'value': eccs})
    lot.eccr = 0
    if 'eccr' in lot_row:
        eccr = lot_row['eccr']
        try:
            lot.eccr = float(eccr)
        except:
            error, c = LotV2Error.objects.update_or_create(lot=lot, field='eccr',
                                                           error='Format non reconnu',
                                                           defaults={'value': eccr})
    lot.eee = 0
    if 'eee' in lot_row:
        eee = lot_row['eee']
        try:
            lot.eee = float(eee)
        except:
            error, c = LotV2Error.objects.update_or_create(lot=lot, field='eee',
                                                           error='Format non reconnu',
                                                           defaults={'value': eee})
    # calculs ghg
    lot.ghg_total = round(lot.eec + lot.el + lot.ep + lot.etd + lot.eu - lot.esca - lot.eccs - lot.eccr - lot.eee, 2)
    lot.ghg_reference = 83.8
    lot.ghg_reduction = round((1.0 - (lot.ghg_total / lot.ghg_reference)) * 100.0, 2)

    lot.source = 'EXCEL'
    lot.save()

    transaction = LotTransaction()
    transaction.lot = lot
    transaction.save()
    transaction.vendor_is_in_carbure = True
    transaction.carbure_vendor = entity

    if 'dae' in lot_row:
        dae = lot_row['dae']
        if dae is not None:
            transaction.dae = dae
            TransactionError.objects.filter(tx=transaction, field='dae').delete()
        else:
            e, c = TransactionError.objects.update_or_create(tx=transaction, field='dae', error="Merci de préciser le numéro de DAE/DAU",
                                                             defaults={'value': dae})
    else:
        e, c = TransactionError.objects.update_or_create(tx=transaction, field='dae', error="Merci de préciser le numéro de DAE/DAU",
                                                         defaults={'value': None})

    if 'delivery_date' not in lot_row or lot_row['delivery_date'] == '':
        transaction.ea_delivery_date = None
        lot.period = ''
        e, c = TransactionError.objects.update_or_create(tx=transaction, field='ea_delivery_date',
                                                         error="Merci de préciser la date de livraison",
                                                         defaults={'value': None})
    else:
        try:
            delivery_date = lot_row['delivery_date']
            year = int(delivery_date[0:4])
            month = int(delivery_date[5:7])
            day = int(delivery_date[8:10])
            dd = datetime.date(year=year, month=month, day=day)
            transaction.delivery_date = dd
            lot.period = dd.strftime('%Y-%m')
            TransactionError.objects.filter(tx=transaction, field='delivery_date').delete()
        except Exception:
            msg = "Format de date incorrect: veuillez entrer une date au format AAAA-MM-JJ"
            e, c = TransactionError.objects.update_or_create(tx=transaction, field='delivery_date',
                                                             error=msg,
                                                             defaults={'value': delivery_date})
    if 'client' in lot_row and lot_row['client'] is not None:
        client = lot_row['client']
        matches = Entity.objects.filter(name=client).count()
        if matches:
            transaction.client_is_in_carbure = True
            transaction.carbure_client = Entity.objects.get(name=client)
            transaction.unknown_client = ''
        else:
            transaction.client_is_in_carbure = False
            transaction.carbure_client = None
            transaction.unknown_client = client
        TransactionError.objects.filter(tx=transaction, field='client').delete()
    else:
        transaction.client_is_in_carbure = False
        transaction.carbure_client = None
        transaction.unknown_client = ''
        e, c = TransactionError.objects.update_or_create(tx=transaction, field='client',
                                                         defaults={'value': None, 'error': "Merci de préciser un client"})

    if 'delivery_site' in lot_row and lot_row['delivery_site'] is not None:
        delivery_site = lot_row['delivery_site']
        matches = Depot.objects.filter(depot_id=delivery_site).count()
        if matches:
            transaction.delivery_site_is_in_carbure = True
            transaction.carbure_delivery_site = Depot.objects.get(depot_id=delivery_site)
            transaction.unknown_client = ''
        else:
            transaction.delivery_site_is_in_carbure = False
            transaction.carbure_delivery_site = None
            transaction.unknown_delivery_site = delivery_site
        TransactionError.objects.filter(tx=transaction, field='delivery_site').delete()
    else:
        transaction.delivery_site_is_in_carbure = False
        transaction.carbure_delivery_site = None
        transaction.unknown_delivery_site = ''
        e, c = TransactionError.objects.update_or_create(tx=transaction, field='delivery_site',
                                                         defaults={'value': None, 'error': "Merci de préciser un site de livraison"})

    if transaction.delivery_site_is_in_carbure is False:
        if 'delivery_site_country' in lot_row:
            try:
                country = Pays.objects.get(code_pays=lot_row['delivery_site_country'])
                transaction.unknown_delivery_site_country = country
            except Exception:
                error, c = TransactionError.objects.update_or_create(tx=transaction, field='delivery_site_country',
                                                                     error='Champ production_site_country incorrect',
                                                                     defaults={'value': lot_row['delivery_site_country']})
        else:
            error, c = TransactionError.objects.update_or_create(tx=transaction, field='delivery_site_country',
                                                                 error='Merci de préciser une valeur dans le champ production_site_country',
                                                                 defaults={'value': None})

    transaction.ghg_total = lot.ghg_total
    transaction.ghg_reduction = lot.ghg_reduction

    if 'champ_libre' in lot_row:
        transaction.champ_libre = lot_row['champ_libre']
    transaction.save()
    lot.save()


@login_required
@enrich_with_user_details
@restrict_to_producers
def excel_template_download_simple(request, *args, **kwargs):
    context = kwargs['context']
    file_location = create_template_xlsx_v2_simple(context['user_entity'])
    try:
        with open(file_location, 'rb') as f:
            file_data = f.read()
            # sending response
            response = HttpResponse(file_data, content_type='application/vnd.ms-excel')
            response['Content-Disposition'] = 'attachment; filename="carbure_template_simple.xlsx"'
            return response
    except Exception as e:
        return JsonResponse({'status': "error", 'message': "Error creating template file", 'error': str(e)}, status=500)


@login_required
@enrich_with_user_details
@restrict_to_producers
def excel_template_download_advanced(request, *args, **kwargs):
    context = kwargs['context']
    file_location = create_template_xlsx_v2_advanced(context['user_entity'])
    try:
        with open(file_location, 'rb') as f:
            file_data = f.read()
            # sending response
            response = HttpResponse(file_data, content_type='application/vnd.ms-excel')
            response['Content-Disposition'] = 'attachment; filename="carbure_template_advanced.xlsx"'
            return response
    except Exception as e:
        return JsonResponse({'status': "error", 'message': "Error creating template file", 'error': str(e)}, status=500)


@login_required
@enrich_with_user_details
@restrict_to_producers
def excel_template_upload(request, *args, **kwargs):
    context = kwargs['context']
    file = request.FILES.get('file')
    if file is None:
        return JsonResponse({'status': "error", 'message': "Merci d'ajouter un fichier"}, status=400)
    # we can load the file
    wb = openpyxl.load_workbook(file)
    lots_sheet = wb['lots']
    colid2field = {}
    lots = []
    # create a dictionary from the line
    for i, row in enumerate(lots_sheet):
        if i == 0:
            # header
            for i, col in enumerate(row):
                colid2field[i] = col.value
        else:
            lot = {}
            for i, col in enumerate(row):
                field = colid2field[i]
                lot[field] = col.value
            lots.append(lot)
    total_lots = len(lots)
    lots_loaded = 0
    for lot in lots:
        try:
            load_excel_lot(context, lot)
            lots_loaded += 1
        except Exception as e:
            print(e)
    return JsonResponse({'status': "success", 'message': "%d/%d lots chargés correctement" % (lots_loaded, total_lots)})


@login_required
@enrich_with_user_details
@restrict_to_producers
def get_drafts(request, *args, **kwargs):
    context = kwargs['context']
    lots = LotV2.objects.filter(added_by=context['user_entity'], status='Draft')
    transactions_ids = set([tx['id__min'] for tx in LotTransaction.objects.filter(lot__in=lots).values('lot_id', 'id').annotate(Min('id'))])
    errors = LotV2Error.objects.filter(lot__in=lots)
    first_transactions = LotTransaction.objects.filter(id__in=transactions_ids)
    sez = serializers.serialize('json', lots, use_natural_foreign_keys=True)
    txsez = serializers.serialize('json', first_transactions, use_natural_foreign_keys=True)
    errsez = serializers.serialize('json', errors, use_natural_foreign_keys=True)
    return JsonResponse({'lots': sez, 'errors': errsez, 'transactions': txsez})


@login_required
@enrich_with_user_details
@restrict_to_producers
def get_received(request, *args, **kwargs):
    context = kwargs['context']
    transactions = LotTransaction.objects.filter(carbure_client=context['user_entity'], delivery_status='N', lot__status="Validated")
    lot_ids = [t.lot.id for t in transactions]
    lots = LotV2.objects.filter(id__in=lot_ids)
    errors = LotV2Error.objects.filter(lot__in=lots)
    sez = serializers.serialize('json', lots, use_natural_foreign_keys=True)
    txsez = serializers.serialize('json', transactions, use_natural_foreign_keys=True)
    errsez = serializers.serialize('json', errors, use_natural_foreign_keys=True)
    return JsonResponse({'lots': sez, 'errors': errsez, 'transactions': txsez})


@login_required
@enrich_with_user_details
@restrict_to_producers
def get_corrections(request, *args, **kwargs):
    context = kwargs['context']
    transactions = LotTransaction.objects.filter(carbure_client=context['user_entity'], delivery_status__in=['R', 'AC', 'AA'], lot__status="Validated")
    lot_ids = [t.lot.id for t in transactions]
    lots = LotV2.objects.filter(id__in=lot_ids)
    sez = serializers.serialize('json', lots, use_natural_foreign_keys=True)
    txsez = serializers.serialize('json', transactions, use_natural_foreign_keys=True)
    return JsonResponse({'lots': sez, 'transactions': txsez})


@login_required
@enrich_with_user_details
@restrict_to_producers
def get_valid(request, *args, **kwargs):
    context = kwargs['context']
    transactions = list(LotTransaction.objects.filter(carbure_vendor=context['user_entity'], lot__status='Validated'))
    transactions.extend(list(LotTransaction.objects.filter(carbure_client=context['user_entity'], lot__status="Validated")))
    lot_ids = [t.lot.id for t in transactions]
    lots = LotV2.objects.filter(id__in=lot_ids)
    sez = serializers.serialize('json', lots, use_natural_foreign_keys=True)
    txsez = serializers.serialize('json', transactions, use_natural_foreign_keys=True)
    return JsonResponse({'lots': sez, 'transactions': txsez})


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
        if not tx.dae:
            results.append({'lot_id': lotid, 'status': 'error', 'message': 'Validation impossible. DAE manquant'})
            continue
        if not tx.delivery_site_is_in_carbure and not tx.unknown_delivery_site:
            results.append({'lot_id': lotid, 'status': 'error', 'message': 'Validation impossible. Site de livraison manquant'})
            continue
        if tx.delivery_site_is_in_carbure and not tx.carbure_delivery_site:
            results.append({'lot_id': lotid, 'status': 'error', 'message': 'Validation impossible. Site de livraison manquant'})
            continue
        if not tx.delivery_date:
            results.append({'lot_id': lotid, 'status': 'error', 'message': 'Validation impossible. Date de livraison manquante'})
            continue
        if tx.client_is_in_carbure and not tx.carbure_client:
            results.append({'lot_id': lotid, 'status': 'error', 'message': 'Validation impossible. Veuillez renseigner un client'})
            continue
        if not tx.client_is_in_carbure and not tx.unknown_client:
            results.append({'lot_id': lotid, 'status': 'error', 'message': 'Validation impossible. Veuillez renseigner un client'})
            continue
        if not lot.volume:
            results.append({'lot_id': lotid, 'status': 'error', 'message': 'Validation impossible. Veuillez renseigner le volume'})
            continue
        if not lot.pays_origine:
            msg = 'Validation impossible. Veuillez renseigner le pays d\'origine de la matière première'
            results.append({'lot_id': lotid, 'status': 'error', 'message': msg})
            continue
        try:
            today = datetime.date.today()
            # [PAYS][YYMM]P[IDProd]-[1....]-([S123])
            # FR2002P001-1
            if lot.producer_is_in_carbure:
                lot.carbure_id = "%s%sP%d-%d" % ('FR', today.strftime('%y%m'), lot.carbure_producer.id, lot.id)
            else:
                lot.carbure_id = "%s%sP%s-%d" % ('FR', today.strftime('%y%m'), 'XXX', lot.id)
            lot.status = "Validated"
            lot.save()
        except Exception:
            results.append({'lot_id': lotid, 'status': 'error', 'message': 'Erreur lors de la validation du lot'})
            continue
        results.append({'lot_id': lotid, 'status': 'sucess'})
    # print({'status': 'success', 'message': results})
    return JsonResponse({'status': 'success', 'message': results})


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
    producer_name = request.POST.get('producer_name', '')
    if not producer_name:
        lot.producer_is_in_carbure = False
        lot.unknown_producer = ''
        lot.carbure_producer = None
    elif producer_name != entity.name:
        lot.producer_is_in_carbure = False
        lot.unknown_producer = producer_name
        lot.carbure_producer = None
    else:
        lot.producer_is_in_carbure = True
        lot.unknown_producer = ''
        lot.carbure_producer = entity

    production_site_id = request.POST.get('production_site_id', '')
    production_site_name = request.POST.get('production_site_name', '')
    if production_site_id == '':
        # production site entered manually without autocomplete.
        lot.production_site_is_in_carbure = False
        lot.carbure_production_site = None
        lot.unknown_production_site = production_site_name
    else:
        try:
            ps = ProductionSite.objects.get(id=production_site_id, producer=entity)
            lot.production_site_is_in_carbure = True
            lot.carbure_production_site = ps
            lot.unknown_production_site = ''
        except Exception:
            lot.production_site_is_in_carbure = False
            lot.carbure_production_site = None
            lot.unknown_production_site = ''
            error, c = LotV2Error.objects.update_or_create(lot=lot, field='production_site_name',
                                                           error='Site de production %s inconnu pour %s' % (production_site_name, entity.name),
                                                           defaults={'value': production_site_name})

    if lot.production_site_is_in_carbure is False:
        production_site_country_code = request.POST.get('production_site_country_code', '')
        production_site_country = request.POST.get('production_site_country', '')
        if production_site_country_code == '':
            lot.unknown_production_country = None
        else:
            try:
                country = Pays.objects.get(code_pays=production_site_country_code)
                lot.unknown_production_country = country
            except Exception:
                lot.unknown_production_country = None
                error, c = LotV2Error.objects.update_or_create(lot=lot, field='production_site_country',
                                                               error='Pays de production inconnu',
                                                               defaults={'value': production_site_country})

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
    transaction.vendor_is_in_carbure = True
    transaction.carbure_vendor = entity
    transaction.dae = request.POST.get('dae', '')
    if transaction.dae == '':
        e, c = TransactionError.objects.update_or_create(tx=transaction, field='dae', error="Merci de préciser le numéro de DAE/DAU",
                                                         defaults={'value': None})
    else:
        TransactionError.objects.filter(tx=transaction, field='dae').delete()

    delivery_date = request.POST.get('delivery_date', '')
    if delivery_date == '':
        transaction.ea_delivery_date = None
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
            msg = "Format de date incorrect: veuillez entrer une date au format AAAA-MM-JJ"
            e, c = TransactionError.objects.update_or_create(tx=transaction, field='delivery_date',
                                                             error=msg,
                                                             defaults={'value': delivery_date})

    client_id = request.POST.get('client_id', '')
    client_name = request.POST.get('client', '')
    if client_id != '':
        try:
            client = Entity.objects.get(id=client_id)
            transaction.client_is_in_carbure = True
            transaction.carbure_client = client
            transaction.unknown_client = ''
        except Exception:
            transaction.client_is_in_carbure = False
            transaction.carbure_client = None
            transaction.unknown_client = client_name
    else:
        transaction.client_is_in_carbure = False
        transaction.carbure_client = None
        transaction.unknown_client = client_name
    if transaction.client_is_in_carbure is False and transaction.unknown_client == '':
        e, c = TransactionError.objects.update_or_create(tx=transaction, field='client',
                                                         defaults={'value': None, 'error': "Merci de préciser un client"})

    delivery_site_id = request.POST.get('delivery_site_id')
    delivery_site_name = request.POST.get('delivery_site')
    if delivery_site_id != '':
        try:
            delivery_site = Depot.objects.get(depot_id=delivery_site_id)
            transaction.delivery_site_is_in_carbure = True
            transaction.carbure_delivery_site = delivery_site
            transaction.unknown_delivery_site = ''
        except Exception:
            transaction.delivery_site_is_in_carbure = False
            transaction.carbure_delivery_site = None
            transaction.unknown_delivery_site = delivery_site_name
    else:
        transaction.delivery_site_is_in_carbure = False
        transaction.carbure_delivery_site = None
        transaction.unknown_delivery_site = delivery_site_name
    if delivery_site_name == '':
        e, c = TransactionError.objects.update_or_create(tx=transaction, field='delivery_site',
                                                         defaults={'value': None, 'error': "Merci de préciser un site de livraison"})

    if transaction.delivery_site_is_in_carbure is False:
        delivery_site_country_code = request.POST.get('delivery_site_country_code', '')
        delivery_site_country_name = request.POST.get('delivery_site_country', '')
        if delivery_site_country_code != '':
            try:
                country = Pays.objects.get(code_pays=delivery_site_country_code)
                transaction.unknown_delivery_site_country = country
            except Exception:
                error, c = TransactionError.objects.update_or_create(tx=transaction, field='delivery_site_country',
                                                                     error='Champ production_site_country incorrect',
                                                                     defaults={'value': delivery_site_country_name})
        else:
            error, c = TransactionError.objects.update_or_create(tx=transaction, field='delivery_site_country',
                                                                 error='Merci de préciser le pays de livraison',
                                                                 defaults={'value': None})

    transaction.ghg_total = lot.ghg_total
    transaction.ghg_reduction = lot.ghg_reduction
    transaction.champ_libre = request.POST.get('champ_libre', '')
    transaction.save()
    lot.save()
    return JsonResponse({'status': 'success', 'lot_id': lot.id, 'transaction_id': transaction.id})
