import datetime
import openpyxl
from django.db.models import Q
from multiprocessing import Process
import pandas as pd

from django.http import JsonResponse
from core.models import LotV2, LotTransaction, LotV2Error, TransactionError, UserRights
from core.models import MatierePremiere, Biocarburant, Pays, Entity, ProductionSite, Depot
from core.models import LotValidationError
import dateutil.parser
from api.v3.sanity_checks import sanity_check, bulk_sanity_checks

def get_prefetched_data(entity):
    d = {}
    d['producers'] = {p.name: p for p in Entity.objects.filter(entity_type='Producteur')}
    d['countries'] = {p.code_pays: p for p in Pays.objects.all()}
    d['biocarburants'] = {b.code: b for b in Biocarburant.objects.all()}
    d['matieres_premieres'] = {m.code: m for m in MatierePremiere.objects.all()}
    d['production_sites'] = {ps.name: ps for ps in ProductionSite.objects.filter(producer=entity)}
    d['depots'] = {d.depot_id: d for d in Depot.objects.all()}
    d['clients'] = {c.name: c for c in Entity.objects.filter(entity_type__in=['Producteur', 'Opérateur', 'Trader'])}
    return d

def tx_is_valid(tx):
    is_valid = True

    # make sure all mandatory fields are set
    if not tx.dae:
        error = 'DAE manquant'
        TransactionError.objects.update_or_create(tx=tx, field='dae', value='', error=error)
        is_valid = False
    if not tx.delivery_site_is_in_carbure and not tx.unknown_delivery_site:
        error = 'Site de livraison manquant'
        TransactionError.objects.update_or_create(tx=tx, field='unknown_delivery_site', value='', error=error)
        is_valid = False
    if tx.delivery_site_is_in_carbure and not tx.carbure_delivery_site:
        error = 'Site de livraison manquant'
        TransactionError.objects.update_or_create(tx=tx, field='carbure_delivery_site', value='', error=error)
        is_valid = False
    if not tx.delivery_date:
        error = 'Date de livraison manquante'
        TransactionError.objects.update_or_create(tx=tx, field='delivery_date', value='', error=error)
        is_valid = False

    today = datetime.date.today()
    if (tx.delivery_date - today) > datetime.timedelta(days=3650) or (tx.delivery_date - today) < datetime.timedelta(days=-3650):
        error = "Date incorrecte: veuillez entrer des données récentes (%s)" % (tx.delivery_date.strftime('%d/%m/%Y'))
        TransactionError.objects.update_or_create(tx=tx, field='delivery_date', value='', error=error)
        is_valid = False

    if tx.client_is_in_carbure and not tx.carbure_client:
        error = 'Veuillez renseigner un client'
        TransactionError.objects.update_or_create(tx=tx, field='carbure_client', value='', error=error)
        is_valid = False
    if not tx.client_is_in_carbure and not tx.unknown_client:
        error = 'Veuillez renseigner un client'
        TransactionError.objects.update_or_create(tx=tx, field='unknown_client', value='', error=error)
        is_valid = False

    if not tx.delivery_site_is_in_carbure and not tx.unknown_delivery_site:
        error = 'Veuillez renseigner un site de livraison'
        TransactionError.objects.update_or_create(tx=tx, field='unknown_delivery_site', value='', error=error)
        is_valid = False

    if not tx.delivery_site_is_in_carbure and not tx.unknown_delivery_site_country:
        error = 'Veuillez renseigner un pays de livraison'
        TransactionError.objects.update_or_create(tx=tx, field='unknown_delivery_site_country', value='', error=error)
        is_valid = False        

    if tx.unknown_delivery_site_country is not None and tx.unknown_delivery_site_country.is_in_europe and tx.lot.pays_origine is None:
        error = "Veuillez renseigner le pays d'origine de la matière première - Marché européen"
        TransactionError.objects.update_or_create(tx=tx, field='unknown_delivery_site_country', value='', error=error)
        is_valid = False
    if tx.carbure_delivery_site is not None and tx.carbure_delivery_site.country.is_in_europe and tx.lot.pays_origine is None:
        error = "Veuillez renseigner le pays d'origine de la matière première - Marché européen"
        TransactionError.objects.update_or_create(tx=tx, field='carbure_delivery_site', value='', error=error)
        is_valid = False
    return is_valid


