import datetime
import openpyxl
from django import db
from django.db.models import Q, Count
from multiprocessing import Process
import numpy as np
import traceback
import os

import pandas as pd
from typing import TYPE_CHECKING, Dict, List, Optional
from pandas._typing import FilePathOrBuffer, Scalar
from django.db import transaction


from core.models import LotV2, LotTransaction, UserRights, GenericError, TransactionUpdateHistory
from core.models import MatierePremiere, Biocarburant, Pays, Entity, ProductionSite, Depot, SustainabilityDeclaration

from certificates.models import ISCCCertificate, EntityISCCTradingCertificate
from certificates.models import DBSCertificate, EntityDBSTradingCertificate
from certificates.models import REDCertCertificate, EntityREDCertTradingCertificate
from certificates.models import EntitySNTradingCertificate, SNCertificate

from core.emails import send_reject_email, send_accepted_lot_in_correction_email

import dateutil.parser
from api.v3.sanity_checks import bulk_sanity_checks, tx_is_valid, lot_is_valid


def try_get_certificate(certificate):
    d = {'holder': '',
         'valid_until': '',
         'valid_from': '',
         'matches': 0,
         'found': False,
         }
    iscc = ISCCCertificate.objects.filter(certificate_id=certificate)
    dbs = DBSCertificate.objects.filter(certificate_id=certificate)
    red = REDCertCertificate.objects.filter(certificate_id=certificate)
    sn = SNCertificate.objects.filter(certificate_id=certificate)
    count = iscc.count() + dbs.count() + red.count() + sn.count()
    if count == 0:
        return d
    if count > 1:
        d['matches'] = count
        return d
    d['matches'] = 1
    if iscc.count() == 1:
        d['holder'] = iscc[0].certificate_holder
        d['valid_until'] = iscc[0].valid_until
        d['valid_from'] = iscc[0].valid_from
    if dbs.count() == 1:
        d['holder'] = dbs[0].certificate_holder
        d['valid_until'] = dbs[0].valid_until
        d['valid_from'] = dbs[0].valid_from
    if red.count() == 1:
        d['holder'] = red[0].certificate_holder
        d['valid_until'] = red[0].valid_until
        d['valid_from'] = red[0].valid_from
    if sn.count() == 1:
        d['holder'] = sn[0].certificate_holder
        d['valid_until'] = sn[0].valid_until
        d['valid_from'] = sn[0].valid_from
    return d


def check_certificates(tx):
    d = {
         'production_site_certificate': None,
         'supplier_certificate': None,
         'vendor_certificate': None
        }
    # production site certificate
    if tx.lot.carbure_production_site_reference:
        d['production_site_certificate'] = try_get_certificate(tx.lot.carbure_production_site_reference)
    if tx.lot.unknown_production_site_reference:
        d['production_site_certificate'] = try_get_certificate(tx.lot.unknown_production_site_reference)
    if tx.lot.unknown_supplier_certificate:
        d['supplier_certificate'] = try_get_certificate(tx.lot.unknown_supplier_certificate)
    if tx.carbure_vendor_certificate:
        d['vendor_certificate'] = try_get_certificate(tx.carbure_vendor_certificate)
    return d

def get_uploaded_files_directory():
    directory = '/app/files'
    if not os.path.exists(directory):
        try:
            os.makedirs(directory)
        except:
            return '/tmp'
    return directory

def calculate_ghg(lot):
    lot.ghg_total = lot.eec + lot.el + lot.ep + lot.etd + lot.eu - lot.esca - lot.eccs - lot.eccr - lot.eee
    lot.ghg_reference = 83.8
    lot.ghg_reduction = round((1.0 - (lot.ghg_total / lot.ghg_reference)) * 100.0, 2)


def convert_cell(cell, convert_float: bool) -> Scalar:
    from openpyxl.cell.cell import TYPE_BOOL, TYPE_ERROR, TYPE_NUMERIC

    if cell.is_date:
        return cell.value
    elif cell.data_type == TYPE_ERROR:
        return np.nan
    elif cell.data_type == TYPE_BOOL:
        return bool(cell.value)
    elif cell.value is None:
        return ""  # compat with xlrd
    elif cell.data_type == TYPE_NUMERIC:
        # GH5394
        if convert_float:
            val = int(cell.value)
            if val == cell.value:
                return val
        else:
            return float(cell.value)

    return cell.value


def get_sheet_data(sheet, convert_float: bool) -> List[List[Scalar]]:
    data: List[List[Scalar]] = []
    for row in sheet.rows:
        data.append([convert_cell(cell, convert_float) for cell in row])
    return data


def send_lot_from_stock(rights, tx, prefetched_data):
    lot = tx.lot
    if tx.lot.added_by not in rights:
        return False, "User not allowed to send this tx"

    # only allow to send drafts
    if tx.lot.status != 'Draft':
        return False, "Tx already sent"

    # make sure all mandatory fields are set
    tx_valid = tx_is_valid(tx, prefetched_data)
    if not tx_valid:
        return False, 'Transaction invalide'
    lot_valid = lot_is_valid(tx)
    if not lot_valid:
        return False, 'Lot invalide'

    # check if we can extract the lot from the parent
    if not lot.parent_lot:
        return False, 'Tx does not have parent'

    if lot.volume > lot.parent_lot.remaining_volume:
        return False, 'Quantité disponible dans la mass balance insuffisante: Dispo %d litres, lot %d litres' % (lot.parent_lot.remaining_volume, lot.volume)

    lot.carbure_id = generate_carbure_id(lot) + 'S'
    lot.status = LotV2.VALIDATED
    lot.save()
    lot.parent_lot.remaining_volume -= lot.volume
    lot.parent_lot.save()
    if tx.is_mac:
        tx.delivery_status = LotTransaction.ACCEPTED
        tx.save()
    return True, ''


