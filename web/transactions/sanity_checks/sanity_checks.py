import traceback

from django.db import transaction
from django.db.models import QuerySet

from core.models import CarbureLot, CarbureLotReliabilityScore, GenericError

from .biofuel_feedstock import check_deprecated_mp, check_mp_bc_incoherent, check_provenance_mp
from .double_counting import (
    check_expired_double_counting_certificate,
    check_invalid_double_counting_certificate,
    check_missing_ref_dbl_counting,
    check_unknown_double_counting_certificate,
)
from .general import (
    check_declaration_already_validated,
    check_delivery_date_validity,
    check_delivery_in_the_future,
    check_depot_not_configured,
    check_mac_bc_wrong,
    check_mac_not_efpe,
    check_volume_faible,
    check_year_locked,
)
from .ghg import (
    check_eec_anormal_high,
    check_eec_anormal_low,
    check_eec_with_residue,
    check_ep_anormal_high,
    check_ep_anormal_low,
    check_etd_anormal_high,
    check_etd_no_eu_too_low,
    check_ghg_eec_0,
    check_ghg_el_neg,
    check_ghg_ep_0,
    check_ghg_etd_0,
    check_ghg_reduc,
    check_ghg_reduc_for_production_site,
)
from .helpers import get_prefetched_data
from .mandatory import (
    check_missing_biofuel,
    check_missing_carbure_client,
    check_missing_carbure_delivery_site,
    check_missing_delivery_date,
    check_missing_delivery_site_country,
    check_missing_feedstock,
    check_missing_feedstock_country_of_origin,
    check_missing_production_site_comdate,
    check_missing_supplier_certificate,
    check_missing_transport_document_reference,
    check_missing_vendor_certificate,
    check_missing_volume,
    check_production_info,
    check_unkown_production_site,
    check_wrong_delivery_date,
)


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
        check_production_info(lot),
        # double counting errors
        check_missing_ref_dbl_counting(lot),
        check_unknown_double_counting_certificate(lot, prefetched_data),
        check_expired_double_counting_certificate(lot, prefetched_data),
        check_invalid_double_counting_certificate(lot, prefetched_data),
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
        check_declaration_already_validated(lot, prefetched_data),
        check_volume_faible(lot),
        check_year_locked(lot, prefetched_data),
        check_mac_bc_wrong(lot),
        check_mac_not_efpe(lot),
        check_delivery_in_the_future(lot),
        # check_mp_not_configured(lot, prefetched_data),
        # check_bc_not_configured(lot, prefetched_data),
        check_depot_not_configured(lot, prefetched_data),
        check_delivery_date_validity(lot),
    ]

    # remove empty values from error list
    return [error for error in errors if error]


def bulk_sanity_checks(lots, prefetched_data=None, dry_run=False):
    if isinstance(lots, QuerySet):
        lots = annotate_lots(lots)

    if prefetched_data is None:
        prefetched_data = get_prefetched_data()

    errors = []

    # cleanup previous errors
    if not dry_run:
        GenericError.objects.filter(lot_id__in=[lot.id for lot in lots]).delete()

    for lot in lots:
        try:
            errors += sanity_checks(lot, prefetched_data)
        except Exception:
            traceback.print_exc()

    # save new errors
    if not dry_run:
        GenericError.objects.bulk_create(errors, batch_size=1000)

    return errors


def bulk_scoring(lots, prefetched_data=None):
    if not prefetched_data:
        prefetched_data = get_prefetched_data()

    if isinstance(lots, QuerySet):
        lots = annotate_lots(lots)

    # delete scoring entries for the lots
    lotids = [lot.id for lot in lots]
    CarbureLotReliabilityScore.objects.filter(lot_id__in=lotids).delete()
    # recalc score
    clrs = []
    # bulk update lots
    with transaction.atomic():
        for lot in lots:
            clrs_entries = lot.recalc_reliability_score(prefetched_data)
            clrs += clrs_entries
        CarbureLot.objects.bulk_update(lots, ["data_reliability_score"])
        CarbureLotReliabilityScore.objects.bulk_create(clrs)


def annotate_lots(lots: QuerySet[CarbureLot]):
    return lots.select_related(
        "carbure_producer",
        "carbure_supplier",
        "carbure_client",
        "added_by",
        "carbure_production_site",
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
    ).prefetch_related("genericerror_set", "carbure_production_site__productionsitecertificate_set")
