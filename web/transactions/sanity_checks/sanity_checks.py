import traceback

from core.models import CarbureLot, GenericError
from .helpers import get_prefetched_data
from .mandatory import *
from .ghg import *
from .general import *
from .double_counting import *
from .biofuel_feedstock import *
from core.models import CarbureLot, CarbureLotReliabilityScore, GenericError

from django.db import transaction


def sanity_checks(lot: CarbureLot, prefetched_data) -> list[GenericError]:
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
        check_missing_vendor_certificate(lot),
        # double counting errors
        check_missing_ref_dbl_counting(lot),
        check_unknown_double_counting_certificate(lot, prefetched_data),
        check_expired_double_counting_certificate(lot, prefetched_data),
        check_invalid_double_counting_certificate(lot, prefetched_data),
        check_double_counting_quotas(lot, prefetched_data),
        # biofuel/feedstock errors
        *check_mp_bc_incoherent(lot),  # this one generates a list of errors so we flatten it with *
        *check_provenance_mp(lot),  # same here
        check_deprecated_mp(lot),
        # ghg errors
        check_etd_anormal_high(lot, prefetched_data),
        check_etd_no_eu_too_low(lot, prefetched_data),
        # check_etd_eu_default_value(lot, prefetched_data),
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
        # general errors
        check_volume_faible(lot),
        check_year_locked(lot, prefetched_data),
        check_mac_bc_wrong(lot),
        check_mac_not_efpe(lot),
        check_delivery_in_the_future(lot),
        # check_mp_not_configured(lot, prefetched_data),
        # check_bc_not_configured(lot, prefetched_data),
        check_depot_not_configured(lot, prefetched_data),
    ]

    # remove empty values from error list
    return [error for error in errors if error]


def bulk_sanity_checks(lots, prefetched_data=None, dry_run=False):
    if prefetched_data is None:
        prefetched_data = get_prefetched_data()

    errors = []

    # cleanup previous errors
    if not dry_run:
        GenericError.objects.filter(lot_id__in=[l.id for l in lots]).delete()

    for lot in lots:
        try:
            errors += sanity_checks(lot, prefetched_data)
        except:
            traceback.print_exc()

    # save new errors
    if not dry_run:
        GenericError.objects.bulk_create(errors, batch_size=1000)

    return errors


def bulk_scoring(lots, prefetched_data=None):
    if not prefetched_data:
        prefetched_data = get_prefetched_data()
    # delete scoring entries for the lots
    lotids = [l.id for l in lots]
    CarbureLotReliabilityScore.objects.filter(lot_id__in=lotids).delete()
    # recalc score
    clrs = []
    # bulk update lots
    with transaction.atomic():
        for l in lots:
            clrs_entries = l.recalc_reliability_score(prefetched_data)
            clrs += clrs_entries
        CarbureLot.objects.bulk_update(lots, ["data_reliability_score"])
        CarbureLotReliabilityScore.objects.bulk_create(clrs)