def check_duplicates(new_txs, background=True):
    if background:
        db.connections.close_all()
    new_daes = [t.dae for t in new_txs]
    nb_duplicates = 0
    duplicates = LotTransaction.objects.filter(dae__in=new_daes, lot__status='Validated', is_forwarded=False).values('dae', 'lot__biocarburant_id', 'lot__volume', 'lot__ghg_total').annotate(count=Count('dae')).filter(count__gt=1)
    if duplicates.count() > 0:
        # print('Found duplicates')
        # print(duplicates)
        # method:
        # when a duplicate exists, the first validated one is right
        for d in duplicates:
            dae = d['dae']
            biocarburant_id = d['lot__biocarburant_id']
            volume = d['lot__volume']
            ghg_total = d['lot__ghg_total']
            matches = LotTransaction.objects.filter(dae=dae, lot__biocarburant_id=biocarburant_id, lot__volume=volume, lot__ghg_total=ghg_total, lot__status='Validated').order_by('id')
            # find the "best" lot
            # the best source is the producer
            best_matches = LotTransaction.objects.filter(dae=dae, lot__biocarburant_id=biocarburant_id, lot__volume=volume, lot__ghg_total=ghg_total, lot__status='Validated', lot__data_origin_entity__entity_type='Producteur').order_by('id')
            if best_matches.count() > 0:
                first_valid = best_matches[0]
            else:
                first_valid = matches[0]
            for m in matches[1:]:
                nb_duplicates += 1
                # there is already a tx with a valid lot and this DAE/volume/biocarburant
                # it can happen if the producer has already created the tx and the operator tries to upload it
                # or the operator has created it and the producer is trying to upload it
                # or a user has validated a duplicate

                # take the existing tx. if vendor is not in carbure, assume we are the vendor
                # if client not in carbure, assume we are the client
                if not first_valid.client_is_in_carbure and m.client_is_in_carbure:
                    # assume we are the client
                    first_valid.client_is_in_carbure = True
                    first_valid.carbure_client = m.carbure_client
                    first_valid.delivery_site_is_in_carbure = m.delivery_site_is_in_carbure
                    first_valid.carbure_delivery_site = m.carbure_delivery_site
                    first_valid.unknown_delivery_site = m.unknown_delivery_site
                    first_valid.unknown_delivery_site_country = m.unknown_delivery_site_country
                elif not first_valid.lot.producer_is_in_carbure and m.lot.producer_is_in_carbure:
                    # we are the producer
                    first_valid.producer_is_in_carbure = True
                    first_valid.lot.carbure_producer = m.lot.carbure_producer
                    first_valid.lot.production_site_is_in_carbure = m.lot.production_site_is_in_carbure
                    first_valid.lot.carbure_production_site = m.lot.carbure_production_site
                else:
                    # assume it's just a duplicate, do nothing
                    # no need to update the original lot
                    pass
            first_valid.lot.save()
            first_valid.save()
            matches.exclude(id=first_valid.id).delete()
        LotV2.objects.filter(tx_lot__isnull=True).delete()
    return nb_duplicates

def get_prefetched_data(entity=None):
    lastyear = datetime.date.today() - datetime.timedelta(days=365)
    d = {}
    d['producers'] = {p.name: p for p in Entity.objects.filter(entity_type='Producteur')}
    d['countries'] = {p.code_pays: p for p in Pays.objects.all()}
    d['biocarburants'] = {b.code: b for b in Biocarburant.objects.all()}
    d['matieres_premieres'] = {m.code: m for m in MatierePremiere.objects.all()}
    if entity:
        # get only my production sites
        d['production_sites'] = {ps.name: ps for ps in ProductionSite.objects.prefetch_related('productionsiteinput_set', 'productionsiteoutput_set', 'productionsitecertificate_set').filter(producer=entity)}
        # get all my linked certificates
        my_vendor_certificates = []
        my_vendor_certificates += [c.certificate.certificate_id for c in EntityISCCTradingCertificate.objects.filter(entity=entity)]
        my_vendor_certificates += [c.certificate.certificate_id for c in EntityDBSTradingCertificate.objects.filter(entity=entity)]
        my_vendor_certificates += [c.certificate.certificate_id for c in EntityREDCertTradingCertificate.objects.filter(entity=entity)]
        my_vendor_certificates += [c.certificate.certificate_id for c in EntitySNTradingCertificate.objects.filter(entity=entity)]
        d['my_vendor_certificates'] = my_vendor_certificates
    else:
        d['production_sites'] = {ps.name: ps for ps in ProductionSite.objects.prefetch_related('productionsiteinput_set', 'productionsiteoutput_set', 'productionsitecertificate_set').all()}
    d['depots'] = {d.depot_id.lstrip('0'): d for d in Depot.objects.all()}
    d['clients'] = {c.name.upper(): c for c in Entity.objects.filter(entity_type__in=['Producteur', 'Opérateur', 'Trader'])}
    d['iscc_certificates'] = {c.certificate_id.upper(): c for c in ISCCCertificate.objects.filter(valid_until__gte=lastyear)}
    d['2bs_certificates'] = {c.certificate_id.upper(): c for c in DBSCertificate.objects.filter(valid_until__gte=lastyear)}
    d['redcert_certificates'] = {c.certificate_id.upper(): c for c in REDCertCertificate.objects.filter(valid_until__gte=lastyear)}
    d['sn_certificates'] = [c.certificate_id.upper() for c in SNCertificate.objects.filter(valid_until__gte=lastyear)]
    return d


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
        stripped_producer = lot_row['producer'].strip()

        if stripped_producer == entity.name:
            # it's me
            lot.producer_is_in_carbure = True
            lot.carbure_producer = entity
            lot.unknown_producer = ''
        else:
            # it's not me. do we know this producer ?
            if stripped_producer in all_producers:
                lot.producer_is_in_carbure = True
                lot.carbure_producer = all_producers[stripped_producer]
                lot.unknown_producer = ''
            else:
                # ok, unknown producer. allow importation
                lot.producer_is_in_carbure = False
                lot.carbure_producer = None
                lot.unknown_producer = stripped_producer
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


