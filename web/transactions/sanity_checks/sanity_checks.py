from core.models import CarbureLot, GenericError
from .mandatory import *
from .ghg import *
from .certificates import *


def sanity_checks(lot: CarbureLot, prefetched_data):
    if lot.lot_status == CarbureLot.FLUSHED:
        return []

    errors: list[GenericError | None] = [
        # mandatory fields errors
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
        # ghg errors
        check_etd_anormal_high(lot, prefetched_data),
        check_etd_no_eu_too_low(lot, prefetched_data),
        check_etd_eu_default_value(lot, prefetched_data),
        check_eec_anormal_low(lot, prefetched_data),
        check_eec_anormal_high(lot, prefetched_data),
        check_ep_anormal_low(lot, prefetched_data),
        check_ep_anormal_high(lot, prefetched_data),
        check_ghg_etd_0(lot),
        check_ghg_ep_0(lot),
        check_ghg_el_neg(lot),
        check_ghg_eec_0(lot),
        check_eec_with_residue(lot),
        check_ghg_reduc(lot),
        check_ghg_reduc_for_production_site(lot),
        # certificate errors
        check_unknown_double_counting_certificate(lot, prefetched_data),
        check_expired_double_counting_certificate(lot, prefetched_data),
        check_invalid_double_counting_certificate(lot, prefetched_data),
    ]

    # remove empty values from error list
    return [error for error in errors if error]
