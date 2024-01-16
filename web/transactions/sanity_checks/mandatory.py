import datetime
from core.carburetypes import CarbureCertificatesErrors, CarbureSanityCheckErrors
from core.models import CarbureLot, Entity
from .helpers import generic_error, is_french_delivery


def check_missing_volume(lot: CarbureLot):
    if not lot.volume:
        return generic_error(
            error=CarbureSanityCheckErrors.MISSING_VOLUME,
            lot=lot,
            field="volume",
            is_blocking=True,
        )


def check_missing_biofuel(lot: CarbureLot):
    if not lot.biofuel:
        return generic_error(
            error=CarbureSanityCheckErrors.MISSING_BIOFUEL,
            lot=lot,
            field="biofuel",
            is_blocking=True,
        )


def check_missing_feedstock(lot: CarbureLot):
    if not lot.feedstock:
        return generic_error(
            error=CarbureSanityCheckErrors.MISSING_FEEDSTOCK,
            lot=lot,
            field="feedstock",
            is_blocking=True,
        )


def check_unkown_production_site(lot: CarbureLot):
    if lot.carbure_producer and lot.carbure_production_site is None:
        return generic_error(
            error=CarbureSanityCheckErrors.UNKNOWN_PRODUCTION_SITE,
            lot=lot,
            field="production_site",
            is_blocking=True,
        )


def check_missing_production_site_comdate(lot: CarbureLot):
    if not lot.carbure_production_site and not lot.production_site_commissioning_date:
        return generic_error(
            error=CarbureSanityCheckErrors.MISSING_PRODUCTION_SITE_COMDATE,
            lot=lot,
            field="production_site_commissioning_date",
            is_blocking=True,
        )


def check_missing_transport_document_reference(lot: CarbureLot):
    if lot.delivery_type not in [CarbureLot.RFC, CarbureLot.FLUSHED] and not lot.transport_document_reference:
        return generic_error(
            error=CarbureSanityCheckErrors.MISSING_TRANSPORT_DOCUMENT_REFERENCE,
            lot=lot,
            field="transport_document_reference",
            is_blocking=True,
        )


def check_missing_carbure_delivery_site(lot: CarbureLot):
    # we need to know the Depot
    if is_french_delivery(lot) and not lot.carbure_delivery_site:
        return generic_error(
            error=CarbureSanityCheckErrors.MISSING_CARBURE_DELIVERY_SITE,
            lot=lot,
            field="delivery_site",
            is_blocking=True,
        )


def check_missing_carbure_client(lot: CarbureLot):
    if is_french_delivery(lot) and not lot.carbure_client:
        return generic_error(
            error=CarbureSanityCheckErrors.MISSING_CARBURE_CLIENT,
            lot=lot,
            field="client",
            is_blocking=True,
        )


def check_missing_delivery_date(lot: CarbureLot):
    if not lot.delivery_date:
        return generic_error(
            error=CarbureSanityCheckErrors.MISSING_DELIVERY_DATE,
            lot=lot,
            field="delivery_date",
            is_blocking=True,
        )


def check_wrong_delivery_date(lot: CarbureLot):
    if not lot.delivery_date:
        return

    today = datetime.date.today()
    time_to_delivery = lot.delivery_date - today
    in_ten_years = datetime.timedelta(days=3650)
    ten_years_ago = datetime.timedelta(days=-3650)

    if time_to_delivery > in_ten_years or time_to_delivery < ten_years_ago:
        return generic_error(
            error=CarbureSanityCheckErrors.WRONG_DELIVERY_DATE,
            lot=lot,
            field="delivery_date",
            is_blocking=True,
        )


def check_missing_delivery_site_country(lot: CarbureLot):
    if not lot.delivery_site_country:
        return generic_error(
            error=CarbureSanityCheckErrors.MISSING_DELIVERY_SITE_COUNTRY,
            lot=lot,
            field="delivery_site_country",
            is_blocking=True,
        )


def check_missing_feedstock_country_of_origin(lot: CarbureLot):
    if lot.delivery_site_country and lot.delivery_site_country.is_in_europe and not lot.country_of_origin:
        return generic_error(
            error=CarbureSanityCheckErrors.MISSING_FEEDSTOCK_COUNTRY_OF_ORIGIN,
            lot=lot,
            field="country_of_origin",
            is_blocking=True,
        )


def check_missing_supplier_certificate(lot: CarbureLot):
    if lot.carbure_client and lot.carbure_client.entity_type in [Entity.OPERATOR, Entity.POWER_STATION]:
        # client is an operator
        # make sure we have a certificate
        if not lot.supplier_certificate and not lot.vendor_certificate:
            return generic_error(
                error=CarbureCertificatesErrors.MISSING_SUPPLIER_CERTIFICATE,
                lot=lot,
                field="supplier_certificate",
                is_blocking=True,
            )


def check_missing_vendor_certificate(lot: CarbureLot):
    if lot.carbure_client != lot.added_by and lot.carbure_supplier != lot.added_by:
        if not lot.vendor_certificate:
            return generic_error(
                error=CarbureCertificatesErrors.MISSING_VENDOR_CERTIFICATE,
                lot=lot,
                field="vendor_certificate",
                is_blocking=True,
            )