def fill_production_site_info(entity, lot_row, lot, tx, prefetched_data):
    lot_errors = []

    # only the data_origin_entity is allowed to change this
    if lot.data_origin_entity != entity:
        return lot_errors

    my_production_sites = prefetched_data['production_sites']
    countries = prefetched_data['countries']
    if 'production_site' in lot_row and lot_row['production_site'] is not None:
        production_site = lot_row['production_site'].strip()
        if production_site in my_production_sites:
            lot.production_site_is_in_carbure = True
            lot.carbure_production_site = my_production_sites[production_site]
            lot.unknown_production_site = ''
        else:
            # do not allow the use of an unknown production site if the producer is registered in Carbure
            print('producer is in carbure and production site is not in carbure. NOT ALLOWED')
            lot.production_site_is_in_carbure = False
            lot.carbure_production_site = None
            lot.unknown_production_site = production_site
    else:
        lot.production_site_is_in_carbure = False
        lot.carbure_production_site = None
        lot.unknown_production_site = ''
    if 'production_site_country' in lot_row:
        production_site_country = lot_row['production_site_country']
        if production_site_country is None or production_site_country == '':
            lot.unknown_production_country = None
        else:
            if production_site_country in countries:
                lot.unknown_production_country = countries[production_site_country]
            else:
                error = GenericError(tx=tx, field='production_site_country',
                                    error='WRONG_PRODUCTION_SITE_COUNTRY',
                                    extra='Champ production_site_country incorrect',
                                    display_to_creator=True, is_blocking=True,
                                    value=production_site_country)
                lot_errors.append(error)
    else:
        lot.unknown_production_country = None
    if 'production_site_reference' in lot_row:
        if lot.production_site_is_in_carbure:
            lot.carbure_production_site_reference = lot_row['production_site_reference']
        else:
            lot.unknown_production_site_reference = lot_row['production_site_reference']
    else:
        # try to find it automatically
        if lot.production_site_is_in_carbure:
            certificates = lot.carbure_production_site.productionsitecertificate_set.all()
            if certificates.count() > 0:
                lot.carbure_production_site_reference = certificates[0].natural_key()['certificate_id']
            else:
                lot.carbure_production_site_reference = 'NOT FOUND'
        else:
            lot.unknown_production_site_reference = ''
    if 'production_site_commissioning_date' in lot_row and lot_row['production_site_commissioning_date'] != '' and lot_row['production_site_commissioning_date'] is not None:
        try:
            com_date = try_get_date(lot_row['production_site_commissioning_date'])
            lot.unknown_production_site_com_date = com_date
        except Exception:
            msg = "Date de mise en service: veuillez entrer une date au format JJ/MM/AAAA"
            error = GenericError(tx=tx, field='production_site_commissioning_date',
                                error='PRODUCTION_SITE_COMDATE_FORMAT_INCORRECT',
                                display_to_creator=True, is_blocking=True,
                                extra=msg,
                                value=lot_row['production_site_commissioning_date'])
            lot_errors.append(error)
    else:
        lot.unknown_production_site_com_date = None
    if 'double_counting_registration' in lot_row:
        lot.unknown_production_site_dbl_counting = lot_row['double_counting_registration']
    else:
        lot.unknown_production_site_dbl_counting = ''
    return lot_errors


def fill_supplier_info(entity, lot_row, lot, prefetched_data):
    tx_errors = []
    if 'supplier' in lot_row:
        lot.unknown_supplier = lot_row['supplier']
    if 'supplier_certificate' in lot_row:
        lot.unknown_supplier_certificate = lot_row['supplier_certificate']
    return tx_errors


def fill_biocarburant_info(lot_row, lot, tx, prefetched_data):
    lot_errors = []
    biocarburants = prefetched_data['biocarburants']
    if 'biocarburant_code' in lot_row:
        biocarburant = lot_row['biocarburant_code']
        if biocarburant in biocarburants:
            lot.biocarburant = biocarburants[biocarburant]
        else:
            lot.biocarburant = None
            lot_errors.append(GenericError(tx=tx, field='biocarburant_code',
                                         error='UNKNOWN_BIOFUEL',
                                         extra='Biocarburant inconnu',
                                         display_to_creator=True, is_blocking=True,
                                         value=biocarburant))
    else:
        biocarburant = None
        lot.biocarburant = None
        lot_errors.append(GenericError(tx=tx, field='biocarburant_code',
                                     error='MISSING_BIOFUEL',
                                     extra='Merci de préciser le Biocarburant',
                                     display_to_creator=True, is_blocking=True,
                                     value=biocarburant))
    return lot_errors


