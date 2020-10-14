import datetime
import openpyxl

from django.http import JsonResponse
from core.models import LotV2, LotTransaction, LotV2Error, TransactionError, UserRights
from core.models import MatierePremiere, Biocarburant, Pays, Entity, ProductionSite, Depot
from core.models import LotValidationError

from api.v2.checkrules import sanity_check


def run_sanity_checks(queryset):
    for obj in queryset:
        sanity_check(obj)


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

    if tx.unknown_delivery_site_country is not None and tx.unknown_delivery_site_country.is_in_europe and tx.lot.pays_origine is None:
        return False, "Veuillez renseigner le pays d'origine de la matière première - Marché européen"
    if tx.carbure_delivery_site is not None and tx.carbure_delivery_site.country.is_in_europe and tx.lot.pays_origine is None:
        return False, "Veuillez renseigner le pays d'origine de la matière première - Marché européen"
    return True, ''


def lot_is_valid(lot):
    if not lot.volume:
        return False, 'Veuillez renseigner le volume'

    if not lot.parent_lot:
        if not lot.biocarburant:
            return False, 'Veuillez renseigner le type de biocarburant'
        if not lot.matiere_premiere:
            return False, 'Veuillez renseigner la matière première'
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


def fuse_lots(txs):
    new_lot = LotV2()
    new_lot.save()

    total_volume = 0
    for tx in txs:
        total_volume += tx.lot.volume
        tx.lot.is_fused = True
        tx.lot.fused_with = new_lot
        tx.lot.save()

    # fill lot details
    lot = txs[0].lot
    new_lot.volume = total_volume
    new_lot.period = lot.period
    new_lot.producer_is_in_carbure = lot.producer_is_in_carbure
    new_lot.carbure_producer = lot.carbure_producer
    new_lot.unknown_producer = lot.unknown_producer
    new_lot.production_site_is_in_carbure = lot.production_site_is_in_carbure
    new_lot.carbure_production_site = lot.carbure_production_site
    new_lot.unknown_production_site = lot.unknown_production_site
    new_lot.unknown_production_site_com_date = lot.unknown_production_site_com_date
    new_lot.unknown_production_site_reference = lot.unknown_production_site_reference
    new_lot.unknown_production_site_dbl_counting = lot.unknown_production_site_dbl_counting
    new_lot.matiere_premiere = lot.matiere_premiere
    new_lot.biocarburant = lot.biocarburant
    new_lot.pays_origine = lot.pays_origine
    new_lot.eec = lot.eec
    new_lot.el = lot.el
    new_lot.ep = lot.ep
    new_lot.etd = lot.etd
    new_lot.eu = lot.eu
    new_lot.esca = lot.esca
    new_lot.eccs = lot.eccs
    new_lot.eccr = lot.eccr
    new_lot.eee = lot.eee
    new_lot.ghg_total = lot.ghg_total
    new_lot.ghg_reduction = lot.ghg_reduction
    new_lot.ghg_reference = lot.ghg_reference
    new_lot.status = 'Validated'
    new_lot.source = 'FUSION'
    new_lot.added_by = lot.added_by
    new_lot.added_by_user = lot.added_by_user
    new_lot.is_fused = False
    new_lot.fused_with = None
    new_lot.save()

    # create a new TX
    new_tx = txs[0]
    new_tx.pk = None
    new_tx.dae = ''
    new_tx.lot = new_lot
    new_tx.save()
    new_lot.carbure_id = generate_carbure_id(new_lot) + 'F'
    new_lot.save()
    print('new lot of %d of %s id %s' % (new_lot.volume, new_lot.biocarburant.name, new_lot.carbure_id))


def fill_producer_info(entity, lot_row, lot):
    if 'producer' in lot_row and lot_row['producer'] is not None:
        # check if we know the producer
        if lot_row['producer'].strip() == entity.name:
            # it's me
            lot.producer_is_in_carbure = True
            lot.carbure_producer = entity
            lot.unknown_producer = ''
        else:
            # it's not me. do we know this producer ?
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
    elif 'producer' in lot_row and lot_row['producer'] is None:
        # producer is not in carbure and we don't even have his name. fine.
        lot.producer_is_in_carbure = False
        lot.carbure_producer = None
        lot.unknown_producer = ''
    else:
        # no producer column = simple template
        # current entity is the producer
        lot.producer_is_in_carbure = True
        lot.carbure_producer = entity
        lot.unknown_producer = ''