def lot_is_valid(lot):
    is_valid = True
    if not lot.volume:
        LotV2Error.objects.update_or_create(lot=lot, field='volume', value='', error='Veuillez renseigner le volume')
        is_valid = False

    if not lot.parent_lot:
        if not lot.biocarburant:
            error = 'Veuillez renseigner le type de biocarburant'
            LotV2Error.objects.update_or_create(lot=lot, field='biocarburant', value='', error=error)
            is_valid = False
        if not lot.matiere_premiere:
            error = 'Veuillez renseigner la matière première'
            LotV2Error.objects.update_or_create(lot=lot, field='matiere_premiere', value='', error=error)
            is_valid = False
        if lot.producer_is_in_carbure and lot.carbure_production_site is None:
            error = 'Veuillez préciser le site de production'
            LotV2Error.objects.update_or_create(lot=lot, field='carbure_production_site', value='', error=error)
            is_valid = False
        if not lot.producer_is_in_carbure:
            if not lot.unknown_production_site_com_date:
                error = "Veuillez renseigner la date de mise en service de l'usine"
                LotV2Error.objects.update_or_create(lot=lot, field='unknown_production_site_com_date', value='', error=error)
                is_valid = False
            if not lot.unknown_production_site_reference:
                error = "Veuillez renseigner le certificat de l'usine de production ou du fournisseur"
                LotV2Error.objects.update_or_create(lot=lot, field='unknown_production_site_reference', value='', error=error)
                is_valid = False
    return is_valid


def generate_carbure_id(lot):
    today = datetime.date.today()
    # [PAYS][YYMM]P[IDProd]-[1....]-([S123])
    # FR2002P001-1
    country = '00'
    if lot.carbure_production_site and lot.carbure_production_site.country:
        country = lot.carbure_production_site.country.code_pays
    yymm = today.strftime('%y%m')
    idprod = '000'
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


def fill_producer_info(entity, lot_row, lot, prefetched_data):
    lot_errors = []
    all_producers = prefetched_data['producers']
    if 'producer' in lot_row and lot_row['producer'] is not None:
        # check if we know the producer
        if lot_row['producer'].strip() == entity.name:
            # it's me
            lot.producer_is_in_carbure = True
            lot.carbure_producer = entity
            lot.unknown_producer = ''
        else:
            # it's not me. do we know this producer ?
            if lot_row['producer'] in all_producers:
                # yes we do
                # in this case, the producer should declare its production directly in Carbure
                # we cannot allow someone else to declare for them
                lot.producer_is_in_carbure = False
                lot.carbure_producer = None
                lot.unknown_producer = ''
                error = LotV2Error(lot=lot, field='carbure_producer',
                                   error="Vous ne pouvez pas déclarer des lots d'un producteur déjà inscrit sur Carbure",
                                   value=lot_row['producer'])
                lot_errors.append(error)                
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
        # no producer column = simple template (producer)
        if entity.entity_type == 'Producteur':
            # current entity is the producer
            lot.producer_is_in_carbure = True
            lot.carbure_producer = entity
            lot.unknown_producer = ''
        else:
            lot.producer_is_in_carbure = False
            lot.carbure_producer = None
            lot.unknown_producer = ''
    return lot_errors


def fill_production_site_info(entity, lot_row, lot, prefetched_data):
    lot_errors = []
    my_production_sites = prefetched_data['production_sites']
    countries = prefetched_data['countries']
    if 'production_site' in lot_row:
        production_site = lot_row['production_site']
        if lot.producer_is_in_carbure:
            if production_site in my_production_sites:
                lot.carbure_production_site = my_production_sites[production_site]
                lot.production_site_is_in_carbure = True
                lot.unknown_production_site = ''
            else:
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
    if lot.producer_is_in_carbure is False:
        if 'production_site_country' in lot_row:
            production_site_country = lot_row['production_site_country']
            if production_site_country is None:
                lot.unknown_production_country = None
            else:
                if production_site_country in countries:
                    lot.unknown_production_country = countries[production_site_country]
                else:
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
            try:
                com_date = lot_row['production_site_commissioning_date']
                if isinstance(com_date, datetime.datetime) or isinstance(com_date, datetime.date):
                    dd = com_date
                else:
                    year = int(com_date[0:4])
                    month = int(com_date[5:7])
                    day = int(com_date[8:10])
                    dd = datetime.date(year=year, month=month, day=day)
                lot.unknown_production_site_com_date = dd
            except Exception:
                msg = "Format de date incorrect: veuillez entrer une date au format AAAA-MM-JJ"
                error = LotV2Error(lot=lot, field='unknown_production_site_com_date',
                                    error=msg,
                                    value=lot_row['production_site_commissioning_date'])
                lot_errors.append(error)
        else:
            lot.unknown_production_site_com_date = None
        if 'double_counting_registration' in lot_row:
            lot.unknown_production_site_dbl_counting = lot_row['double_counting_registration']
        else:
            lot.unknown_production_site_dbl_counting = ''
    return lot_errors


