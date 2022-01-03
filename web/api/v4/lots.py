import datetime
import unicodedata
import dateutil
from typing import Generic, List
from django.db.models.query import QuerySet
from numpy.lib.function_base import insert
from api.v4.sanity_checks import bulk_sanity_checks
from core.models import CarbureLot, CarbureLotEvent, CarbureStock, Entity, GenericError, LotTransaction

INCORRECT_DELIVERY_DATE = "INCORRECT_DELIVERY_DATE"
INCORRECT_FORMAT_DELIVERY_DATE = "INCORRECT_FORMAT_DELIVERY_DATE"
COULD_NOT_FIND_PRODUCTION_SITE = "COULD_NOT_FIND_PRODUCTION_SITE"
MISSING_BIOFUEL = "MISSING_BIOFUEL"
MISSING_FEEDSTOCK = "MISSING_FEEDSTOCK"
MISSING_COUNTRY_OF_ORIGIN = "MISSING_COUNTRY_OF_ORIGIN"
UNKNOWN_BIOFUEL = "UNKNOWN_BIOFUEL"
UNKNOWN_FEEDSTOCK = "UNKNOWN_FEEDSTOCK"
UNKNOWN_COUNTRY_OF_ORIGIN = "UNKNOWN_COUNTRY_OF_ORIGIN"
MISSING_VOLUME = "MISSING_VOLUME"
VOLUME_FORMAT_INCORRECT = "VOLUME_FORMAT_INCORRECT"
WRONG_FLOAT_FORMAT = "WRONG_FLOAT_FORMAT"
UNKNOWN_DELIVERY_SITE = "UNKNOWN_DELIVERY_SITE"
UNKNOWN_DELIVERY_COUNTRY = "UNKNOWN_DELIVERY_COUNTRY"
UNKNOWN_CLIENT = "UNKNOWN_CLIENT"

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

def fill_delivery_date(lot, data):
    errors = []
    today = datetime.date.today()
    # default: today
    lot.delivery_date = today
    try:
        delivery_date = data['delivery_date']
        dd = try_get_date(delivery_date)
        diff = today - dd
        if diff > datetime.timedelta(days=365):
            errors.append(GenericError(lot=lot, field='delivery_date', error=INCORRECT_DELIVERY_DATE, value=delivery_date, display_to_creator=True, is_blocking=True))
        else:
            lot.delivery_date = dd
    except Exception:
        errors.append(GenericError(lot=lot, field='delivery_date', error=INCORRECT_FORMAT_DELIVERY_DATE, value=delivery_date, display_to_creator=True, is_blocking=True))
    lot.period = lot.delivery_date.year * 100 + lot.delivery_date.month
    lot.year = lot.delivery_date.year
    return errors