def fill_matiere_premiere_info(lot_row, lot, tx, prefetched_data):
    lot_errors = []
    mps = prefetched_data['matieres_premieres']
    if 'matiere_premiere_code' in lot_row:
        matiere_premiere = lot_row['matiere_premiere_code']
        if matiere_premiere in mps:
            lot.matiere_premiere = mps[matiere_premiere]
        else:
            lot.matiere_premiere = None
            lot_errors.append(GenericError(tx=tx, field='matiere_premiere_code', error='UNKNOWN_FEEDSTOCK',
                                         extra='Matière Première inconnue', display_to_creator=True, is_blocking=True,
                                         value=matiere_premiere))
    else:
        lot.matiere_premiere = None
        lot_errors.append(GenericError(tx=tx, field='matiere_premiere_code', error='MISSING_FEEDSTOCK',
                                     extra='Merci de préciser la matière première',
                                     display_to_creator=True, is_blocking=True,
                                     value=None))
    return lot_errors


def fill_volume_info(lot_row, lot, tx):
    lot_errors = []
    if 'volume' in lot_row:
        volume = lot_row['volume']
        try:
            lot.volume = float(volume)
            lot.remaining_volume = lot.volume
            if lot.volume <= 0:
                lot_errors.append(GenericError(tx=tx, field='volume',
                                            display_to_creator=True, is_blocking=True,
                                            error='VOLUME_LTE_0',
                                            extra='Le volume doit être supérieur à 0', value=volume))
        except Exception:
            lot.volume = 0
            lot_errors.append(GenericError(tx=tx, field='volume',
                                           display_to_creator=True, is_blocking=True,
                                           error='VOLUME_FORMAT_INCORRECT',
                                           extra='Format du volume incorrect', value=volume))
    else:
        lot.volume = 0
        lot_errors.append(GenericError(tx=tx, field='volume',
                                     display_to_creator=True, is_blocking=True,
                                     error='MISSING_VOLUME',
                                     extra='Merci de préciser un volume', value=''))
    return lot_errors


def fill_pays_origine_info(lot_row, lot, tx, prefetched_data):
    lot_errors = []
    countries = prefetched_data['countries']
    if 'pays_origine_code' in lot_row:
        pays_origine = lot_row['pays_origine_code'].upper()
        if pays_origine in countries:
            lot.pays_origine = countries[pays_origine]
        else:
            lot.pays_origine = None
            lot_errors.append(GenericError(tx=tx, field='pays_origine_code', error='UNKNOWN_COUNTRY', extra='Pays inconnu',
                                         display_to_creator=True, is_blocking=True,
                                         value=pays_origine))
    else:
        lot.pays_origine = None
        lot_errors.append(GenericError(tx=tx, field='pays_origine_code', error='MISSING_COUNTRY', extra='Merci de préciser le pays',
                                       display_to_creator=True, is_blocking=True,
                                       value=''))
    return lot_errors


def fill_ghg_info(lot_row, lot, tx):
    lot_errors = []
    lot.eec = 0
    if 'eec' in lot_row and lot_row['eec'] is not None and lot_row['eec'] != '':
        eec = lot_row['eec']
        try:
            lot.eec = abs(float(eec))
        except Exception:
            lot_errors.append(GenericError(tx=tx, field='eec', error='WRONG_FORMAT', extra='Format non reconnu',
                                           display_to_creator=True, is_blocking=True, value=eec))

    lot.el = 0
    if 'el' in lot_row and lot_row['el'] is not None and lot_row['el'] != '':
        el = lot_row['el']
        try:
            lot.el = abs(float(el))
        except Exception:
             lot_errors.append(GenericError(tx=tx, field='el', error='WRONG_FORMAT', extra='Format non reconnu',
                                           display_to_creator=True, is_blocking=True, value=el))

    lot.ep = 0
    if 'ep' in lot_row and lot_row['ep'] is not None and lot_row['ep'] != '':
        ep = lot_row['ep']
        try:
            lot.ep = abs(float(ep))
        except Exception:
             lot_errors.append(GenericError(tx=tx, field='ep', error='WRONG_FORMAT', extra='Format non reconnu',
                                           display_to_creator=True, is_blocking=True, value=ep))

    lot.etd = 0
    if 'etd' in lot_row and lot_row['etd'] is not None and lot_row['etd'] != '':
        etd = lot_row['etd']
        try:
            lot.etd = abs(float(etd))
        except Exception:
             lot_errors.append(GenericError(tx=tx, field='etd', error='WRONG_FORMAT', extra='Format non reconnu',
                                           display_to_creator=True, is_blocking=True, value=etd))

    lot.eu = 0
    if 'eu' in lot_row and lot_row['eu'] is not None and lot_row['eu'] != '':
        eu = lot_row['eu']
        try:
            lot.eu = abs(float(eu))
        except Exception:
             lot_errors.append(GenericError(tx=tx, field='eu', error='WRONG_FORMAT', extra='Format non reconnu',
                                           display_to_creator=True, is_blocking=True, value=eu))

    lot.esca = 0
    if 'esca' in lot_row and lot_row['esca'] is not None and lot_row['esca'] != '':
        esca = lot_row['esca']
        try:
            lot.esca = abs(float(esca))
        except Exception:
             lot_errors.append(GenericError(tx=tx, field='esca', error='WRONG_FORMAT', extra='Format non reconnu',
                                           display_to_creator=True, is_blocking=True, value=esca))

    lot.eccs = 0
    if 'eccs' in lot_row and lot_row['eccs'] is not None and lot_row['eccs'] != '':
        eccs = lot_row['eccs']
        try:
            lot.eccs = abs(float(eccs))
        except Exception:
             lot_errors.append(GenericError(tx=tx, field='eccs', error='WRONG_FORMAT', extra='Format non reconnu',
                                           display_to_creator=True, is_blocking=True, value=eccs))

    lot.eccr = 0
    if 'eccr' in lot_row and lot_row['eccr'] is not None and lot_row['eccr'] != '':
        eccr = lot_row['eccr']
        try:
            lot.eccr = abs(float(eccr))
        except Exception:
             lot_errors.append(GenericError(tx=tx, field='eccr', error='WRONG_FORMAT', extra='Format non reconnu',
                                           display_to_creator=True, is_blocking=True, value=eccr))

    lot.eee = 0
    if 'eee' in lot_row and lot_row['eee'] is not None and lot_row['eee'] != '':
        eee = lot_row['eee']
        try:
            lot.eee = abs(float(eee))
        except Exception:
             lot_errors.append(GenericError(tx=tx, field='eee', error='WRONG_FORMAT', extra='Format non reconnu',
                                           display_to_creator=True, is_blocking=True, value=eee))
    # calculs ghg
    calculate_ghg(lot)
    return lot_errors