def fill_biocarburant_info(lot_row, lot, prefetched_data):
    lot_errors = []
    biocarburants = prefetched_data['biocarburants']
    if 'biocarburant_code' in lot_row:
        biocarburant = lot_row['biocarburant_code']
        if biocarburant in biocarburants:
            lot.biocarburant = biocarburants[biocarburant]
        else:
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


def fill_matiere_premiere_info(lot_row, lot, prefetched_data):
    lot_errors = []
    mps = prefetched_data['matieres_premieres']
    if 'matiere_premiere_code' in lot_row:
        matiere_premiere = lot_row['matiere_premiere_code']
        if matiere_premiere in mps:
            lot.matiere_premiere = mps[matiere_premiere]
        else:
            lot.matiere_premiere = None
            lot_errors.append(LotV2Error(lot=lot, field='matiere_premiere_code',
                                         error='Matière Première inconnue',
                                         value=matiere_premiere))
    else:
        lot.matiere_premiere = None
        lot_errors.append(LotV2Error(lot=lot, field='matiere_premiere_code',
                                     error='Merci de préciser la matière première',
                                     value=None))
    return lot_errors


def fill_volume_info(lot_row, lot):
    lot_errors = []
    if 'volume' in lot_row:
        volume = lot_row['volume']
        try:
            lot.volume = float(volume)
            if lot.volume <= 0:
                lot_errors.append(LotV2Error(lot=lot, field='volume',
                                            error='Le volume doit être supérieur à 0', value=volume))
        except Exception:
            lot.volume = 0
            lot_errors.append(LotV2Error(lot=lot, field='volume',
                                         error='Format du volume incorrect', value=volume))
    else:
        lot.volume = 0
        lot_errors.append(LotV2Error(lot=lot, field='volume',
                                     error='Merci de préciser un volume', value=''))
    return lot_errors


def fill_pays_origine_info(lot_row, lot, prefetched_data):
    lot_errors = []
    countries = prefetched_data['countries']
    if 'pays_origine_code' in lot_row:
        pays_origine = lot_row['pays_origine_code']
        if pays_origine in countries:
            lot.pays_origine = countries[pays_origine]
        else:
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
    if 'eec' in lot_row and lot_row['eec'] is not None and lot_row['eec'] != '':
        eec = lot_row['eec']
        try:
            lot.eec = float(eec)
        except Exception:
            lot_errors.append(LotV2Error(lot=lot, field='eec', error='Format non reconnu', value=eec))

    lot.el = 0
    if 'el' in lot_row and lot_row['el'] is not None and lot_row['el'] != '':
        el = lot_row['el']
        try:
            lot.el = float(el)
        except Exception:
            lot_errors.append(LotV2Error(lot=lot, field='el', error='Format non reconnu', value=el))

    lot.ep = 0
    if 'ep' in lot_row and lot_row['ep'] is not None and lot_row['ep'] != '':
        ep = lot_row['ep']
        try:
            lot.ep = float(ep)
        except Exception:
            lot_errors.append(LotV2Error(lot=lot, field='ep', error='Format non reconnu', value=ep))

    lot.etd = 0
    if 'etd' in lot_row and lot_row['etd'] is not None and lot_row['etd'] != '':
        etd = lot_row['etd']
        try:
            lot.etd = float(etd)
        except Exception:
            lot_errors.append(LotV2Error(lot=lot, field='etd', error='Format non reconnu', value=etd))

    lot.eu = 0
    if 'eu' in lot_row and lot_row['eu'] is not None and lot_row['eu'] != '':
        eu = lot_row['eu']
        try:
            lot.eu = float(eu)
        except Exception:
            lot_errors.append(LotV2Error(lot=lot, field='eu', error='Format non reconnu', value=eu))

    lot.esca = 0
    if 'esca' in lot_row and lot_row['esca'] is not None and lot_row['esca'] != '':
        esca = lot_row['esca']
        try:
            lot.esca = float(esca)
        except Exception:
            lot_errors.append(LotV2Error(lot=lot, field='esca', error='Format non reconnu', value=esca))

    lot.eccs = 0
    if 'eccs' in lot_row and lot_row['eccs'] is not None and lot_row['eccs'] != '':
        eccs = lot_row['eccs']
        try:
            lot.eccs = float(eccs)
        except Exception:
            lot_errors.append(LotV2Error(lot=lot, field='eccs', error='Format non reconnu', value=eccs))

    lot.eccr = 0
    if 'eccr' in lot_row and lot_row['eccr'] is not None and lot_row['eccr'] != '':
        eccr = lot_row['eccr']
        try:
            lot.eccr = float(eccr)
        except Exception:
            lot_errors.append(LotV2Error(lot=lot, field='eccr', error='Format non reconnu', value=eccr))

    lot.eee = 0
    if 'eee' in lot_row and lot_row['eee'] is not None and lot_row['eee'] != '':
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
    transaction.dae = ''
    if 'dae' in lot_row:
        dae = lot_row['dae']
        if dae is not None:
            transaction.dae = dae
    if transaction.dae == '' and transaction.is_mac is False:
        tx_errors.append(TransactionError(tx=transaction, field='dae', error="Merci de préciser le numéro de DAE/DAU", value=None))
    return tx_errors


