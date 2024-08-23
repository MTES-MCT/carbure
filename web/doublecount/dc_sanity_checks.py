from typing import List

from core.models import Biocarburant, MatierePremiere
from doublecount.errors import DcError, DoubleCountingError, error
from doublecount.models import DoubleCountingApplication, DoubleCountingProduction, DoubleCountingSourcing
from doublecount.parser.types import ProductionBaseRow, ProductionRow, SourcingRow
from transactions.sanity_checks.double_counting import get_dc_biofuel_feedstock_incompatibilities


# check a line in the sourcing section of an imported dc excel file
def check_sourcing_row(data: SourcingRow) -> List[DcError]:
    errors: List[DcError] = []
    line = data["line"]
    meta = {"year": data["year"]}

    if not data["feedstock"]:
        errors.append(error(DoubleCountingError.MISSING_FEEDSTOCK, line, meta))

    if not data["origin_country"]:
        meta["feedstock"] = data["feedstock"]
        errors.append(error(DoubleCountingError.MISSING_COUNTRY_OF_ORIGIN, line, meta))

    return errors


# check a line in the production section of an imported dc excel file
def check_production_row(production: DoubleCountingProduction, data: ProductionRow) -> List[DcError]:
    errors: List[DcError] = []
    line = data["line"]
    tab_name = "Reconnaissance double comptage"

    if production.max_production_capacity < production.estimated_production:
        meta = {
            "feedstock": production.feedstock.name,
            "biofuel": production.biofuel.name,
            "max_production_capacity": production.max_production_capacity,
            "estimated_production": production.estimated_production,
            "tab_name": tab_name,
            "year": data["year"],
        }
        errors.append(error(DoubleCountingError.PRODUCTION_MISMATCH_PRODUCTION_MAX, line, meta))

    # check that requested quotas aren't bigger than estimated production
    if (production.requested_quota or 0) > (production.estimated_production or 0):
        meta = {
            "feedstock": production.feedstock.name,
            "biofuel": production.biofuel.name,
            "estimated_production": production.estimated_production,
            "requested_quota": production.requested_quota,
            "tab_name": tab_name,
            "year": data["year"],
        }
        errors.append(error(DoubleCountingError.PRODUCTION_MISMATCH_QUOTA, line, meta))

    return errors


# check a line in the production section of an imported dc excel file
def check_production_row_integrity(
    feedstock: MatierePremiere,
    biofuel: Biocarburant,
    data: ProductionBaseRow,
    tab_name: str,
    dca: DoubleCountingApplication,
) -> List[DcError]:
    errors: List[DcError] = []
    line = data["line"]
    year = data["year"]
    meta = {"tab_name": tab_name, "year": year}

    if year not in [dca.period_start.year, dca.period_end.year]:
        errors.append(error(DoubleCountingError.INVALID_YEAR, line, meta))

    # if not data["biofuel"]:
    #     errors.append(error(DoubleCountingError.MISSING_BIOFUEL, line, meta))

    # if not data["feedstock"]:
    #     errors.append(error(DoubleCountingError.MISSING_FEEDSTOCK, line, meta))

    if not biofuel:
        errors.append(error(DoubleCountingError.MISSING_BIOFUEL, line, meta))

    if not feedstock:
        errors.append(error(DoubleCountingError.MISSING_FEEDSTOCK, line, meta))

    if feedstock and biofuel:
        incompatibilities: List[str] = []

        for e in get_dc_biofuel_feedstock_incompatibilities(biofuel, feedstock):
            incompatibilities.append(e)

        meta = {
            "feedstock": feedstock.code,
            "biofuel": biofuel.code,
            "infos": incompatibilities,
            "tab_name": tab_name,
        }
        if len(incompatibilities) > 0:
            errors.append(error(DoubleCountingError.MP_BC_INCOHERENT, line, meta))

    return errors


# check rules that check sourcing and production
def check_dc_globally(
    sourcing: list[DoubleCountingSourcing],
    production: list[DoubleCountingProduction],
) -> List[DcError]:
    errors: List[DcError] = []

    errors += check_sourcing_vs_production(sourcing, production)
    # errors += check_pome_excess(production) TODO : decommenter ça et les tests POME_GT_2000 quand l'outil sera mis à disposition de producteur, pour l'instant ça empeche Emilien de valider les dossiers rapidement (sinon doit contacter le producteur)

    return errors


# check that sourcing feedstock quantities match production biofuel quantities
def check_sourcing_vs_production(
    sourcing: list[DoubleCountingSourcing], production: list[DoubleCountingProduction]
) -> List[DcError]:
    errors: List[DcError] = []

    # group sourcing by year and feedstock, and sum the total quantity
    sourcing_by_year_by_feedstock = {}
    for s in sourcing:
        year = s.year
        feedstock = s.feedstock.code if s.feedstock else "UNKNOWN"
        if year not in sourcing_by_year_by_feedstock:
            sourcing_by_year_by_feedstock[year] = {}
        if feedstock not in sourcing_by_year_by_feedstock[year]:
            sourcing_by_year_by_feedstock[year][feedstock] = 0
        sourcing_by_year_by_feedstock[year][feedstock] += s.metric_tonnes or 0

    # group production by year and feedstock and sum estimated production
    production_by_year_by_feedstock = {}
    for p in production:
        year = p.year
        feedstock = p.feedstock.code if p.feedstock else "UNKNOWN"
        if year not in production_by_year_by_feedstock:
            production_by_year_by_feedstock[year] = {}
        if feedstock not in production_by_year_by_feedstock[year]:
            production_by_year_by_feedstock[year][feedstock] = 0
        production_by_year_by_feedstock[year][feedstock] += p.estimated_production or 0

    for year in production_by_year_by_feedstock:
        for feedstock in production_by_year_by_feedstock[year]:
            production = production_by_year_by_feedstock[year].get(feedstock, 0)
            sourcing = sourcing_by_year_by_feedstock.get(year, {}).get(feedstock, 0)
            # check that the sourced amount of feedstock roughly matches the total production generated with this feedstock
            if production > sourcing:
                meta = {
                    "feedstock": feedstock,
                    "year": year,
                    "sourcing": sourcing,
                    "production": production,
                }
                errors.append(error(DoubleCountingError.PRODUCTION_MISMATCH_SOURCING, meta=meta))

    return errors


# check that biofuels made with POME (EFFLUENTS_HUILERIES_PALME_RAFLE) aren't requested in the quota for more than 2000 tonnes / year
def check_pome_excess(production: list[DoubleCountingProduction]) -> List[DcError]:
    errors: List[DcError] = []

    pome_requested_by_year = {}
    for p in production:
        if p.feedstock.code != "EFFLUENTS_HUILERIES_PALME_RAFLE":
            continue
        if p.requested_quota == 0:
            continue
        if p.year not in pome_requested_by_year:
            pome_requested_by_year[p.year] = 0
        pome_requested_by_year[p.year] += p.requested_quota or 0

    for year in pome_requested_by_year:
        requested_quota = pome_requested_by_year[year]
        if requested_quota > 2000:
            meta = {"year": year, "requested_production": requested_quota}
            errors.append(error(DoubleCountingError.POME_GT_2000, meta=meta))

    return errors