def fill_production_info(lot, data, entity, prefetched_data):
    errors = []
    # possibilities:
    # Case 1: I have a parent_lot or parent_stock -> copy production info
    # Case 2: I am a producer and this is my own production (unknown_producer is None) -> I am the producer, ensure production_site is known
    # Case 3: all other cases (unknown producer / unknown production site) -> fill unknown_producer and unknown_production_site

    # CASE 1
    if lot.parent_lot or lot.parent_stock:
        # EXISTING PRODUCTION DATA FROM PARENT
        if lot.parent_stock:
            parent_lot = lot.parent_stock.get_parent_lot()
        else:
            parent_lot = lot.parent_lot
        lot.copy_production_details(parent_lot)
    else:
        # NEW LOT
        lot.production_site_certificate = data.get('production_site_certificate', None)
        lot.production_site_certificate_type = data.get('production_site_certificate_type', None)
        unknown_producer = data.get('unknown_producer', None)
        # CASE 2
        if unknown_producer is None and entity.entity_type == Entity.PRODUCER:
            lot.carbure_producer = entity
            lot.unknown_producer = None
            carbure_production_site = data.get('carbure_production_site', '').upper()
            if carbure_production_site in prefetched_data['my_production_sites']:
                lot.carbure_production_site = prefetched_data['my_production_sites'][carbure_production_site]
            else:
                lot.carbure_production_site = None
                errors.append(GenericError(lot=lot, field='carbure_production_site', error=COULD_NOT_FIND_PRODUCTION_SITE, value=carbure_production_site, display_to_creator=True, is_blocking=True))
            lot.unknown_production_site = None
            lot.production_country = lot.carbure_production_site.country if lot.carbure_production_site else None
            lot.production_site_commissioning_date = lot.carbure_production_site.date_mise_en_service if lot.carbure_production_site else None
            lot.production_site_double_counting_certificate = lot.carbure_production_site.dc_reference if lot.carbure_production_site else None
        # CASE 3
        else:
            lot.carbure_producer = None
            lot.unknown_producer = data.get('unknown_producer', None)
            lot.carbure_production_site = None
            lot.unknown_production_site = data.get('unknown_production_site', None)
            pcc = data.get('production_country_code', None)
            if pcc not in prefetched_data['countries']:
                lot.production_country = None
            else:
                lot.production_country = prefetched_data['countries'][pcc]
            lot.production_site_commissioning_date = try_get_date(data.get('production_site_commissioning_date', None))
            lot.production_site_double_counting_certificate = data.get('production_site_double_counting_certificate', None)
    return errors

def fill_basic_info(lot, data, prefetched_data):
    errors = []
    if lot.parent_lot or lot.parent_stock:
        # EXISTING DATA FROM PARENT
        if lot.parent_stock:
            parent_lot = lot.parent_stock.get_parent_lot()
        else:
            parent_lot = lot.parent_lot
        lot.copy_basic_info(parent_lot)
    else:
        ### BIOFUEL
        biofuels = prefetched_data['biofuels']
        biofuel_code = data.get('biofuel_code', None)
        lot.biofuel = None
        if not biofuel_code:
            errors.append(GenericError(lot=lot, field='biofuel_code', error=MISSING_BIOFUEL, display_to_creator=True, is_blocking=True))
        else:
            if biofuel_code not in biofuels:
                errors.append(GenericError(lot=lot, field='biofuel_code', error=UNKNOWN_BIOFUEL, display_to_creator=True, is_blocking=True))
            else:
                # all good
                lot.biofuel = biofuels[biofuel_code]
        ### FEEDSTOCK
        feedstocks = prefetched_data['feedstocks']
        feedstock_code = data.get('feedstock_code', None)
        lot.feedstock = None
        if not feedstock_code:
            errors.append(GenericError(lot=lot, field='feedstock_code', error=MISSING_FEEDSTOCK, display_to_creator=True, is_blocking=True))
        else:
            if feedstock_code not in feedstocks:
                errors.append(GenericError(lot=lot, field='feedstock_code', error=UNKNOWN_FEEDSTOCK, display_to_creator=True, is_blocking=True))
            else:
                # all good
                lot.feedstock = feedstocks[feedstock_code]
        ### COUNTRY OF ORIGIN
        countries = prefetched_data['countries']
        country_code = data.get('country_code', None)
        lot.country_of_origin = None
        if not country_code:
            errors.append(GenericError(lot=lot, field='country_code', error=MISSING_COUNTRY_OF_ORIGIN, display_to_creator=True, is_blocking=True))
        else:
            if country_code not in countries:
                errors.append(GenericError(lot=lot, field='country_code', error=UNKNOWN_COUNTRY_OF_ORIGIN, display_to_creator=True, is_blocking=True))
            else:
                # all good
                lot.country_of_origin = countries[country_code]
    ### VOLUME
    if lot.parent_lot is None:
        volume = data.get('volume', None)
        if not volume:
            errors.append(GenericError(lot=lot, field='volume', error=MISSING_VOLUME, display_to_creator=True, is_blocking=True))
        else:
            try:
                volume = round(abs(float(volume)), 2)
                if lot.volume != 0 and volume != lot.volume:
                    if lot.parent_stock is not None:
                        # we are updating the volume of a lot from stock
                        lot.parent_stock.update_remaining_volume(lot.volume, volume)
                    else:
                        lot.volume = volume
                else:
                    # initial volume setting or override
                    lot.volume = volume
            except Exception:
                lot.volume = 0
                errors.append(GenericError(lot=lot, field='volume', error=VOLUME_FORMAT_INCORRECT, display_to_creator=True, is_blocking=True))
        lot.weight = lot.get_weight()
        lot.lhv_amount = lot.get_lhv_amount()
    return errors