def fill_delivery_date(lot_row, lot, transaction):
    today = datetime.date.today()
    tx_errors = []
    if 'delivery_date' not in lot_row or lot_row['delivery_date'] == '' or lot_row['delivery_date'] is None:
        transaction.delivery_date = today
        lot.period = today.strftime('%Y-%m')
    else:
        try:
            delivery_date = lot_row['delivery_date']
            if isinstance(delivery_date, datetime.datetime) or isinstance(delivery_date, datetime.date):
                dd = delivery_date
            else:
                dd = dateutil.parser.parse(delivery_date, dayfirst=True)
            transaction.delivery_date = dd
            lot.period = dd.strftime('%Y-%m')
        except Exception as e:
            print(e)
            transaction.delivery_date = None
            lot.period = today.strftime('%Y-%m')
            msg = "Format de date incorrect: veuillez entrer une date au format AAAA-MM-JJ (%s)" % (lot_row['delivery_date'])
            tx_errors.append(TransactionError(tx=transaction, field='delivery_date', error=msg, value=delivery_date))
    return tx_errors


def fill_client_data(entity, lot_row, transaction, prefetched_data):
    tx_errors = []
    clients = prefetched_data['clients']
    if entity.entity_type == 'Opérateur':
        transaction.client_is_in_carbure = True
        transaction.carbure_client = entity
        transaction.unknown_client = ''
    elif 'client' in lot_row and lot_row['client'] is not None and lot_row['client'] != '':
        client = lot_row['client']
        if client in clients:
            transaction.client_is_in_carbure = True
            transaction.carbure_client = clients[client]
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


def fill_vendor_data(entity, lot_row, transaction):
    tx_errors = []
    # by default, assume we are the vendor / supplier
    transaction.vendor_is_in_carbure = True
    transaction.carbure_vendor = entity 
    transaction.unknown_vendor = None
    if 'vendor' in lot_row:
        transaction.vendor_is_in_carbure = False
        transaction.carbure_vendor = None
        transaction.unknown_vendor = lot_row['vendor']
    else:
        # do nothing unless we are Operator
        if entity.entity_type == 'Opérateur':
            # as an operator, I am saving lots in Carbure but not specifying who sold them to me.
            # so be it
            transaction.vendor_is_in_carbure = False
            transaction.carbure_vendor = None
            transaction.unknown_vendor = ''
    return tx_errors