def fill_production_site_info(entity, lot_row, lot):
    lot_errors = []
    if 'production_site' in lot_row:
        production_site = lot_row['production_site']
        if lot.producer_is_in_carbure:
            try:
                lot.carbure_production_site = ProductionSite.objects.get(producer=lot.carbure_producer, name=production_site)
                lot.production_site_is_in_carbure = True
                lot.unknown_production_site = ''
            except Exception:
                # do not allow the use of an unknown production site if the producer is registered in Carbure
                lot.carbure_production_site = None
                lot.production_site_is_in_carbure = False
                lot.unknown_production_site = ''
                error = LotV2Error(lot=lot, field='production_site',
                                   error='Site de production %s inconnu pour %s' % (production_site, lot.carbure_producer.name),
                                   value=production_site)
                lot_errors.append(error)
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
        error = LotV2Error(lot=lot, field='production_site',
                           error='Champ production_site introuvable dans le fichier excel',
                           value=None)
        lot_errors.append(error)
    if lot.producer_is_in_carbure is False:
        if 'production_site_country' in lot_row:
            production_site_country = lot_row['production_site_country']
            if production_site_country is None:
                lot.unknown_production_country = None
            else:
                try:
                    country = Pays.objects.get(code_pays=production_site_country)
                    lot.unknown_production_country = country
                except Exception:
                    error = LotV2Error(lot=lot, field='unknown_production_country',
                                       error='Champ production_site_country incorrect',
                                       value=production_site_country)
                    lot_errors.append(error)
        else:
            lot.unknown_production_country = None
        if 'production_site_reference' in lot_row:
            lot.unknown_production_site_reference = lot_row['production_site_reference']
        else:
            lot.unknown_production_site_reference = ''
        if 'production_site_commissioning_date' in lot_row:
            lot.unknown_production_site_com_date = lot_row['production_site_commissioning_date']
        else:
            lot.unknown_production_site_com_date = ''
        if 'double_counting_registration' in lot_row:
            lot.unknown_production_site_dbl_counting = lot_row['double_counting_registration']
        else:
            lot.unknown_production_site_dbl_counting = ''
    return lot_errors


def fill_biocarburant_info(lot_row, lot):
    lot_errors = []
    if 'biocarburant_code' in lot_row:
        biocarburant = lot_row['biocarburant_code']
        try:
            lot.biocarburant = Biocarburant.objects.get(code=biocarburant)
        except Exception:
            lot.biocarburant = None
            lot_errors.append(LotV2Error(lot=lot, field='biocarburant_code',
                                         error='Biocarburant inconnu',
                                         value=biocarburant))
    else:
        biocarburant = None
        lot.biocarburant = None
        lot_errors.append(LotV2Error(lot=lot, field='biocarburant_code',
                                     error='Merci de préciser le Biocarburant',
                                     value=biocarburant))
    return lot_errors


def fill_matiere_premiere_info(lot_row, lot):
    lot_errors = []
    if 'matiere_premiere_code' in lot_row:
        matiere_premiere = lot_row['matiere_premiere_code']
        try:
            lot.matiere_premiere = MatierePremiere.objects.get(code=matiere_premiere)
        except Exception:
            lot.matiere_premiere = None
            lot_errors.append(LotV2Error(lot=lot, field='matiere_premiere_code',
                                         error='Matière Première inconnue',
                                         value=matiere_premiere))
    else:
        matiere_premiere = None
        lot.matiere_premiere = None
        lot_errors.append(LotV2Error(lot=lot, field='matiere_premiere_code',
                                     error='Merci de préciser la matière première',
                                     value=matiere_premiere))
    return lot_errors


def fill_volume_info(lot_row, lot):
    lot_errors = []
    if 'volume' in lot_row:
        volume = lot_row['volume']
        try:
            lot.volume = float(volume)
        except Exception:
            lot.volume = 0
            lot_errors.append(LotV2Error(lot=lot, field='volume',
                                         error='Format du volume incorrect', value=volume))
    else:
        lot_errors.append(LotV2Error(lot=lot, field='volume',
                                     error='Merci de préciser un volume', value=volume))
    return lot_errors


