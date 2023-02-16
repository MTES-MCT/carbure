from typing import List, TypedDict
from doublecount.models import DoubleCountingProduction, DoubleCountingSourcing
from core.models import Biocarburant, MatierePremiere
from doublecount.dc_parser import ProductionRow, SourcingRow


class DoubleCountingError:
    NOT_DC_FEEDSTOCK = "NOT_DC_FEEDSTOCK"
    PRODUCTION_MISMATCH_SOURCING = "PRODUCTION_MISMATCH_SOURCING"
    POME_GT_2000 = "POME_GT_2000"
    PRODUCTION_MISMATCH_QUOTA = "PRODUCTION_MISMATCH_QUOTA"
    MP_BC_INCOHERENT = "MP_BC_INCOHERENT"
    UNKNOWN_FEEDSTOCK = "UNKNOWN_FEEDSTOCK"
    UNKNOWN_BIOFUEL = "UNKNOWN_BIOFUEL"
    MISSING_FEEDSTOCK = "MISSING_FEEDSTOCK"
    MISSING_BIOFUEL = "MISSING_BIOFUEL"
    MISSING_ESTIMATED_PRODUCTION = "MISSING_ESTIMATED_PRODUCTION"


class DcError(TypedDict):
    error: str
    line_number: int
    is_blocking: bool
    meta: dict


def error(type: str, line: int = -1, meta: dict = {}, is_blocking: bool = True) -> DcError:
    return {
        "error": type,
        "line_number": line,
        "is_blocking": is_blocking,
        "meta": meta,
    }


# check a line in the sourcing section of an imported dc excel file
def check_sourcing_row(sourcing: DoubleCountingSourcing, data: SourcingRow) -> List[DcError]:
    errors: List[DcError] = []
    line = data["line"]

    if not data["feedstock"]:
        errors.append(error(DoubleCountingError.MISSING_FEEDSTOCK, line))
    elif not sourcing.feedstock_id:
        errors.append(error(DoubleCountingError.UNKNOWN_FEEDSTOCK, line, {"feedstock": data["feedstock"]}))

    return errors


# check a line in the production section of an imported dc excel file
def check_production_row(production: DoubleCountingProduction, data: ProductionRow) -> List[DcError]:
    errors: List[DcError] = []
    line = data["line"]

    if not data["feedstock"]:
        errors.append(error(DoubleCountingError.MISSING_FEEDSTOCK, line))
    elif not production.feedstock_id:
        errors.append(error(DoubleCountingError.UNKNOWN_FEEDSTOCK, line, {"feedstock": data["feedstock"]}))
    elif (production.requested_quota or 0) > 0 and not production.feedstock.is_double_compte:
        errors.append(error(DoubleCountingError.NOT_DC_FEEDSTOCK, line, {"feedstock": production.feedstock.code}))

    if not data["biofuel"]:
        errors.append(error(DoubleCountingError.MISSING_BIOFUEL, line))
    elif not production.biofuel_id:
        errors.append(error(DoubleCountingError.UNKNOWN_BIOFUEL, line, {"biofuel": data["biofuel"]}))

    if production.feedstock_id and production.biofuel_id:
        incompatibilities = check_compatibility_feedstock_biofuel(production.feedstock, production.biofuel)
        meta = {"feedstock": production.feedstock.code, "biofuel": production.biofuel.code, "infos": incompatibilities}
        if len(incompatibilities) > 0:
            errors.append(error(DoubleCountingError.MP_BC_INCOHERENT, line, meta))

    # check that requested quotas aren't bigger than estimated production
    if (production.requested_quota or 0) > (production.estimated_production or 0):
        errors.append(error(DoubleCountingError.PRODUCTION_MISMATCH_QUOTA, line))

    return errors


# check rules that check sourcing and production
def check_dc_globally(
    sourcing: list[DoubleCountingSourcing],
    production: list[DoubleCountingProduction],
) -> List[DcError]:
    errors: List[DcError] = []

    errors += check_sourcing_vs_production(sourcing, production)
    errors += check_pome_excess(production)

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
        if not year in sourcing_by_year_by_feedstock:
            sourcing_by_year_by_feedstock[year] = {}
        if not feedstock in sourcing_by_year_by_feedstock[year]:
            sourcing_by_year_by_feedstock[year][feedstock] = 0
        sourcing_by_year_by_feedstock[year][feedstock] += s.metric_tonnes or 0

    # group production by year and feedstock and sum estimated production
    production_by_year_by_feedstock = {}
    for p in production:
        year = p.year
        feedstock = p.feedstock.code if p.feedstock else "UNKNOWN"
        if not year in production_by_year_by_feedstock:
            production_by_year_by_feedstock[year] = {}
        if not feedstock in production_by_year_by_feedstock[year]:
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


