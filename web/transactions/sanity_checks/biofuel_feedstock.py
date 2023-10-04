from core.carburetypes import CarbureSanityCheckErrors
from core.models import Biocarburant, CarbureLot, MatierePremiere, Pays
from .helpers import generic_error


def check_deprecated_mp(lot: CarbureLot):
    if lot.feedstock and lot.feedstock.code == "RESIDUS_VINIQUES":
        return generic_error(
            error=CarbureSanityCheckErrors.DEPRECATED_MP,
            lot=lot,
            field="feedstock",
        )


def check_mp_bc_incoherent(lot: CarbureLot):
    if not lot.biofuel or not lot.feedstock:
        return

    for error in get_biofuel_feedstock_incompatibilities(lot.biofuel, lot.feedstock):
        yield generic_error(
            error=CarbureSanityCheckErrors.MP_BC_INCOHERENT,
            lot=lot,
            is_blocking=True,
            extra=error,
            fields=["biofuel", "feedstock"],
        )


def check_provenance_mp(lot: CarbureLot):
    if not lot.feedstock or not lot.country_of_origin:
        return

    for error in get_feedstock_origin_incompatibilities(lot.feedstock, lot.country_of_origin):
        yield generic_error(
            error=CarbureSanityCheckErrors.PROVENANCE_MP,
            lot=lot,
            extra=error,
            fields=["feedstock", "country_of_origin"],
        )


def get_biofuel_feedstock_incompatibilities(biofuel: Biocarburant, feedstock: MatierePremiere):
    if biofuel.is_alcool and not feedstock.compatible_alcool:
        yield f"{biofuel} issu de fermentation et {feedstock} n'est pas fermentescible"

    if biofuel.is_graisse and feedstock.compatible_graisse is False:
        yield f"Matière première {feedstock} incompatible avec {biofuel}"

    if biofuel.code == "EMHU" and feedstock.code != "HUILE_ALIMENTAIRE_USAGEE":
        yield f"{biofuel} doit être à base d'huiles alimentaires usagées"

    if biofuel.code == "EEHU" and feedstock.code != "HUILE_ALIMENTAIRE_USAGEE":
        yield f"{biofuel} doit être à base d'huiles alimentaires usagées"

    emhv_feedstocks = ("COLZA", "TOURNESOL", "SOJA", "HUILE_PALME", "CARINATA")
    if biofuel.code == "EMHV" and feedstock.code not in emhv_feedstocks:
        yield f"{biofuel} doit être à base de végétaux (Colza, Tournesol, Soja, Huile de Palme)"

    if biofuel.code == "EEHV" and feedstock.code not in emhv_feedstocks:
        yield f"{biofuel} doit être à base de végétaux (Colza, Tournesol, Soja, Huile de Palme)"

    emha_feedstocks = ("HUILES_OU_GRAISSES_ANIMALES_CAT1_CAT2", "HUILES_OU_GRAISSES_ANIMALES_CAT3")
    if biofuel.code == "EMHA" and feedstock.code not in emha_feedstocks:
        yield f"{biofuel} doit être à base d'huiles ou graisses animales"

    if biofuel.code == "EEHA" and feedstock.code not in emha_feedstocks:
        yield f"{biofuel} doit être à base d'huiles ou graisses animales"

    fat_biofuels = ("EMHA", "HOE", "HOG", "HOC", "HCC", "HCG", "HCE", "B100")
    fat_feedstocks = ("HUILES_OU_GRAISSES_ANIMALES_CAT1_CAT2", "HUILES_OU_GRAISSES_ANIMALES_CAT3")
    if feedstock.code in fat_feedstocks and biofuel.code not in fat_biofuels:
        yield "Des huiles ou graisses animales ne peuvent donner que des EMHA, B100 ou HOG/HOE/HOC"

    sugar_feedstocks = ("MAIS", "BLE", "BETTERAVE", "CANNE_A_SUCRE", "RESIDUS_VINIQUES", "LIES_DE_VIN", "MARC_DE_RAISIN")
    sugar_biofuels = ("ETH", "ETBE", "ED95")
    if feedstock.code in sugar_feedstocks and biofuel.code not in sugar_biofuels:
        yield "Maïs, Blé, Betterave, Canne à Sucre ou Résidus Viniques ne peuvent créer que de l'Éthanol ou ETBE"

    hvo_biofuels = ("HVOE", "HVOG", "HVOC")
    if biofuel.code in hvo_biofuels and not feedstock.is_huile_vegetale:
        yield "Un HVO doit provenir d'huiles végétales uniquement. Pour les autres huiles hydrotraitées, voir la nomenclature HOE/HOG/HOC"

    hc_biofuels = ("HCE", "HCG", "HCC")
    hc_feedstocks = (
        "COLZA",
        "TOURNESOL",
        "SOJA",
        "HUILE_PALME",
        "CARINATA",
        "EFFLUENTS_HUILERIES_PALME_RAFLE",
        "HUILE_ALIMENTAIRE_USAGEE",
        "HUILES_OU_GRAISSES_ANIMALES_CAT1_CAT2",
        "HUILES_OU_GRAISSES_ANIMALES_CAT3",
    )
    if biofuel.code in hc_biofuels and feedstock.code not in hc_feedstocks:
        yield "Une huile Co-traitées doit provenir d'huiles végétales, d'huiles usagées ou de graisses animales uniquement."


def get_feedstock_origin_incompatibilities(feedstock: MatierePremiere, country: Pays):
    soja_countries = ("US", "AR", "BR", "UY", "PY")
    if feedstock.code == "SOJA" and country.code_pays not in soja_countries:
        yield f"{feedstock} de {country}"

    palm_countries = ("ID", "MY", "HN")
    if feedstock.code == "HUILE_PALME" and country.code_pays not in palm_countries:
        yield f"{feedstock} de {country}"

    colza_countries = ("US", "CA", "AU", "UA", "CN", "IN", "DE", "FR", "PL", "UK")
    if feedstock.code == "COLZA" and not country.is_in_europe and country.code_pays not in colza_countries:
        yield f"{feedstock} de {country}"

    sugarcane_countries = ("BO", "BR", "CR", "GT", "PE")
    if feedstock.code == "CANNE_A_SUCRE" and country.code_pays not in sugarcane_countries:
        yield f"{feedstock} de {country}"

    mais_countries = ("US", "UA", "CA", "BR", "PY", "AR")
    if feedstock.code == "MAIS" and not country.is_in_europe and country.code_pays not in mais_countries:
        yield f"{feedstock} de {country}"

    if feedstock.code == "BETTERAVE" and not country.is_in_europe:
        yield f"{feedstock} de {country}"