def fill_pays_origine_info(lot_row, lot):
    lot_errors = []
    if 'pays_origine_code' in lot_row:
        pays_origine = lot_row['pays_origine_code']
        try:
            lot.pays_origine = Pays.objects.get(code_pays=pays_origine)
        except Exception:
            lot.pays_origine = None
            lot_errors.append(LotV2Error(lot=lot, field='pays_origine_code', error='Pays inconnu', value=pays_origine))
    else:
        pays_origine = None
        lot.pays_origine = None
        lot_errors.append(LotV2Error(lot=lot, field='pays_origine_code', error='Merci de préciser le pays', value=pays_origine))
    return lot_errors


def fill_ghg_info(lot_row, lot):
    lot_errors = []
    lot.eec = 0
    if 'eec' in lot_row:
        eec = lot_row['eec']
        try:
            lot.eec = float(eec)
        except Exception:
            lot_errors.append(LotV2Error(lot=lot, field='eec', error='Format non reconnu', value=eec))

    lot.el = 0
    if 'el' in lot_row:
        el = lot_row['el']
        try:
            lot.el = float(el)
        except Exception:
            lot_errors.append(LotV2Error(lot=lot, field='el', error='Format non reconnu', value=el))

    lot.ep = 0
    if 'ep' in lot_row:
        ep = lot_row['ep']
        try:
            lot.ep = float(ep)
        except Exception:
            lot_errors.append(LotV2Error(lot=lot, field='ep', error='Format non reconnu', value=ep))

    lot.etd = 0
    if 'etd' in lot_row:
        etd = lot_row['etd']
        try:
            lot.etd = float(etd)
        except Exception:
            lot_errors.append(LotV2Error(lot=lot, field='etd', error='Format non reconnu', value=etd))

    lot.eu = 0
    if 'eu' in lot_row:
        eu = lot_row['eu']
        try:
            lot.eu = float(eu)
        except Exception:
            lot_errors.append(LotV2Error(lot=lot, field='eu', error='Format non reconnu', value=eu))

    lot.esca = 0
    if 'esca' in lot_row:
        esca = lot_row['esca']
        try:
            lot.esca = float(esca)
        except Exception:
            lot_errors.append(LotV2Error(lot=lot, field='esca', error='Format non reconnu', value=esca))

    lot.eccs = 0
    if 'eccs' in lot_row:
        eccs = lot_row['eccs']
        try:
            lot.eccs = float(eccs)
        except Exception:
            lot_errors.append(LotV2Error(lot=lot, field='eccs', error='Format non reconnu', value=eccs))

    lot.eccr = 0
    if 'eccr' in lot_row:
        eccr = lot_row['eccr']
        try:
            lot.eccr = float(eccr)
        except Exception:
            lot_errors.append(LotV2Error(lot=lot, field='eccr', error='Format non reconnu', value=eccr))

    lot.eee = 0
    if 'eee' in lot_row:
        eee = lot_row['eee']
        try:
            lot.eee = float(eee)
        except Exception:
            lot_errors.append(LotV2Error(lot=lot, field='eee', error='Format non reconnu', value=eee))

    # calculs ghg
    lot.ghg_total = round(lot.eec + lot.el + lot.ep + lot.etd + lot.eu - lot.esca - lot.eccs - lot.eccr - lot.eee, 2)
    lot.ghg_reference = 83.8
    lot.ghg_reduction = round((1.0 - (lot.ghg_total / lot.ghg_reference)) * 100.0, 2)
    return lot_errors


def fill_dae_data(lot_row, transaction):
    tx_errors = []
    transaction.dae = None
    if 'dae' in lot_row:
        dae = lot_row['dae']
        transaction.dae = dae
    if transaction.dae is None and transaction.is_mac is False:
        tx_errors.append(TransactionError(tx=transaction, field='dae', error="Merci de préciser le numéro de DAE/DAU", value=None))
    return tx_errors


