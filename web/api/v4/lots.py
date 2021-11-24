import datetime
import dateutil
from core.models import CarbureLot, CarbureStock, Entity, GenericError, LotTransaction

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
        dd = try_get_date(data['delivery_date'])
        diff = today - dd
        if diff > datetime.timedelta(days=365):
            errors.append(GenericError(lot=lot, field='delivery_date', error=INCORRECT_DELIVERY_DATE, value=data['delivery_date'], display_to_creator=True, is_blocking=True))
        else:
            lot.delivery_date = dd
    except Exception:
        errors.append(GenericError(lot=lot, field='delivery_date', error=INCORRECT_FORMAT_DELIVERY_DATE, value=data['delivery_date'], display_to_creator=True, is_blocking=True))
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
            try:
                carbure_production_site_id = int(data.get('carbure_production_site_id', None))
                lot.carbure_production_site = prefetched_data['my_production_sites'][carbure_production_site_id]
                lot.unknown_production_site = None
                lot.production_country = lot.carbure_production_site.country
                lot.production_site_commissioning_date = lot.carbure_production_site.date_mise_en_service
                lot.production_site_double_counting_certificate = lot.carbure_production_site.dc_reference
            except:
                # integer cast fail or key missing
                errors.append(GenericError(lot=lot, field='carbure_production_site_id', error=COULD_NOT_FIND_PRODUCTION_SITE, value=carbure_production_site_id, display_to_creator=True, is_blocking=True))
        # CASE 3
        else:
            lot.carbure_producer = None
            lot.unknown_producer = data.get('unknown_producer', None)
            lot.carbure_production_site = None
            lot.unknown_production_site = data.get('unknown_production_site', None)
            lot.production_country_id = data.get('production_country_id', None)
            lot.production_site_commissioning_date = data.get('production_site_commissioning_date', None)
            lot.production_site_double_counting_certificate = data.get('production_site_double_counting_certificate', None)
    return errors

def fill_basic_info(lot, data, prefetched_data):
    errors = []
    ### BIOFUEL
    biofuels = prefetched_data['biocarburants']
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
    volume = data.get('volume', None)
    if not volume:
        errors.append(GenericError(lot=lot, field='volume', error=MISSING_VOLUME, display_to_creator=True, is_blocking=True))
    else:
        try:
            lot.volume = abs(float(volume))
        except Exception:
            lot.volume = 0
            errors.append(GenericError(lot=lot, field='volume', error=VOLUME_FORMAT_INCORRECT, display_to_creator=True, is_blocking=True))
    lot.weight = lot.get_weight()
    lot.lhv_amount = lot.get_lhv_amount()
    return errors

def fill_supplier_info(lot, data, entity):
    # I am a producer, this is my own production
    if lot.carbure_producer == entity:
        lot.carbure_supplier = entity
        lot.unknown_supplier = None
    else:
        lot.carbure_supplier = None
        lot.unknown_supplier = data.get('unknown_supplier', None)
    lot.supplier_certificate = data.get('supplier_certificate', None)
    lot.supplier_certificate_type = data.get('supplier_certificate_type', None)

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

def fill_delivery_data(lot, data, entity, prefetched_data):
    errors = []
    lot.transport_document_type = data.get('transport_document_type', None)
    lot.transport_document_reference = data.get('transport_document_type', None)
    lot.delivery_type = data.get('delivery_type', None)
    lot.carbure_delivery_site_id = data.get('carbure_delivery_site_id', None)
    if lot.carbure_delivery_site_id not in prefetched_data['depots']:
        errors.append(GenericError(lot=lot, field='carbure_client_id', error=UNKNOWN_DELIVERY_SITE, display_to_creator=True, is_blocking=True))
        lot.carbure_delivery_site_id = None
    lot.unknown_delivery_site = data.get('unknown_delivery_site', None)
    lot.delivery_site_country_id = data.get('delivery_site_country_id', None)
    if lot.delivery_site_country_id not in prefetched_data['countries']:
        errors.append(GenericError(lot=lot, field='country_code', error=UNKNOWN_DELIVERY_COUNTRY, display_to_creator=True, is_blocking=True))
    return errors


def fill_client_data(lot, data, entity, prefetched_data):
    errors = []
    lot.carbure_client_id = data.get('carbure_client_id', None)
    if lot.carbure_client_id not in prefetched_data['clients']:
        lot.carbure_client_id = None
        if lot.delivery_type in [CarbureLot.PROCESSING, CarbureLot.TRADING, CarbureLot.STOCK, CarbureLot.BLENDING]:
            errors.append(GenericError(lot=lot, field='carbure_client_id', error=UNKNOWN_CLIENT, display_to_creator=True, is_blocking=True))
        else:
            errors.append(GenericError(lot=lot, field='carbure_client_id', error=UNKNOWN_CLIENT, display_to_creator=True))
    lot.unknown_client = data.get('unknown_client', None)
    return errors

def construct_carbure_lot(prefetched_data, entity, data):
    errors = []

    lot = CarbureLot()
    errors += fill_delivery_date(lot, data)
    errors += fill_production_info(lot, data, entity, prefetched_data)
    errors += fill_basic_info(lot, data, prefetched_data)
    errors += fill_supplier_info(lot, data, entity, prefetched_data)
    errors += fill_ghg_info(lot, data)
    errors += fill_delivery_data(lot, data, entity, prefetched_data)
    errors += fill_client_data()
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

def bulk_insert_lots(entity, lots, errors, prefetched_data):
    pass