def fill_delivery_site_data(lot_row, transaction, prefetched_data):
    tx_errors = []
    depots = prefetched_data['depots']
    countries = prefetched_data['countries']
    if 'delivery_site' in lot_row and lot_row['delivery_site'] is not None:
        delivery_site = str(lot_row['delivery_site'])
        if delivery_site in depots:
            transaction.delivery_site_is_in_carbure = True
            transaction.carbure_delivery_site = depots[delivery_site]
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
            country_code = lot_row['delivery_site_country']
            if country_code in countries: 
                country = countries[country_code]
                transaction.unknown_delivery_site_country = country
            else:
                tx_errors.append(TransactionError(tx=transaction, field='delivery_site_country',
                                                  error='Champ production_site_country incorrect',
                                                  value=lot_row['delivery_site_country']))
        else:
            tx_errors.append(TransactionError(tx=transaction, field='delivery_site_country',
                                              error='Merci de préciser une valeur dans le champ production_site_country',
                                              value=None))
    return tx_errors

def load_mb_lot(prefetched_data, entity, user, lot_dict, source):
    lot_errors = []
    tx_errors = []

    # check for empty row
    if lot_dict.get('carbure_id', None) is None:
        return None, None, None, None
    carbure_id = lot_dict['carbure_id']
    # get source transaction
    try:
        source_tx = LotTransaction.objects.get(lot__carbure_id=carbure_id)
        source_lot = LotV2.objects.get(id=source_tx.lot.id)
    except Exception:
        print('Could not find carbure_id %s' % (carbure_id))
        return None, None, None, None
    lot = source_tx.lot

    if source_tx.carbure_client == entity and source_tx.delivery_status == 'A' and lot.fused_with is None:
        # I am the client of this lot, I have accepted it and it's not fused with anything else
        # this lot is currently in my mass balance
        pass
    else:
        return None, None, None, None

    # let's create a new lot and transaction
    lot.pk = None
    lot.parent_lot = source_lot
    lot.added_by = entity
    lot.data_origin_entity = lot.parent_lot.data_origin_entity
    lot.added_by_user = user
    lot.status = 'Draft'
    lot.carbure_id = ''
    lot.is_fused = False
    lot.source = 'EXCEL'
    lot_errors.append(fill_volume_info(lot_dict, lot))

    transaction = LotTransaction()
    # done in bulk_insert
    # transaction.lot = lot
    transaction.vendor_is_in_carbure = True
    transaction.carbure_vendor = entity

    tx_errors.append(fill_dae_data(lot_dict, transaction))
    tx_errors.append(fill_delivery_date(lot_dict, lot, transaction))
    tx_errors.append(fill_client_data(entity, lot_dict, transaction, prefetched_data, ))
    tx_errors.append(fill_delivery_site_data(lot_dict, transaction, prefetched_data, ))
    transaction.ghg_total = lot.ghg_total
    transaction.ghg_reduction = lot.ghg_reduction
    transaction.champ_libre = lot_dict['champ_libre'] if 'champ_libre' in lot_dict else ''
    lot_errors = [item for sublist in lot_errors for item in sublist]
    tx_errors = [item for sublist in tx_errors for item in sublist]
    return lot, transaction, lot_errors, tx_errors

def load_lot(prefetched_data, entity, user, lot_dict, source, transaction=None):
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

    lot_errors += fill_producer_info(entity, lot_dict, lot, prefetched_data)
    lot_errors += fill_production_site_info(entity, lot_dict, lot, prefetched_data)
    lot_errors += fill_biocarburant_info(lot_dict, lot, prefetched_data)
    lot_errors += fill_matiere_premiere_info(lot_dict, lot, prefetched_data)
    lot_errors += fill_volume_info(lot_dict, lot)
    lot_errors += fill_pays_origine_info(lot_dict, lot, prefetched_data)
    lot_errors += fill_ghg_info(lot_dict, lot)
    lot.is_valid = False

    if transaction is None:
        transaction = LotTransaction()
    transaction.is_mac = False
    if 'mac' in lot_dict and lot_dict['mac'] == 1:
        transaction.is_mac = True

    tx_errors += fill_dae_data(lot_dict, transaction)
    tx_errors += fill_delivery_date(lot_dict, lot, transaction)
    tx_errors += fill_client_data(entity, lot_dict, transaction, prefetched_data)
    tx_errors += fill_vendor_data(entity, lot_dict, transaction)
    tx_errors += fill_delivery_site_data(lot_dict, transaction, prefetched_data)
    transaction.ghg_total = lot.ghg_total
    transaction.ghg_reduction = lot.ghg_reduction
    transaction.champ_libre = lot_dict['champ_libre'] if 'champ_libre' in lot_dict else ''
    return lot, transaction, lot_errors, tx_errors


