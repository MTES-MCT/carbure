from core.models import CarbureLot, GenericError
from .mandatory import *


def sanity_checks(lot: CarbureLot):
    if lot.lot_status == CarbureLot.FLUSHED:
        return []

    errors: list[GenericError] = [
        check_missing_volume(lot),
        check_missing_biofuel(lot),
        check_missing_feedstock(lot),
        check_unkown_production_site(lot),
        check_missing_production_site_comdate(lot),
        check_missing_transport_document_reference(lot),
        check_missing_carbure_delivery_site(lot),
        check_missing_carbure_client(lot),
        check_missing_delivery_date(lot),
        check_wrong_delivery_date(lot),
        check_missing_delivery_site_country(lot),
        check_missing_feedstock_country_of_origin(lot),
        check_missing_supplier_certificate(lot),
    ]

    # remove empty values from error list
    return [error for error in errors if error]