def fill_dae_data(lot_row, transaction):
    tx_errors = []
    transaction.dae = ''
    if 'dae' in lot_row:
        dae = lot_row['dae']
        if dae is not None:
            transaction.dae = dae
    if transaction.dae == '' and transaction.is_mac is False:
        tx_errors.append(GenericError(tx=transaction, field='dae', error="MISSING_DAE", extra="Merci de préciser le numéro de DAE/DAU", value=None, display_to_creator=True, is_blocking=True))
    return tx_errors


def try_get_date(dd):
    if isinstance(dd, int):
        return datetime.datetime.fromordinal(datetime.datetime(1900, 1, 1).toordinal() + dd - 2)
    if isinstance(dd, datetime.datetime):
        return dd.date()
    if isinstance(dd, datetime.date):
        return dd
    try:
        return datetime.datetime.strptime(dd, "%Y-%m-%d").date()
    except Exception:
        pass
    return dateutil.parser.parse(dd, dayfirst=True).date()


def fill_delivery_date(lot_row, lot, transaction):
    today = datetime.date.today()
    tx_errors = []
    if 'delivery_date' not in lot_row or lot_row['delivery_date'] == '' or lot_row['delivery_date'] is None:
        transaction.delivery_date = today
        lot.period = today.strftime('%Y-%m')
    else:
        try:
            dd = try_get_date(lot_row['delivery_date'])
            diff = today - dd
            if diff > datetime.timedelta(days=365):
                msg = "Date trop éloignée (%s)" % (lot_row['delivery_date'])
                tx_errors.append(GenericError(tx=transaction, field='delivery_date', error="INCORRECT_DELIVERY_DATE", extra=msg, value=lot_row['delivery_date'], display_to_creator=True, is_blocking=True))
                lot.period = today.strftime('%Y-%m')
                transaction.delivery_date = None
            else:
                transaction.delivery_date = dd
                lot.period = dd.strftime('%Y-%m')
        except Exception:
            transaction.delivery_date = today
            lot.period = today.strftime('%Y-%m')
            msg = "Format de date incorrect: veuillez entrer une date au format JJ/MM/AAAA (%s)" % (lot_row['delivery_date'])
            tx_errors.append(GenericError(tx=transaction, field='delivery_date', error="INCORRECT_FORMAT_DELIVERY_DATE", extra=msg, value=lot_row['delivery_date'], display_to_creator=True, is_blocking=True))
    return tx_errors


def fill_client_data(entity, lot_row, tx, prefetched_data):
    # if lot has already been validated and is currently in correction, we cannot change the client
    if tx.delivery_status == 'AC':
        return []

    if tx.is_mac:
        tx.client_is_in_carbure = False
        tx.carbure_client = None
        tx.unknown_client = ''
        if 'client' in lot_row:
            tx.unknown_client = lot_row['client']

    tx_errors = []
    clients = prefetched_data['clients']
    if entity.entity_type == 'Opérateur':
        tx.client_is_in_carbure = True
        tx.carbure_client = entity
        tx.unknown_client = ''
    elif 'client' in lot_row and lot_row['client'] is not None and lot_row['client'] != '':
        client = lot_row['client'].upper().strip()
        if client in clients:
            tx.client_is_in_carbure = True
            tx.carbure_client = clients[client]
            tx.unknown_client = ''
        else:
            tx.client_is_in_carbure = False
            tx.carbure_client = None
            tx.unknown_client = client
    else:
        tx.client_is_in_carbure = True
        tx.carbure_client = entity
        tx.unknown_client = ''
    return tx_errors


def fill_vendor_data(entity, lot_row, transaction, prefetched_data):
    tx_errors = []
    if entity.entity_type == Entity.OPERATOR:
        # the lot is added in db by an Operator. no certificate needed, no carbure_vendor
        return tx_errors

    # supplier is who we get the lot from
    # vendor is the one who adds the lot in the database
    if not transaction.carbure_vendor:
        transaction.carbure_vendor = entity

    # if the lot is added by a Producer or Trader, try to attach the trading certificate
    # first, use what is provided in the excel file
    if 'vendor_certificate' in lot_row and lot_row['vendor_certificate'] != '' and lot_row['vendor_certificate'] is not None:
        transaction.carbure_vendor_certificate = lot_row['vendor_certificate']
    else:
        # no certificate provided. get it from database
        if len(prefetched_data['my_vendor_certificates']) > 0:
            transaction.carbure_vendor_certificate = prefetched_data['my_vendor_certificates'][0]
        else:
            transaction.carbure_vendor_certificate = ''
    return tx_errors

