import datetime
import traceback
import dateutil
from typing import List
from django.db.models.query import QuerySet
from core.carburetypes import CarbureUnit, CarbureStockErrors
from core.models import CarbureLot, CarbureStock, Entity, GenericError
from certificates.models import DoubleCountingRegistration
from api.v4.sanity_checks import bulk_sanity_checks

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
UNKNOWN_UNIT = "UNKNOWN_UNIT"
VOLUME_FORMAT_INCORRECT = "VOLUME_FORMAT_INCORRECT"
WRONG_FLOAT_FORMAT = "WRONG_FLOAT_FORMAT"
UNKNOWN_DELIVERY_SITE = "UNKNOWN_DELIVERY_SITE"
UNKNOWN_DELIVERY_COUNTRY = "UNKNOWN_DELIVERY_COUNTRY"
UNKNOWN_CLIENT = "UNKNOWN_CLIENT"


def try_get_date(dd):
    if isinstance(dd, str):
        dd = dd.strip()
    if dd == "":
        return None
    if dd is None:
        return dd
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
    try:
        return datetime.datetime.strptime(dd, "%d/%m/%Y").date()
    except Exception:
        pass
    try:
        return datetime.datetime.strptime(dd, "%d/%m/%y").date()
    except Exception:
        pass
    return dateutil.parser.parse(dd, dayfirst=True).date()


def fill_delivery_date(lot, data):
    errors = []
    today = datetime.date.today()
    # default: today
    lot.delivery_date = today
    try:
        delivery_date = data.get("delivery_date", "")
        dd = try_get_date(delivery_date)
        lot.delivery_date = dd
    except Exception:
        errors.append(
            GenericError(
                lot=lot,
                field="delivery_date",
                error=INCORRECT_FORMAT_DELIVERY_DATE,
                value=delivery_date,
                display_to_creator=True,
                is_blocking=True,
            )
        )
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
        lot.production_site_certificate = data.get("production_site_certificate", None)
        lot.production_site_certificate_type = data.get("production_site_certificate_type", None)
        carbure_production_site = data.get("carbure_production_site", "").upper()
        # CASE 2
        if carbure_production_site and entity.entity_type == Entity.PRODUCER:
            lot.carbure_producer = entity
            lot.unknown_producer = None
            if carbure_production_site in prefetched_data["my_production_sites"]:
                lot.carbure_production_site = prefetched_data["my_production_sites"][carbure_production_site]
            else:
                lot.carbure_production_site = None
                errors.append(
                    GenericError(
                        lot=lot,
                        field="carbure_production_site",
                        error=COULD_NOT_FIND_PRODUCTION_SITE,
                        value=carbure_production_site,
                        display_to_creator=True,
                        is_blocking=True,
                    )
                )
            lot.unknown_production_site = None
            lot.production_country = lot.carbure_production_site.country if lot.carbure_production_site else None
            lot.production_site_commissioning_date = (
                lot.carbure_production_site.date_mise_en_service if lot.carbure_production_site else None
            )

            # si il y a un certificat DC renseigné, on recupere et verifie la validité des certificats associés à ce site de production
            if lot.carbure_production_site.dc_reference:
                delivery_date = data.get("delivery_date")
                try:
                    pd_certificates = DoubleCountingRegistration.objects.filter(
                        production_site_id=lot.carbure_production_site.id,
                        valid_from__lt=delivery_date,
                        valid_until__gte=delivery_date,
                    )
                    current_certificate = pd_certificates.first()
                    if current_certificate:
                        lot.production_site_double_counting_certificate = current_certificate.certificate_id
                    else:  # le certificat renseigné sur le site de production est mis par defaut
                        lot.production_site_double_counting_certificate = lot.carbure_production_site.dc_reference
                except:
                    lot.production_site_double_counting_certificate = lot.carbure_production_site.dc_reference
            else:
                lot.production_site_double_counting_certificate = None

        # CASE 3
        else:
            lot.carbure_producer = None
            lot.unknown_producer = data.get("unknown_producer", None)
            lot.carbure_production_site = None
            lot.unknown_production_site = data.get("unknown_production_site", None)
            pcc = data.get("production_country_code", None)
            if pcc not in prefetched_data["countries"]:
                lot.production_country = None
            else:
                lot.production_country = prefetched_data["countries"][pcc]
            lot.production_site_commissioning_date = try_get_date(data.get("production_site_commissioning_date", None))
            lot.production_site_double_counting_certificate = data.get(
                "production_site_double_counting_certificate", None
            )
    return errors