def fill_supplier_info(lot, data, entity):
    errors = []
    # I am a producer, this is my own production
    if lot.carbure_producer and lot.carbure_producer.id == entity.id:
        lot.carbure_supplier = entity
        lot.unknown_supplier = None
    elif data.get('carbure_supplier_id') == str(entity.id):
        lot.carbure_supplier = entity
        lot.unknown_supplier = None
    else:
        lot.carbure_supplier = None
        lot.unknown_supplier = data.get('unknown_supplier', None)
    lot.supplier_certificate = data.get('supplier_certificate', None)
    lot.supplier_certificate_type = data.get('supplier_certificate_type', None)
    if lot.supplier_certificate is None:
        lot.supplier_certificate = entity.default_certificate
    return errors

def fill_ghg_info(lot, data):
    errors = []
    try:
        lot.eec = abs(float(data.get('eec', 0)))
    except:
        errors.append(GenericError(lot=lot, field='eec', error=WRONG_FLOAT_FORMAT, display_to_creator=True))
    try:
        lot.el = float(data.get('el', 0))
    except:
        errors.append(GenericError(lot=lot, field='el', error=WRONG_FLOAT_FORMAT, display_to_creator=True))
    try:
        lot.ep = abs(float(data.get('ep', 0)))
    except:
        errors.append(GenericError(lot=lot, field='ep', error=WRONG_FLOAT_FORMAT, display_to_creator=True))
    try:
        lot.etd = abs(float(data.get('etd', 0)))
    except:
        errors.append(GenericError(lot=lot, field='etd', error=WRONG_FLOAT_FORMAT, display_to_creator=True))
    try:
        lot.eu = abs(float(data.get('eu', 0)))
    except:
        errors.append(GenericError(lot=lot, field='eu', error=WRONG_FLOAT_FORMAT, display_to_creator=True))
    try:
        lot.esca = abs(float(data.get('esca', 0)))
    except:
        errors.append(GenericError(lot=lot, field='esca', error=WRONG_FLOAT_FORMAT, display_to_creator=True))
    try:
        lot.eccs = abs(float(data.get('eccs', 0)))
    except:
        errors.append(GenericError(lot=lot, field='eccs', error=WRONG_FLOAT_FORMAT, display_to_creator=True))
    try:
        lot.eccr = abs(float(data.get('eccr', 0)))
    except:
        errors.append(GenericError(lot=lot, field='eccr', error=WRONG_FLOAT_FORMAT, display_to_creator=True))
    try:
        lot.eee = abs(float(data.get('eee', 0)))
    except:
        errors.append(GenericError(lot=lot, field='eee', error=WRONG_FLOAT_FORMAT, display_to_creator=True))
    lot.update_ghg()
    return errors

