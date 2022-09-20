from django.db.models import Sum
from doublecount.models import DoubleCountingProduction, DoubleCountingSourcing


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


def error(type, line=None, meta={}, is_blocking=True):
    return {
        "error": type,
        "line_number": line,
        "is_blocking": is_blocking,
        "meta": meta,
    }


# check a line in the sourcing section of an imported dc excel file
def check_sourcing_line(sourcing, data, line):
    errors = []

    if not data.feedstock:
        errors.append(error(DoubleCountingError.MISSING_FEEDSTOCK, line))
    elif not sourcing.feedstock_id:
        errors.append(error(DoubleCountingError.UNKNOWN_FEEDSTOCK, line, {"feedstock": data.feedstock}))

    return errors


# check a line in the production section of an imported dc excel file
def check_production_line(production, data, line):
    errors = []

    if not data.feedstock:
        errors.append(error(DoubleCountingError.MISSING_FEEDSTOCK, line))
    elif not production.feedstock_id:
        errors.append(error(DoubleCountingError.UNKNOWN_FEEDSTOCK, line, {"feedstock": data.feedstock}))
    elif (production.requested_quota or 0) > 0 and not production.feedstock.is_double_compte:
        errors.append(error(DoubleCountingError.NOT_DC_FEEDSTOCK, line, {"feedstock": production.feedstock.code}))

    if not data.biofuel:
        errors.append(error(DoubleCountingError.MISSING_BIOFUEL, line))
    elif not production.biofuel_id:
        errors.append(error(DoubleCountingError.UNKNOWN_BIOFUEL, line, {"biofuel": data.biofuel}))

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
def check_dc_globally(dca):
    errors = []

    sourcing = DoubleCountingSourcing.objects.filter(dca_id=dca.id)
    production = DoubleCountingProduction.objects.filter(dca_id=dca.id)

    errors += check_sourcing_vs_production(sourcing, production)
    errors += check_pome_excess(production)

    return errors


# check that sourcing feedstock quantities match production biofuel quantities
def check_sourcing_vs_production(sourcing, production):
    errors = []

    # group sourcing by feedstock and year, and sum the total quantity
    sourcing_per_feedstock = (
        sourcing.select_related("feedstock").values("feedstock__code", "year").annotate(quantity=Sum("metric_tonnes"))
    )

    # group production by feedstock and year, and sum the total quantity
    production_per_feedstock = (
        production.select_related("feedstock")
        .values("feedstock__code", "year")
        .annotate(quantity=Sum("estimated_production"))
    )

    for p in production_per_feedstock:
        try:
            # check that the sourced amount of feedstock roughly matches the total production generated with this feedstock
            s = sourcing_per_feedstock.get(feedstock__code=p["feedstock__code"], year=p["year"])
            if p["quantity"] > s["quantity"]:
                meta = {"feedstock": p["feedstock__code"], "sourcing": s["quantity"], "production": p["quantity"]}
                errors.append(error(DoubleCountingError.PRODUCTION_MISMATCH_SOURCING, meta=meta))
        except:
            meta = {"feedstock": p["feedstock__code"], "sourcing": 0, "production": p["quantity"]}
            errors.append(error(DoubleCountingError.PRODUCTION_MISMATCH_SOURCING, meta=meta))

    return errors


# check that biofuels made with POME (EFFLUENTS_HUILERIES_PALME_RAFLE) aren't produced for more than 2000 tonnes
def check_pome_excess(production):
    errors = []

    pome_production_per_year = (
        production.select_related("feedstock")
        .filter(feedstock__code="EFFLUENTS_HUILERIES_PALME_RAFLE")
        .values("year")
        .annotate(quantity=Sum("estimated_production"))
    )

    for p in pome_production_per_year:
        if p["quantity"] > 2000:
            meta = {"year": p["year"], "production": p["quantity"]}
            errors.append(error(DoubleCountingError.POME_GT_2000, meta=meta))

    return errors


# check if the biofuel can be made with the specified feedstock
def check_compatibility_feedstock_biofuel(feedstock, biofuel):
    errors = []

    if biofuel.is_alcool and feedstock.compatible_alcool is False:
        errors.append(("%s issu de fermentation et %s n'est pas fermentescible" % (biofuel.name, feedstock.name),))

    if biofuel.is_graisse and feedstock.compatible_graisse is False:
        errors.append(("Matière première (%s) incompatible avec Esthers Méthyliques" % (feedstock.name),))

    if biofuel.is_graisse:
        if biofuel.code == "EMHU" and feedstock.code != "HUILE_ALIMENTAIRE_USAGEE":
            errors.append(("%s doit être à base d'huiles alimentaires usagées" % (biofuel.name),))

        if biofuel.code == "EMHV" and feedstock.code not in ["COLZA", "TOURNESOL", "SOJA", "HUILE_PALME"]:
            errors.append(
                ("%s doit être à base de végétaux (Colza, Tournesol, Soja, Huile de Palme)" % (biofuel.name),)
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
        errors.append(("Des huiles ou graisses animales ne peuvent donner que des EMHA ou HOG/HOE/HOC",))

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