# check that biofuels made with POME (EFFLUENTS_HUILERIES_PALME_RAFLE) aren't produced for more than 2000 tonnes
def check_pome_excess(production: list[DoubleCountingProduction]) -> List[DcError]:
    errors: List[DcError] = []

    pome_production_by_year = {}
    for p in production:
        if p.feedstock.code != "EFFLUENTS_HUILERIES_PALME_RAFLE":
            continue
        if p.year not in pome_production_by_year:
            pome_production_by_year[p.year] = 0
        pome_production_by_year[p.year] += p.estimated_production or 0

    for year in pome_production_by_year:
        estimated_production = pome_production_by_year[year]
        if estimated_production > 2000:
            meta = {"year": year, "production": estimated_production}
            errors.append(error(DoubleCountingError.POME_GT_2000, meta=meta))

    return errors


# check if the biofuel can be made with the specified feedstock
def check_compatibility_feedstock_biofuel(feedstock: MatierePremiere, biofuel: Biocarburant) -> List[str]:
    errors: List[str] = []

    if biofuel.is_alcool and feedstock.compatible_alcool is False:
        errors.append("%s issu de fermentation et %s n'est pas fermentescible" % (biofuel.name, feedstock.name))

    if biofuel.is_graisse and feedstock.compatible_graisse is False:
        errors.append("Matière première (%s) incompatible avec Esthers Méthyliques" % (feedstock.name))

    if biofuel.is_graisse:
        if biofuel.code == "EMHU" and feedstock.code != "HUILE_ALIMENTAIRE_USAGEE":
            errors.append("%s doit être à base d'huiles alimentaires usagées" % (biofuel.name))

        if biofuel.code == "EMHV" and feedstock.code not in ["COLZA", "TOURNESOL", "SOJA", "HUILE_PALME"]:
            errors.append(
                "%s doit être à base de végétaux (Colza, Tournesol, Soja, Huile de Palme)" % (biofuel.name),
            )

        if biofuel.code == "EMHA" and feedstock.code not in [
            "HUILES_OU_GRAISSES_ANIMALES_CAT1_CAT2",
            "HUILES_OU_GRAISSES_ANIMALES_CAT3",
        ]:
            errors.append("%s doit être à base d'huiles ou graisses animales" % (biofuel.name))

    if feedstock.code in [
        "HUILES_OU_GRAISSES_ANIMALES_CAT1_CAT2",
        "HUILES_OU_GRAISSES_ANIMALES_CAT3",
    ] and biofuel.code not in ["EMHA", "HOE", "HOG", "HOC", "HCC", "HCG", "HCE", "B100"]:
        errors.append("Des huiles ou graisses animales ne peuvent donner que des EMHA ou HOG/HOE/HOC")

    if feedstock.code == "HUILE_ALIMENTAIRE_USAGEE" and biofuel.code not in [
        "EMHU",
        "HOE",
        "HOG",
        "HOC",
        "HCC",
        "HCG",
        "HCE",
    ]:
        errors.append("Des huiles alimentaires usagées ne peuvent donner que des EMHU ou HOG/HOE/HOC")

    if feedstock.code in [
        "MAIS",
        "BLE",
        "BETTERAVE",
        "CANNE_A_SUCRE",
        "RESIDUS_VINIQUES",
        "LIES_DE_VIN",
        "MARC_DE_RAISIN",
    ] and biofuel.code not in ["ETH", "ETBE", "ED95"]:
        errors.append(
            "Maïs, Blé, Betterave, Canne à Sucre ou Résidus Viniques ne peuvent créer que de l'Éthanol ou ETBE"
        )

    if not feedstock.is_huile_vegetale and biofuel.code in ["HVOE", "HVOG", "HVOC"]:
        errors.append(
            "Un HVO doit provenir d'huiles végétales uniquement. Pour les autres huiles hydrotraitées, voir la nomenclature HOE/HOG/HOC"
        )

    return errors