def fill_delivery_date(lot_row, lot, transaction):
    tx_errors = []
    if 'delivery_date' not in lot_row or lot_row['delivery_date'] == '':
        transaction.ea_delivery_date = None
        lot.period = ''
        tx_errors.append(TransactionError(tx=transaction, field='ea_delivery_date', error="Merci de préciser la date de livraison", value=None))
    else:
        try:
            delivery_date = lot_row['delivery_date']
            if isinstance(delivery_date, datetime.datetime) or isinstance(delivery_date, datetime.date):
                dd = delivery_date
            else:
                year = int(delivery_date[0:4])
                month = int(delivery_date[5:7])
                day = int(delivery_date[8:10])
                dd = datetime.date(year=year, month=month, day=day)
            transaction.delivery_date = dd
            lot.period = dd.strftime('%Y-%m')
            TransactionError.objects.filter(tx=transaction, field='delivery_date').delete()
        except Exception:
            msg = "Format de date incorrect: veuillez entrer une date au format AAAA-MM-JJ"
            tx_errors.append(TransactionError(tx=transaction, field='delivery_date', error=msg, value=delivery_date))
    return tx_errors


def fill_client_data(entity, lot_row, transaction):
    tx_errors = []

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
    else:
        transaction.client_is_in_carbure = True
        transaction.carbure_client = entity
        transaction.unknown_client = ''
    return tx_errors


def fill_delivery_site_data(lot_row, transaction):
    tx_errors = []
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
    else:
        transaction.delivery_site_is_in_carbure = False
        transaction.carbure_delivery_site = None
        transaction.unknown_delivery_site = ''
        tx_errors.append(TransactionError(tx=transaction, field='delivery_site', value=None, error="Merci de préciser un site de livraison"))
    if transaction.delivery_site_is_in_carbure is False:
        if 'delivery_site_country' in lot_row:
            try:
                country = Pays.objects.get(code_pays=lot_row['delivery_site_country'])
                transaction.unknown_delivery_site_country = country
            except Exception:
                tx_errors.append(TransactionError(tx=transaction, field='delivery_site_country',
                                                  error='Champ production_site_country incorrect',
                                                  value=lot_row['delivery_site_country']))
        else:
            tx_errors.append(TransactionError(tx=transaction, field='delivery_site_country',
                                              error='Merci de préciser une valeur dans le champ production_site_country',
                                              value=None))
    return tx_errors


def load_lot(entity, user, lot_dict, source, transaction=None):
    lot_errors = []
    tx_errors = []

    # check for empty row
    if lot_dict.get('biocarburant_code', None) is None:
        return None, None, None, None

    if transaction is None:
        lot = LotV2()
        lot.added_by = entity
        lot.data_origin_entity = entity
        lot.added_by_user = user
        lot.source = source
    else:
        lot = transaction.lot

    lot_errors.append(fill_producer_info(entity, lot_dict, lot))
    lot_errors.append(fill_production_site_info(entity, lot_dict, lot))
    lot_errors.append(fill_biocarburant_info(lot_dict, lot))
    lot_errors.append(fill_matiere_premiere_info(lot_dict, lot))
    lot_errors.append(fill_volume_info(lot_dict, lot))
    lot_errors.append(fill_pays_origine_info(lot_dict, lot))
    lot_errors.append(fill_ghg_info(lot_dict, lot))
    lot.is_valid = False
    lot.save()

    if transaction is None:
        transaction = LotTransaction()
        transaction.lot = lot
        transaction.vendor_is_in_carbure = True
        transaction.carbure_vendor = entity
    transaction.is_mac = False
    if 'mac' in lot_dict and lot_dict['mac'] == 1:
        transaction.is_mac = True

    tx_errors.append(fill_dae_data(lot_dict, transaction))
    tx_errors.append(fill_delivery_date(lot_dict, lot, transaction))
    tx_errors.append(fill_client_data(entity, lot_dict, transaction))
    tx_errors.append(fill_delivery_site_data(lot_dict, transaction))
    transaction.ghg_total = lot.ghg_total
    transaction.ghg_reduction = lot.ghg_reduction
    transaction.champ_libre = lot_dict['champ_libre'] if 'champ_libre' in lot_dict else ''
    transaction.save()
    lot.save()
    return lot, transaction, lot_errors, tx_errors