def fill_delivery_site_data(lot_row, transaction, prefetched_data):
    tx_errors = []
    depots = prefetched_data['depots']
    countries = prefetched_data['countries']
    if 'delivery_site' in lot_row and lot_row['delivery_site'] is not None and lot_row['delivery_site'] != '':
        delivery_site = lot_row['delivery_site']
        if isinstance(delivery_site, float):
            # sometimes excel will convert a columns of integers to float
            delivery_site = int(delivery_site)
        # convert to string 4.0 -> 4 -> '4' and remove leading 0
        delivery_site = str(delivery_site)
        stripped_delivery_site = str(delivery_site).lstrip('0')
        if delivery_site in depots or stripped_delivery_site in depots:
            transaction.delivery_site_is_in_carbure = True
            if delivery_site in depots:
                transaction.carbure_delivery_site = depots[delivery_site]
            else:
                transaction.carbure_delivery_site = depots[stripped_delivery_site]
            transaction.unknown_delivery_site = ''
        else:
            transaction.delivery_site_is_in_carbure = False
            transaction.carbure_delivery_site = None
            transaction.unknown_delivery_site = delivery_site
    else:
        transaction.delivery_site_is_in_carbure = False
        transaction.carbure_delivery_site = None
        transaction.unknown_delivery_site = ''
        if not transaction.is_mac:
            tx_errors.append(GenericError(tx=transaction, field='delivery_site', value=None, error="MISSING_DELIVERY_SITE", extra="Merci de préciser un site de livraison", is_blocking=True, display_to_creator=True))
    if transaction.delivery_site_is_in_carbure is False and not transaction.is_mac:
        if 'delivery_site_country' in lot_row:
            country_code = lot_row['delivery_site_country']
            if country_code in countries:
                country = countries[country_code]
                transaction.unknown_delivery_site_country = country
            else:
                tx_errors.append(GenericError(tx=transaction, field='unknown_delivery_site_country',
                                                  error="INCORRECT_DELIVERY_SITE_COUNTRY",
                                                  extra='Champ delivery_site_country incorrect',
                                                  value=lot_row['delivery_site_country'],
                                                  is_blocking=True, display_to_creator=True))
        else:
            tx_errors.append(GenericError(tx=transaction, field='unknown_delivery_site_country',
                                              error="MISSING_UNKNOWN_DELIVERY_SITE_COUNTRY",
                                              extra='Merci de préciser une valeur dans le champ delivery_site_country',
                                              is_blocking=True, display_to_creator=True,
                                              value=None))
    return tx_errors

def load_mb_lot(prefetched_data, entity, user, lot_dict, source):
    errors = []

    # check for empty row
    if lot_dict.get('volume', None) is None:
        return None, None, "Missing volume"

    carbure_id = lot_dict.get('carbure_id', False)
    tx_id = lot_dict.get('tx_id', False)
    biocarburant = lot_dict.get('biocarburant_code', False)
    depot = lot_dict.get('depot', False)
    matiere_premiere = lot_dict.get('matiere_premiere_code', False)
    pays_origine = lot_dict.get('pays_origine_code', False)
    ghg_reduction = lot_dict.get('ghg_reduction', False)



    if tx_id:
        try:
            source_tx = LotTransaction.objects.get(carbure_client=entity, delivery_status='A', id=tx_id)
            source_lot = LotV2.objects.get(id=source_tx.lot.id)
        except Exception:
            return None, None, "TX not found"
    elif carbure_id:
        try:
            source_tx = LotTransaction.objects.get(carbure_client=entity, delivery_status='A', lot__carbure_id=carbure_id)
            source_lot = LotV2.objects.get(id=source_tx.lot.id)
        except Exception:
            return None, None, "TX not found"
    else:
        # try to find it via filters
        matching_txs = LotTransaction.objects.filter(carbure_client=entity, delivery_status='A')
        if biocarburant:
            try:
                bc = Biocarburant.objects.get(code=biocarburant)
            except:
                return None, None, "Unknown biocarburant"
            matching_txs = matching_txs.filter(lot__biocarburant=bc)
        if matiere_premiere:
            try:
                mp = MatierePremiere.objects.get(code=matiere_premiere)
            except:
                return None, None, "Unknown matiere premiere"
            matching_txs = matching_txs.filter(lot__matiere_premiere=mp)
        if ghg_reduction:
            matching_txs = matching_txs.filter(lot__ghg_reduction=ghg_reduction)
        if depot:
            matching_txs = matching_txs.filter(Q(carbure_delivery_site__depot_id=depot) | Q(unknown_delivery_site=depot))
        if pays_origine:
            matching_txs = matching_txs.filter(lot__pays_origine__code_pays=pays_origine)
        if matching_txs.count() == 1:
            source_tx = matching_txs[0]
            source_lot = LotV2.objects.get(id=source_tx.lot.id)
        else:
            nb_matches = matching_txs.count()
            return None, None, "Could not find mass balance line. %d matches" % (nb_matches)

    lot = source_tx.lot

    if source_tx.carbure_client == entity and source_tx.delivery_status == 'A' and lot.fused_with is None:
        # I am the client of this lot, I have accepted it and it's not fused with anything else
        # this lot is currently in my mass balance
        pass
    else:
        return None, None, "Cannot extract from this lot"

    # let's create a new lot and transaction
    lot.pk = None
    lot.parent_lot = source_lot
    lot.added_by = entity
    lot.data_origin_entity = lot.parent_lot.data_origin_entity
    lot.added_by_user = user
    lot.status = 'Draft'
    lot.carbure_id = ''
    lot.is_fused = False
    lot.is_split = True
    lot.source = 'EXCEL'

    transaction = LotTransaction()
    transaction.carbure_vendor = entity
    transaction.parent_tx = source_tx
    errors += fill_volume_info(lot_dict, lot, transaction)
    fill_mac_data(lot_dict, transaction) # does not return errors
    errors += fill_dae_data(lot_dict, transaction)
    errors += fill_delivery_date(lot_dict, lot, transaction)
    errors += fill_client_data(entity, lot_dict, transaction, prefetched_data)
    errors += fill_vendor_data(entity, lot_dict, transaction, prefetched_data)
    errors += fill_delivery_site_data(lot_dict, transaction, prefetched_data)

    transaction.ghg_total = lot.ghg_total
    transaction.ghg_reduction = lot.ghg_reduction
    transaction.champ_libre = lot_dict['champ_libre'] if 'champ_libre' in lot_dict else ''
    return lot, transaction, errors

