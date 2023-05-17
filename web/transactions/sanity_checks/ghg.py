import datetime
from core.carburetypes import CarbureMLGHGErrors, CarbureSanityCheckErrors
from core.models import CarbureLot
from .helpers import generic_error, is_red_ii

oct2015 = datetime.date(year=2015, month=10, day=5)
jan2021 = datetime.date(year=2021, month=1, day=1)


def check_etd_anormal_high(lot: CarbureLot, prefetched_data):
    etd = get_etd(lot, prefetched_data)
    if etd is None:
        return

    if lot.etd > 2 * etd and lot.etd > 5:
        return generic_error(
            error=CarbureMLGHGErrors.ETD_ANORMAL_HIGH,
            lot=lot,
            display_to_creator=False,
            field="etd",
        )


def check_etd_no_eu_too_low(lot: CarbureLot, prefetched_data):
    etd = get_etd(lot, prefetched_data)
    if etd is None:
        return

    if (not lot.country_of_origin or not lot.country_of_origin.is_in_europe) and lot.etd < etd:
        return generic_error(
            error=CarbureMLGHGErrors.ETD_NO_EU_TOO_LOW,
            lot=lot,
            display_to_creator=False,
            field="etd",
        )


def check_etd_eu_default_value(lot: CarbureLot, prefetched_data):
    etd = get_etd(lot, prefetched_data)
    if etd is None:
        return

    if lot.country_of_origin and lot.country_of_origin.is_in_europe and lot.etd == etd:
        return generic_error(
            error=CarbureMLGHGErrors.ETD_EU_DEFAULT_VALUE,
            lot=lot,
            display_to_creator=False,
            field="etd",
        )


def check_eec_anormal_low(lot: CarbureLot, prefetched_data):
    eec = get_eec(lot, prefetched_data)
    if eec is None:
        return

    if lot.eec < 0.8 * min(eec.default_value, eec.average):
        return generic_error(
            error=CarbureMLGHGErrors.EEC_ANORMAL_LOW,
            lot=lot,
            display_to_creator=False,
            field="eec",
        )


def check_eec_anormal_high(lot: CarbureLot, prefetched_data):
    eec = get_eec(lot, prefetched_data)
    if eec is None:
        return

    if lot.eec > 1.2 * max(eec.default_value, eec.average):
        return generic_error(
            error=CarbureMLGHGErrors.EEC_ANORMAL_HIGH,
            lot=lot,
            display_to_creator=False,
            field="eec",
        )


def check_ep_anormal_low(lot: CarbureLot, prefetched_data):
    ep = get_ep(lot, prefetched_data)
    if ep is None:
        return

    if lot.ep < 0.8 * ep.average:
        return generic_error(
            error=CarbureMLGHGErrors.EP_ANORMAL_LOW,
            lot=lot,
            display_to_creator=False,
            field="ep",
        )


def check_ep_anormal_high(lot: CarbureLot, prefetched_data):
    ep = get_ep(lot, prefetched_data)
    if ep is None:
        return

    if lot.ep > 1.2 * ep.default_value_max_ep:
        return generic_error(
            error=CarbureMLGHGErrors.EP_ANORMAL_HIGH,
            lot=lot,
            display_to_creator=False,
            field="ep",
        )


def check_ghg_etd_0(lot: CarbureLot):
    if lot.etd <= 0:
        return generic_error(
            error=CarbureSanityCheckErrors.GHG_ETD_0,
            lot=lot,
            is_blocking=True,
            field="etd",
        )


def check_ghg_ep_0(lot: CarbureLot):
    if lot.ep <= 0:
        return generic_error(
            error=CarbureSanityCheckErrors.GHG_EP_0,
            lot=lot,
            is_blocking=True,
            field="ep",
        )


def check_ghg_el_neg(lot: CarbureLot):
    if lot.el < 0:
        return generic_error(
            error=CarbureSanityCheckErrors.GHG_EL_NEG,
            lot=lot,
            field="el",
        )