def fill_basic_info(lot, data, prefetched_data):
    errors = []
    if lot.parent_lot or lot.parent_stock:
        # EXISTING DATA FROM PARENT
        if lot.parent_stock:
            parent_lot = lot.parent_stock.get_parent_lot()
        else:
            parent_lot = lot.parent_lot
        lot.copy_production_details(parent_lot)
        lot.copy_sustainability_data(parent_lot)
    else:
        ### BIOFUEL
        biofuels = prefetched_data["biofuels"]
        biofuel_code = data.get("biofuel_code", None)
        lot.biofuel = None
        if not biofuel_code:
            errors.append(
                GenericError(
                    lot=lot, field="biofuel_code", error=MISSING_BIOFUEL, display_to_creator=True, is_blocking=True
                )
            )
        else:
            if biofuel_code not in biofuels:
                errors.append(
                    GenericError(
                        lot=lot, field="biofuel_code", error=UNKNOWN_BIOFUEL, display_to_creator=True, is_blocking=True
                    )
                )
            else:
                # all good
                lot.biofuel = biofuels[biofuel_code]
        ### FEEDSTOCK
        feedstocks = prefetched_data["feedstocks"]
        feedstock_code = data.get("feedstock_code", None)
        lot.feedstock = None
        if not feedstock_code:
            errors.append(
                GenericError(
                    lot=lot, field="feedstock_code", error=MISSING_FEEDSTOCK, display_to_creator=True, is_blocking=True
                )
            )
        else:
            if feedstock_code not in feedstocks:
                errors.append(
                    GenericError(
                        lot=lot,
                        field="feedstock_code",
                        error=UNKNOWN_FEEDSTOCK,
                        display_to_creator=True,
                        is_blocking=True,
                    )
                )
            else:
                # all good
                lot.feedstock = feedstocks[feedstock_code]
        ### COUNTRY OF ORIGIN
        countries = prefetched_data["countries"]
        country_code = data.get("country_code", None)
        lot.country_of_origin = None
        if not country_code:
            errors.append(
                GenericError(
                    lot=lot,
                    field="country_code",
                    error=MISSING_COUNTRY_OF_ORIGIN,
                    display_to_creator=True,
                    is_blocking=True,
                )
            )
        else:
            if country_code not in countries:
                errors.append(
                    GenericError(
                        lot=lot,
                        field="country_code",
                        error=UNKNOWN_COUNTRY_OF_ORIGIN,
                        display_to_creator=True,
                        is_blocking=True,
                    )
                )
            else:
                # all good
                lot.country_of_origin = countries[country_code]
    return errors


def compute_lot_quantity(lot, data):
    volume = None
    weight = None
    lhv_amount = None

    # normalize the given data in the form of a (quantity, unit) couple
    if data.get("quantity") is not None and data.get("unit") is not None:
        quantity = round(float(data.get("quantity")), 2)
        unit = data.get("unit", CarbureUnit.LITER).lower()
    elif data.get("volume") is not None:
        quantity = round(float(data.get("volume")), 2)
        unit = CarbureUnit.LITER
    elif data.get("weight") is not None:
        quantity = round(float(data.get("weight")), 2)
        unit = CarbureUnit.KILOGRAM
    elif data.get("lhv_amount") is not None:
        quantity = round(float(data.get("lhv_amount")), 2)
        unit = CarbureUnit.LHV
    else:
        raise Exception("No quantity was specified")

    # compute the different quantity values based on the previous config
    if unit == CarbureUnit.LITER:
        volume = quantity
        weight = round(volume * lot.biofuel.masse_volumique, 2)
        lhv_amount = round(volume * lot.biofuel.pci_litre, 2)
    elif unit == CarbureUnit.KILOGRAM:
        weight = quantity
        volume = round(weight / lot.biofuel.masse_volumique, 2)
        lhv_amount = round(volume * lot.biofuel.pci_litre, 2)
    elif unit == CarbureUnit.LHV:
        lhv_amount = quantity
        volume = round(lhv_amount / lot.biofuel.pci_litre, 2)
        weight = round(volume * lot.biofuel.masse_volumique, 2)

    return {"volume": volume, "weight": weight, "lhv_amount": lhv_amount}