def fill_mac_data(lot_dict, transaction):
    transaction.is_mac = False
    if 'mac' in lot_dict:
        if lot_dict['mac'] == 1 or lot_dict['mac'] == 'true':
            transaction.is_mac = True

def load_lot(prefetched_data, entity, user, lot_dict, source, tx=None):
    errors = []

    # check for empty row
    biocarburant_code = lot_dict.get('biocarburant_code', None)
    if biocarburant_code is None or biocarburant_code == '':
        return None, None, "Missing biocarburant_code"
    
    can_update_tx = False
    if tx is None:
        can_update_tx = True
        lot = LotV2()
        lot.added_by = entity
        lot.data_origin_entity = entity
        lot.added_by_user = user
        lot.source = source
        tx = LotTransaction()
    else:
        lot = tx.lot

    lot.is_valid = False # I don't think we need this. validity is checked everytime we re-submit transactions

    # do not allow to modify production data for stock-lots
    if lot.parent_lot == None:
        errors += fill_producer_info(entity, lot_dict, lot, prefetched_data)
        errors += fill_production_site_info(entity, lot_dict, lot, tx, prefetched_data)
        errors += fill_supplier_info(entity, lot_dict, lot, prefetched_data)
        errors += fill_biocarburant_info(lot_dict, lot, tx, prefetched_data)
        errors += fill_matiere_premiere_info(lot_dict, lot, tx, prefetched_data)
        errors += fill_pays_origine_info(lot_dict, lot, tx, prefetched_data)
        errors += fill_ghg_info(lot_dict, lot, tx)
        errors += fill_volume_info(lot_dict, lot, tx)
    else:
        # STOCK// if someone updates the volume of a validated split-lot
        # STOCK// we first recredit the volume back in stock
        if lot.status == LotV2.VALIDATED and lot.is_split:
            lot.parent_lot.remaining_volume += lot.volume
            lot.parent_lot.save()
        # STOCK// only the lot.added_by can update the volume of a split transaction
        if lot.added_by == entity and lot.is_split:
            errors += fill_volume_info(lot_dict, lot, tx)
        # STOCK// and debit the stock back according to new volume 
        if lot.status == LotV2.VALIDATED and lot.is_split:
            lot.parent_lot.remaining_volume -= lot.volume
            lot.parent_lot.save()

    # data related to TRANSACTION

    if tx.carbure_vendor and tx.carbure_vendor == entity:
        # I am the seller
        can_update_tx = True
    if not tx.carbure_vendor and tx.carbure_client and tx.carbure_client == entity:
        # lot added by client, he's allowed to update
        can_update_tx = True
    if can_update_tx:
        fill_mac_data(lot_dict, tx) # does not return anything
        errors += fill_dae_data(lot_dict, tx)
        errors += fill_delivery_date(lot_dict, lot, tx)
        errors += fill_client_data(entity, lot_dict, tx, prefetched_data)
        errors += fill_vendor_data(entity, lot_dict, tx, prefetched_data)
        errors += fill_delivery_site_data(lot_dict, tx, prefetched_data)
        tx.ghg_total = lot.ghg_total
        tx.ghg_reduction = lot.ghg_reduction
        tx.champ_libre = lot_dict['champ_libre'] if 'champ_libre' in lot_dict else ''

    return lot, tx, errors


def load_excel_file(entity, user, file, mass_balance=False):
    #print('File received %s' % (datetime.datetime.now()))
    errors = []
    # prefetch some data
    prefetched_data = get_prefetched_data(entity)

    try:
        wb = openpyxl.load_workbook(file, data_only=True)
        sheet = wb.worksheets[0]
        data = get_sheet_data(sheet, convert_float=True)
        column_names = data[0]
        data = data[1:]
        df = pd.DataFrame(data, columns=column_names)
        df.fillna('', inplace=True)
        total_lots = len(df)
        lots_loaded = 0
        lots_to_insert = []
        txs_to_insert = []
        generic_errors = []
        print('File read %s' % (datetime.datetime.now()))
        for row in df.iterrows():
            lot_row = row[1]
            try:
                if mass_balance:
                    lot, tx, errors = load_mb_lot(prefetched_data, entity, user, lot_row, 'EXCEL')
                else:
                    lot, tx, errors = load_lot(prefetched_data, entity, user, lot_row, 'EXCEL')
                if lot is None:
                    # could not load line. missing column biocaburant_code?
                    #print(lot_row)
                    print(errors)
                    continue
                lots_loaded += 1
                lots_to_insert.append(lot)
                txs_to_insert.append(tx)
                generic_errors.append(errors)
            except Exception:
                traceback.print_exc()
        print('File processed %s' % (datetime.datetime.now()))
        bulk_insert(entity, lots_to_insert, txs_to_insert, generic_errors, prefetched_data)
        print('%d Lots out of %d lines loaded in database %s' % (lots_loaded, total_lots, datetime.datetime.now()))
        return lots_loaded, total_lots, errors
    except Exception:
        return False, False, errors