def fill_delivery_data(lot, data, entity, prefetched_data):
    errors = []
    lot.transport_document_type = data.get('transport_document_type', None)
    if lot.transport_document_type is None:
        lot.transport_document_type = CarbureLot.DAE
    lot.transport_document_reference = data.get('transport_document_reference', None)
    delivery_type = data.get('delivery_type', None)
    if delivery_type is None:
        lot.delivery_type = CarbureLot.OTHER
    else:
        lot.delivery_type = data.get('delivery_type', None)
    dest = data.get('carbure_delivery_site_depot_id', None)
    if dest in prefetched_data['depots']:
        lot.carbure_delivery_site = prefetched_data['depots'][dest]
        lot.delivery_site_country = lot.carbure_delivery_site.country
    else:
        lot.carbure_delivery_site = None
        errors.append(GenericError(lot=lot, field='carbure_delivery_site_depot_id', error=UNKNOWN_DELIVERY_SITE, display_to_creator=True, is_blocking=True))

    if not lot.carbure_delivery_site:
        lot.unknown_delivery_site = data.get('unknown_delivery_site', None)
        delivery_country_code = data.get('delivery_site_country_code', None)
        if delivery_country_code in prefetched_data['countries']:
            lot.delivery_site_country = prefetched_data['countries'][delivery_country_code]
    return errors


def fill_client_data(lot, data, entity, prefetched_data):
    errors = []
    carbure_client_id = data.get('carbure_client_id', None)
    try:
        carbure_client_id = int(carbure_client_id)
        if carbure_client_id in prefetched_data['clients']:
            lot.carbure_client = prefetched_data['clients'][carbure_client_id]
        else:
            lot.carbure_client = None
            if lot.delivery_type in [CarbureLot.PROCESSING, CarbureLot.TRADING, CarbureLot.STOCK, CarbureLot.BLENDING]:
                errors.append(GenericError(lot=lot, field='carbure_client_id', error=UNKNOWN_CLIENT, display_to_creator=True, is_blocking=True))
            else:
                errors.append(GenericError(lot=lot, field='carbure_client_id', error=UNKNOWN_CLIENT, display_to_creator=True))
    except:
        lot.carbure_client = None
    lot.unknown_client = data.get('unknown_client', None)
    return errors

def construct_carbure_lot(prefetched_data, entity, data, existing_lot=None):
    errors = []

    if existing_lot:
        lot = existing_lot
    else:
        lot = CarbureLot()
    errors += fill_delivery_date(lot, data)
    errors += fill_production_info(lot, data, entity, prefetched_data)
    errors += fill_basic_info(lot, data, prefetched_data)
    errors += fill_supplier_info(lot, data, entity)
    errors += fill_ghg_info(lot, data)
    errors += fill_delivery_data(lot, data, entity, prefetched_data)
    errors += fill_client_data(lot, data, entity, prefetched_data)
    lot.free_field = data.get('free_field', None)
    lot.added_by = entity

    if 'parent_stock_id' in data:
        try:
            parent_stock = CarbureStock.objects.get(id=data['parent_stock_id'])
            assert(parent_stock.carbure_client == entity)
        except:
            return False
        fill_production_info_from_stock(lot, parent_stock)
        lot.parent_stock = parent_stock
        lot.carbure_dispatch_site = parent_stock.depot
        lot.carbure_supplier = parent_stock.carbure_client
        lot.feedstock = parent_stock.feedstock
        lot.biofuel = parent_stock.biofuel
        lot.country_of_origin = parent_stock.country_of_origin
        fill_ghg_values_from_stock(lot, parent_stock)
        remaining_volume = models.FloatField(default=0.0)
        remaining_weight = models.FloatField(default=0.0)
        remaining_lhv_amount = models.FloatField(default=0.0)
        ghg_reduction = models.FloatField(default=0.0)
        ghg_reduction_red_ii = models.FloatField(default=0.0)

    return lot, errors

def bulk_insert_lots(entity: Entity, lots: List[CarbureLot], errors: List[GenericError], prefetched_data: dict) -> QuerySet:
    CarbureLot.objects.bulk_create(lots, batch_size=100)
    inserted_lots = CarbureLot.objects.filter(added_by=entity).order_by('-id')[0:len(lots)]
    for lot, errors in zip(inserted_lots, errors):
        for e in errors:
            e.lot_id = lot.id
    bulk_sanity_checks(inserted_lots, prefetched_data, background=False)
    GenericError.objects.bulk_create(errors, batch_size=100)
    return inserted_lots