def fill_volume_info(lot, data):
    errors = []
    ### VOLUME
    if lot.parent_stock is not None:
        # UPDATING VOLUME OF A LOT COMING FROM A STOCK SPLIT
        # 1) check volume diff
        try:
            quantity = compute_lot_quantity(lot, data)
            diff = round(lot.volume - quantity["volume"], 2)
            # 2) if new volume > old volume, ensure we have enough stock
            if diff < 0 and lot.parent_stock.remaining_volume < abs(diff):
                # not enough stock remaining, dont change anything
                errors.append(
                    GenericError(
                        lot=lot,
                        field="volume",
                        error=CarbureStockErrors.NOT_ENOUGH_VOLUME_LEFT,
                        display_to_creator=True,
                    )
                )
            else:
                # all good
                lot.volume = quantity["volume"]
                lot.weight = quantity["weight"]
                lot.lhv_amount = quantity["lhv_amount"]
                lot.parent_stock.remaining_volume = round(lot.parent_stock.remaining_volume + diff, 2)
                lot.parent_stock.remaining_weight = lot.parent_stock.get_weight()
                lot.parent_stock.remaining_lhv_amount = lot.parent_stock.get_lhv_amount()
                lot.parent_stock.save()
        except Exception:
            errors.append(
                GenericError(
                    lot=lot, field="volume", error=VOLUME_FORMAT_INCORRECT, display_to_creator=True, is_blocking=True
                )
            )

    elif lot.parent_lot is None:
        try:
            quantity = compute_lot_quantity(lot, data)
            lot.volume = quantity["volume"]
            lot.weight = quantity["weight"]
            lot.lhv_amount = quantity["lhv_amount"]
        except:
            traceback.print_exc()
            errors.append(
                GenericError(
                    lot=lot, field="volume", error=VOLUME_FORMAT_INCORRECT, display_to_creator=True, is_blocking=True
                )
            )
    return errors


def fill_supplier_info(lot, data, entity):
    errors = []
    # definitions:
    # supplier = my supplier - who supplied the biofuel to me
    # vendor = me (as a producer or trader)

    # OPERATOR: no vendor_certificate and supplier_certificate is mandatory (and becomes lot.supplier_certificate)
    # PRODUCER: no vendor_certificate and supplier_certificate is mandatory (and becomes lot.supplier_certificate)
    # TRADER: supplier_certificate optional (lot.supplier_certificate of lot1),
    #         vendor_certificate mandatory (and becomes lot.supplier_certificate of lot2)

    # default values
    lot.carbure_supplier = None
    lot.unknown_supplier = data.get("unknown_supplier", None)
    lot.supplier_certificate = str(data.get("supplier_certificate", "")).strip()

    # I AM THE SUPPLIER
    if str(data.get("carbure_supplier_id")) == str(entity.id):
        lot.carbure_supplier = entity
        lot.supplier_certificate = data.get("supplier_certificate", entity.default_certificate)
    # LOT FROM STOCK
    if lot.parent_stock:
        lot.carbure_supplier = entity
        lot.supplier_certificate = data.get("supplier_certificate", entity.default_certificate)
    # EXCEL: NO SUPPLIER IS SPECIFIED AND I AM THE PRODUCER
    if lot.carbure_producer and lot.carbure_producer.id == entity.id and not lot.carbure_supplier:
        lot.carbure_supplier = entity
        if not lot.supplier_certificate:
            lot.supplier_certificate = entity.default_certificate

    return errors


def fill_vendor_data(lot, data, entity):
    # I AM NEITHER THE PRODUCER NOR THE CLIENT - TRADING - OVERRIDE SOME FIELDS
    if entity != lot.carbure_supplier and entity != lot.carbure_client:
        lot.carbure_vendor = entity  # this will flag the transaction when it is validated in order to create 2 transactions (unknown_supplier -> vendor and vendor -> client)
        lot.vendor_certificate = data.get("vendor_certificate", entity.default_certificate)
    else:
        lot.vendor_certificate = None
        lot.carbure_vendor = None
        # patch to deal with people who confuse vendor certificate for supplier certificate
        if not lot.supplier_certificate and data.get("vendor_certificate", False):
            # maybe they used vendor_certificate ?
            lot.supplier_certificate = data.get("vendor_certificate", "")