def bulk_insert(entity, lots_to_insert, txs_to_insert, generic_errors, prefetched_data):
    # print('Starting bulk_insert %s' % (datetime.datetime.now()))
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
    # likewise, GenericError requires a foreign key
    # 6 assign tx.id to GenericError
    new_txs = [t for t in LotTransaction.objects.filter(lot__added_by=entity).order_by('-id')[0:len(lots_to_insert)]]
    for tx, errors in zip(sorted(new_txs, key=lambda x: x.id), generic_errors):
        for e in errors:
            e.tx_id = tx.id
    flat_generic_errors = [item for sublist in generic_errors for item in sublist]
    GenericError.objects.bulk_create(flat_generic_errors, batch_size=100)
    bulk_sanity_checks(new_txs, prefetched_data, background=False)
    return new_lots, new_txs


def validate_lots(user, entity, txs):
    valid = 0
    invalid = 0
    submitted = txs.count()
    errors = []
    to_validate = []
    for tx in txs:
        if tx.lot.status != 'Draft':
            # lot is not a draft: must be a request for correction
            if tx.delivery_status not in ['AA', 'AC', 'R']:
                # tx already validated and not pending correction. reject
                invalid += 1
                errors.append({'tx_id': tx.id, 'message': "Transaction already validated"})
                continue
        to_validate.append(tx)

    prefetched_data = get_prefetched_data(entity)
    # run sanity_checks
    results = bulk_sanity_checks(to_validate, prefetched_data, background=False)

    # disable autocommit
    with transaction.atomic():
        for sanity_result, tx in zip(results, to_validate):
            lot_valid, tx_valid, is_sane = sanity_result
            print('tx %d valid %s lot valid %s is_sane %s' % (tx.id, tx_valid, lot_valid, is_sane))

            if not is_sane or not lot_valid or not tx_valid:
                invalid += 1
                errors.append({'tx_id': tx.id, 'message': "Could not validate tx/lot/sanity %s/%s/%s" % (tx_valid, lot_valid, is_sane)})
                tx.lot.is_valid = False
            else:
                valid += 1
                tx.lot.is_valid = True
                tx.lot.carbure_id = generate_carbure_id(tx.lot)
                tx.lot.status = "Validated"
                previous_status = tx.delivery_status

                # if we create a lot for ourselves
                if tx.carbure_client and tx.lot.added_by == tx.carbure_client:
                    tx.delivery_status = LotTransaction.ACCEPTED
                # if the client is not in carbure, auto-accept
                elif not tx.client_is_in_carbure:
                    tx.delivery_status = LotTransaction.ACCEPTED
                # if we save a lot that was requiring a fix, change status to 'AA'
                elif tx.delivery_status in [LotTransaction.TOFIX, LotTransaction.REJECTED]:
                    tx.delivery_status = LotTransaction.FIXED
                else:
                    pass
                TransactionUpdateHistory.objects.create(tx=tx, update_type=TransactionUpdateHistory.UPDATE, field='status', value_before=previous_status, value_after=tx.delivery_status, modified_by=user, modified_by_entity=entity)
                # is this a Stock tx?
                if tx.carbure_client and tx.carbure_client.entity_type in [Entity.PRODUCER, Entity.TRADER]:
                    tx.is_stock = True
            tx.save()
            tx.lot.save()
    return {'submitted': submitted, 'valid': valid, 'invalid': invalid, 'errors': errors}



def send_rejection_emails(rejected_txs):
    # group by vendors
    reject_by_vendors = {}
    for tx in rejected_txs:
        if tx.carbure_vendor not in reject_by_vendors:
            reject_by_vendors[tx.carbure_vendor] = []
        reject_by_vendors[tx.carbure_vendor].append(tx)

    for vendor, txs in reject_by_vendors.items():
        send_reject_email(vendor, txs)


def notify_accepted_lot_change(tx):
    recipients = [ur.user.email for ur in UserRights.objects.filter(entity=tx.carbure_vendor, user__is_staff=False)]
    cc = []
    if tx.carbure_client:
        cc += [ur.user.email for ur in UserRights.objects.filter(entity=tx.carbure_client, user__is_staff=False)]

    if tx.delivery_status == LotTransaction.FROZEN:
        # add administration in copy
        cc += 'carbure@beta.gouv.fr'

    send_accepted_lot_in_correction_email(tx, recipients, cc)


def invalidate_declaration(tx, entity):
    year, month = tx.lot.period.split('-')
    period = datetime.date(year=year, month=int(month), day=1)
    try:
        sd = SustainabilityDeclaration.objects.filter(entity=entity, period=period)
        sd.declared = False
        sd.checked = False
        sd.save()
    except:
        # declaration doesn't exist ?
        pass