def load_excel_file(entity, user, file, mass_balance=False):
    print('File received %s' % (datetime.datetime.now()))

    # prefetch some data
    prefetched_data = get_prefetched_data(entity)

    try:
        df = pd.read_excel(file)
        df.fillna('', inplace=True)
        total_lots = len(df)
        lots_loaded = 0
        lots_to_insert = []
        txs_to_insert = []
        lot_errors = []
        tx_errors = []
        print('File read %s' % (datetime.datetime.now()))
        for row in df.iterrows():
            lot_row = row[1]
            try:
                if mass_balance:
                    lot, tx, l_errors, t_errors = load_mb_lot(prefetched_data, entity, user, lot_row, 'EXCEL')
                else:
                    lot, tx, l_errors, t_errors = load_lot(prefetched_data, entity, user, lot_row, 'EXCEL')
                if lot is None:
                    continue
                lots_loaded += 1
                lots_to_insert.append(lot)
                txs_to_insert.append(tx)
                lot_errors.append(l_errors)
                tx_errors.append(t_errors)
            except Exception as e:
                print(e)
                print(lot_row)
        print('File processed %s' % (datetime.datetime.now()))
        bulk_insert(entity, lots_to_insert, txs_to_insert, lot_errors, tx_errors)
        print('Lots loaded in database %s' % (datetime.datetime.now()))
        return lots_loaded, total_lots
    except Exception as e:
        print(e)
        return False, False


def bulk_insert(entity, lots_to_insert, txs_to_insert, lot_errors, tx_errors):
    print('Starting bulk_insert %s' % (datetime.datetime.now()))
    # below lines are for batch insert of Lots, Transactions and errors
    # it's a bit rough
    # with mysql, returned object from bulk_create do not contain ids
    # since LotTransaction object requires the Lot foreign key, we need to fetch the Lots after creation
    # and sort them to assign the Transaction to the correct Lot

    # 1: Batch insert of Lot objects
    LotV2.objects.bulk_create(lots_to_insert, batch_size=100)
    # 2: Fetch newly created lots
    new_lots = [lot for lot in LotV2.objects
        .select_related('matiere_premiere', 'biocarburant', 'pays_origine', 'carbure_production_site')
        .filter(added_by=entity).order_by('-id')[0:len(lots_to_insert)]
    ]
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
    # 8 run sanity checks
    print('calling bulk_sanity_check in background %s' % (datetime.datetime.now()))
    bulk_sanity_checks(new_lots)
    #p = Process(target=bulk_sanity_checks, args=(new_lots,))
    #p.start()
    return new_lots, new_txs


def validate_lots(user, tx_ids):
    for tx_id in tx_ids:
        try:
            tx_id = int(tx_id)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': "tx_id must be an integer", 'extra': str(e)}, status=400)
        print('Trying to validate tx id %d' % (tx_id))
        try:
            tx = LotTransaction.objects.get(Q(id=tx_id), Q(lot__status='Draft') | Q(delivery_status__in=['AA', 'AC', 'R']))
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': "Draft not found", 'extra': str(e)}, status=400)

        rights = [r.entity for r in UserRights.objects.filter(user=user)]
        if tx.lot.added_by not in rights:
            return JsonResponse({'status': 'forbidden', 'message': "User not allowed"}, status=403)

        # make sure all mandatory fields are set
        tx_valid = tx_is_valid(tx)
        lot_valid = lot_is_valid(tx.lot)
        # run sanity_checks
        is_sane = bulk_sanity_checks([tx.lot])[0]
        print('tx valid %s lot valid %s is_sane %s' % (tx_valid, lot_valid, is_sane))

        if not is_sane or not lot_valid or not tx_valid:
            tx.lot.is_valid = False
        else:
            tx.lot.is_valid = True
            tx.lot.carbure_id = generate_carbure_id(tx.lot)
            tx.lot.status = "Validated"

            # when the lot is added to mass balance, auto-accept
            if tx.carbure_client == tx.carbure_vendor:
                tx.delivery_status = 'A'
            if tx.delivery_status in ['AA', 'AC', 'R']:
                tx.delivery_status = 'AA'
        
        tx.save()
        tx.lot.save()

    return JsonResponse({'status': 'success'})