def fill_ghg_info(lot, data):
    errors = []
    try:
        lot.eec = abs(float(data.get("eec", 0)))
    except:
        errors.append(GenericError(lot=lot, field="eec", error=WRONG_FLOAT_FORMAT, display_to_creator=True))
    try:
        lot.el = float(data.get("el", 0))
    except:
        errors.append(GenericError(lot=lot, field="el", error=WRONG_FLOAT_FORMAT, display_to_creator=True))
    try:
        lot.ep = abs(float(data.get("ep", 0)))
    except:
        errors.append(GenericError(lot=lot, field="ep", error=WRONG_FLOAT_FORMAT, display_to_creator=True))
    try:
        lot.etd = abs(float(data.get("etd", 0)))
    except:
        errors.append(GenericError(lot=lot, field="etd", error=WRONG_FLOAT_FORMAT, display_to_creator=True))
    try:
        lot.eu = abs(float(data.get("eu", 0)))
    except:
        errors.append(GenericError(lot=lot, field="eu", error=WRONG_FLOAT_FORMAT, display_to_creator=True))
    try:
        lot.esca = abs(float(data.get("esca", 0)))
    except:
        errors.append(GenericError(lot=lot, field="esca", error=WRONG_FLOAT_FORMAT, display_to_creator=True))
    try:
        lot.eccs = abs(float(data.get("eccs", 0)))
    except:
        errors.append(GenericError(lot=lot, field="eccs", error=WRONG_FLOAT_FORMAT, display_to_creator=True))
    try:
        lot.eccr = abs(float(data.get("eccr", 0)))
    except:
        errors.append(GenericError(lot=lot, field="eccr", error=WRONG_FLOAT_FORMAT, display_to_creator=True))
    try:
        lot.eee = abs(float(data.get("eee", 0)))
    except:
        errors.append(GenericError(lot=lot, field="eee", error=WRONG_FLOAT_FORMAT, display_to_creator=True))
    lot.update_ghg()
    return errors


def fill_delivery_type(lot, data):
    delivery_type = data.get("delivery_type", None)
    if delivery_type is None:
        lot.delivery_type = CarbureLot.UNKNOWN
    else:
        lot.delivery_type = data.get("delivery_type", None)
        if lot.delivery_type not in [
            CarbureLot.UNKNOWN,
            CarbureLot.RFC,
            CarbureLot.STOCK,
            CarbureLot.BLENDING,
            CarbureLot.EXPORT,
            CarbureLot.TRADING,
            CarbureLot.PROCESSING,
            CarbureLot.DIRECT,
            CarbureLot.FLUSHED,
        ]:
            lot.delivery_type = CarbureLot.UNKNOWN


def fill_delivery_data(lot, data, entity, prefetched_data):
    errors = []
    lot.transport_document_type = data.get("transport_document_type", None)
    if lot.transport_document_type is None:
        lot.transport_document_type = CarbureLot.DAE
    lot.transport_document_reference = data.get("transport_document_reference", None)

    dest = data.get("carbure_delivery_site_depot_id", None)
    if dest in prefetched_data["depots"]:
        lot.carbure_delivery_site = prefetched_data["depots"][dest]
        lot.delivery_site_country = lot.carbure_delivery_site.country
    else:
        lot.carbure_delivery_site = None
        errors.append(
            GenericError(
                lot=lot,
                field="carbure_delivery_site_depot_id",
                error=UNKNOWN_DELIVERY_SITE,
                display_to_creator=True,
                is_blocking=True,
            )
        )
    if not lot.carbure_delivery_site:
        lot.unknown_delivery_site = data.get("unknown_delivery_site", None)
        delivery_country_code = data.get("delivery_site_country_code", None)
        if delivery_country_code in prefetched_data["countries"]:
            lot.delivery_site_country = prefetched_data["countries"][delivery_country_code]

    if (
        entity.entity_type == Entity.OPERATOR
        and lot.carbure_client == entity
        and lot.delivery_type == CarbureLot.UNKNOWN
    ):
        lot.delivery_type = CarbureLot.BLENDING
    return errors