def check_ghg_eec_0(lot: CarbureLot):
    # 2022-02-01: is_blocking=True sur demande de Guillaume
    if lot.feedstock and lot.feedstock.category == "CONV" and lot.eec == 0:
        return generic_error(
            error=CarbureSanityCheckErrors.GHG_EEC_0,
            lot=lot,
            is_blocking=True,
            extra="GES Culture 0 pour MP conventionnelle (%s)" % (lot.feedstock.name),
            field="eec",
        )


def check_eec_with_residue(lot: CarbureLot):
    if lot.feedstock and lot.feedstock.category != "CONV" and lot.feedstock.code != "EP2" and lot.eec != 0:
        return generic_error(
            error=CarbureSanityCheckErrors.EEC_WITH_RESIDUE,
            lot=lot,
            field="eec",
        )


def check_ghg_reduc(lot: CarbureLot):
    if is_red_ii(lot):
        if lot.ghg_reduction_red_ii >= 100:
            return generic_error(error=CarbureSanityCheckErrors.GHG_REDUC_SUP_100, lot=lot)
        elif lot.ghg_reduction_red_ii > 99:
            return generic_error(error=CarbureSanityCheckErrors.GHG_REDUC_SUP_99, lot=lot)
        elif lot.ghg_reduction_red_ii < 50:
            return generic_error(error=CarbureSanityCheckErrors.GHG_REDUC_INF_50, lot=lot, is_blocking=True)
    else:
        if lot.ghg_reduction >= 100:
            return generic_error(error=CarbureSanityCheckErrors.GHG_REDUC_SUP_100, lot=lot)
        elif lot.ghg_reduction > 99:
            return generic_error(error=CarbureSanityCheckErrors.GHG_REDUC_SUP_99, lot=lot)
        elif lot.ghg_reduction < 50:
            return generic_error(error=CarbureSanityCheckErrors.GHG_REDUC_INF_50, lot=lot, is_blocking=True)


def check_ghg_reduc_for_production_site(lot: CarbureLot):
    commissioning_date = get_commissioning_date(lot)
    if commissioning_date is None:
        return

    if is_red_ii(lot):
        if commissioning_date > oct2015 and lot.ghg_reduction_red_ii < 60:
            return generic_error(
                error=CarbureSanityCheckErrors.GHG_REDUC_INF_60,
                lot=lot,
                is_blocking=True,
            )
        if commissioning_date >= jan2021 and lot.ghg_reduction_red_ii < 65:
            return generic_error(
                error=CarbureSanityCheckErrors.GHG_REDUC_INF_65,
                lot=lot,
                is_blocking=True,
            )
    else:
        if commissioning_date > oct2015 and lot.ghg_reduction < 60:
            return generic_error(
                error=CarbureSanityCheckErrors.GHG_REDUC_INF_60,
                lot=lot,
                is_blocking=True,
            )
        if commissioning_date >= jan2021 and lot.ghg_reduction < 65:
            return generic_error(
                error=CarbureSanityCheckErrors.GHG_REDUC_INF_65,
                lot=lot,
                is_blocking=True,
            )


def get_etd(lot: CarbureLot, prefetched_data):
    if not lot.feedstock:
        return None

    etd = prefetched_data["etd"]
    return etd.get(lot.feedstock)


def get_eec(lot: CarbureLot, prefetched_data):
    if not lot.feedstock or not lot.country_of_origin:
        return None

    eec = prefetched_data["eec"]
    key = lot.feedstock.code + lot.country_of_origin.code_pays
    return eec.get(key)


def get_ep(lot: CarbureLot, prefetched_data):
    if not lot.feedstock or not lot.biofuel:
        return None

    ep = prefetched_data["ep"]
    key = lot.feedstock.code + lot.biofuel.code
    return ep.get(key)


def get_commissioning_date(lot: CarbureLot):
    commissioning_date = lot.production_site_commissioning_date
    if not isinstance(commissioning_date, datetime.datetime) and not isinstance(commissioning_date, datetime.date):
        return None
    return commissioning_date