def load_excel_file(entity, user, file):
    wb = openpyxl.load_workbook(file)
    try:
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
        lots_to_insert = []
        txs_to_insert = []
        lot_errors = []
        tx_errors = []
        for lot in lots:
            try:
                lot, tx, l_errors, t_errors = load_lot(entity, user, lot, 'EXCEL')
                if lot is None:
                    continue
                lots_loaded += 1
                lots_to_insert.append(lot)
                txs_to_insert.append(tx)
                lot_errors.append(l_errors)
                tx_errors.append(t_errors)
            except Exception as e:
                print('Could not load %s' % (lot))
                print(e)

        # below lines are for batch insert of Lots, Transactions and errors
        # it's a bit rough
        # with mysql, returned object from bulk_create do not contain ids
        # since LotTransaction object requires the Lot foreign key, we need to fetch the Lots after creation
        # and sort them to assign the Transaction to the correct Lot

        # 1: Batch insert of Lot objects
        LotV2.objects.bulk_create(lots_to_insert, batch_size=100)
        # 2: Fetch newly created lots
        new_lots = [lot for lot in LotV2.objects.filter(added_by=entity).order_by('-id')[0:len(lots_to_insert)]]
        # 3: Sort by ID (might be overkill but better safe than sorry)
        for lot, tx in zip(sorted(new_lots, key=lambda x: x.id), txs_to_insert):
            # 4: Assign lot.id to tx
            tx.lot_id = lot.id
        # 5: Batch insert transaction
        LotTransaction.objects.bulk_create(txs_to_insert, batch_size=100)

        # likewise, LotError and TransactionError require a foreign key
        # 6 assign lot.id to LotError
        for lot, errors in zip(sorted(new_lots, key=lambda x: x.id), lot_errors):
            for e in errors:
                e.lot_id = lot.id
        flat_errors = [item for sublist in lot_errors for item in sublist]
        LotV2Error.objects.bulk_create(flat_errors, batch_size=100)
        # 7 assign tx.id to TransactionError
        new_txs = [t for t in LotTransaction.objects.filter(lot__added_by=entity).order_by('-id')[0:len(lots_to_insert)]]
        for tx, errors in zip(sorted(new_txs, key=lambda x: x.id), tx_errors):
            for e in errors:
                e.tx_id = tx.id
        flat_tx_errors = [item for sublist in tx_errors for item in sublist]
        TransactionError.objects.bulk_create(flat_tx_errors, batch_size=100)
        return lots_loaded, total_lots
    except Exception:
        return False, False


def validate_lots(user, tx_ids):
    for tx_id in tx_ids:
        try:
            tx_id = int(tx_id)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': "tx_id must be an integer", 'extra': str(e)}, status=400)
        print('Trying to validate tx id %d' % (tx_id))
        try:
            tx = LotTransaction.objects.get(id=tx_id, lot__status='Draft')
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': "Draft not found", 'extra': str(e)}, status=400)

        rights = [r.entity for r in UserRights.objects.filter(user=user)]
        if tx.lot.added_by not in rights:
            return JsonResponse({'status': 'forbidden', 'message': "User not allowed"}, status=403)

        # make sure all mandatory fields are set
        tx_valid, error = tx_is_valid(tx)
        if not tx_valid:
            return JsonResponse({'status': 'error', 'message': "Invalid transaction: %s" % (error)}, status=400)

        lot_valid, error = lot_is_valid(tx.lot)
        if not lot_valid:
            return JsonResponse({'status': 'error', 'message': "Invalid lot: %s" % (error)}, status=400)

        # run sanity_checks
        sanity_check(tx.lot)
        blocking_sanity_checks = LotValidationError.objects.filter(lot=tx.lot, block_validation=True)
        if len(blocking_sanity_checks):
            tx.lot.is_valid = False
        else:
            tx.lot.is_valid = True
            tx.lot.carbure_id = generate_carbure_id(tx.lot)
            tx.lot.status = "Validated"
        # when the lot is added to mass balance, auto-accept
        if tx.carbure_client == tx.carbure_vendor:
            tx.delivery_status = 'A'
            tx.save()
        tx.lot.save()