def fill_client_data(lot, data, entity, prefetched_data):
    errors = []
    carbure_client_id = data.get("carbure_client_id", None)
    if entity.entity_type == Entity.OPERATOR and carbure_client_id is None and lot.delivery_type == CarbureLot.UNKNOWN:
        lot.carbure_client = entity

    try:
        carbure_client_id = int(carbure_client_id)
        if carbure_client_id in prefetched_data["clients"]:
            lot.carbure_client = prefetched_data["clients"][carbure_client_id]
        else:
            lot.carbure_client = None
            if lot.delivery_type in [CarbureLot.PROCESSING, CarbureLot.TRADING, CarbureLot.STOCK, CarbureLot.BLENDING]:
                errors.append(
                    GenericError(
                        lot=lot,
                        field="carbure_client_id",
                        error=UNKNOWN_CLIENT,
                        display_to_creator=True,
                        is_blocking=True,
                    )
                )
            else:
                errors.append(
                    GenericError(lot=lot, field="carbure_client_id", error=UNKNOWN_CLIENT, display_to_creator=True)
                )
    except:
        pass
    lot.unknown_client = data.get("unknown_client", None)
    return errors


def construct_carbure_lot(prefetched_data, entity, data, existing_lot=None):
    errors = []
    if existing_lot:
        lot = existing_lot
    else:
        lot = CarbureLot()
    lot.free_field = data.get("free_field", None)
    lot.added_by = entity
    carbure_stock_id = data.get("carbure_stock_id", False)
    if carbure_stock_id or lot.parent_stock_id:
        # Lot is extracted from STOCK.
        # FILL sustainability data from parent_stock
        if lot.parent_stock is not None:
            parent_stock = lot.parent_stock
        else:
            try:
                parent_stock = CarbureStock.objects.get(carbure_id=carbure_stock_id)
            except Exception as e:
                # traceback.print_exc()
                print("Could not find stock %s" % (carbure_stock_id))
                return None, []
        original_lot = parent_stock.get_parent_lot()
        lot.parent_stock = parent_stock
        lot.copy_production_details(original_lot)
        lot.copy_sustainability_data(original_lot)
        lot.carbure_dispatch_site = parent_stock.depot
        lot.carbure_supplier = parent_stock.carbure_client
        lot.biofuel = parent_stock.biofuel
    else:
        # FILL sustainability data from excel file
        errors += fill_production_info(lot, data, entity, prefetched_data)
        errors += fill_basic_info(lot, data, prefetched_data)
        errors += fill_ghg_info(lot, data)

    # common data
    fill_delivery_type(lot, data)
    errors += fill_client_data(lot, data, entity, prefetched_data)
    errors += fill_volume_info(lot, data)
    errors += fill_delivery_date(lot, data)
    errors += fill_supplier_info(lot, data, entity)
    errors += fill_delivery_data(lot, data, entity, prefetched_data)
    fill_vendor_data(lot, data, entity)
    return lot, errors


def bulk_insert_lots(
    entity: Entity, lots: List[CarbureLot], errors: List[GenericError], prefetched_data: dict
) -> QuerySet:
    created = CarbureLot.objects.bulk_create(lots, batch_size=100)
    inserted_lots = (
        CarbureLot.objects.select_related(
            "carbure_producer",
            "carbure_supplier",
            "carbure_client",
            "added_by",
            "carbure_production_site",
            "carbure_production_site__producer",
            "carbure_production_site__country",
            "production_country",
            "carbure_dispatch_site",
            "carbure_dispatch_site__country",
            "dispatch_site_country",
            "carbure_delivery_site",
            "carbure_delivery_site__country",
            "delivery_site_country",
            "feedstock",
            "biofuel",
            "country_of_origin",
            "parent_lot",
            "parent_stock",
            "parent_stock__carbure_client",
            "parent_stock__carbure_supplier",
            "parent_stock__feedstock",
            "parent_stock__biofuel",
            "parent_stock__depot",
            "parent_stock__country_of_origin",
            "parent_stock__production_country",
        )
        .prefetch_related(
            "genericerror_set",
            "carbure_production_site__productionsitecertificate_set",
            "carbure_production_site__productionsiteinput_set",
            "carbure_production_site__productionsiteoutput_set",
        )
        .filter(added_by=entity)
        .order_by("-id")[0 : len(lots)]
    )
    errors = reversed(errors)  # lots are fetched by DESC ID
    for lot, lot_errors in zip(inserted_lots, errors):
        for e in lot_errors:
            e.lot_id = lot.id
    bulk_sanity_checks(inserted_lots, prefetched_data)
    GenericError.objects.bulk_create([error for lot_errors in errors for error in lot_errors], batch_size=100)
    return inserted_lots
