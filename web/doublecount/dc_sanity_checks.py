from doublecount.models import DoubleCountingProduction, DoubleCountingSourcing


class DoubleCountingError:
    NOT_DC_FEEDSTOCK = "NOT_DC_FEEDSTOCK"
    PRODUCTION_MISMATCH_SUPPLY = "PRODUCTION_MISMATCH_SUPPLY"
    POME_GT_2000 = "POME_GT_2000"
    PRODUCTION_MISMATCH_QUOTA = "PRODUCTION_MISMATCH_QUOTA"
    MP_BC_INCOHERENT = "MP_BC_INCOHERENT"
    UNKNOWN_FEEDSTOCK = "UNKNOWN_FEEDSTOCK"
    UNKNOWN_BIOFUEL = "UNKNOWN_BIOFUEL"
    MISSING_FEEDSTOCK = "MISSING_FEEDSTOCK"
    MISSING_BIOFUEL = "MISSING_BIOFUEL"


# S’assurer que la matière première est bien dans la liste des matières premières pouvant être double-comptées
# S’assurer de la cohérence entre approvisionnement et production (en tonne)
# Assurer que la production éstimée de biocarburants à partir de POME (EFFLUENTS_HUILERIES_PALME_RAFLE) ne soit pas supérieur à 2000 tonnes par usine de production PAR AN "
# S'assurer la cohérence entre le quota demandé et la production (en tonne)
# S’assurer que le code matière première est bien reconnue
# S’assurer que le biocarburant est bien reconnu
# S’assurer de la cohérence Biocarburant ⇔ matière première
# Le biocarburant est manquant
# S’assurer que le biocarburant est bien dans la liste des biocarburant fait à partir de matières premières pouvant être double comptées


def dc_sanity_check(dca):
    sourcing = DoubleCountingSourcing.objects.filter(dca_id=dca.id)
    production = DoubleCountingProduction.objects.filter(dca_id=dca.id)


def check_sourcing_line(sourcing, data, line):
    errors = []

    if not data.feedstock:
        errors.append(
            {
                "error": DoubleCountingError.MISSING_FEEDSTOCK,
                "is_blocking": True,
                "line_number": line,
            }
        )
    elif not sourcing.feedstock_id:
        errors.append(
            {
                "error": DoubleCountingError.UNKNOWN_FEEDSTOCK,
                "is_blocking": True,
                "line_number": line,
                "meta": {"feedstock": data.feedstock},
            }
        )
    elif not sourcing.feedstock.is_double_compte:
        errors.append(
            {
                "error": DoubleCountingError.NOT_DC_FEEDSTOCK,
                "is_blocking": False,
                "line_number": line,
                "meta": {"feedstock": sourcing.feedstock.code},
            }
        )

    return errors


def check_production_line(production, data, line):
    errors = []

    if not data.feedstock:
        errors.append(
            {
                "error": DoubleCountingError.MISSING_FEEDSTOCK,
                "is_blocking": True,
                "line_number": line,
            }
        )
    elif not production.feedstock_id:
        errors.append(
            {
                "error": DoubleCountingError.UNKNOWN_FEEDSTOCK,
                "is_blocking": True,
                "line_number": line,
                "meta": {"feedstock": data.feedstock},
            }
        )
    elif (production.requested_quota or 0) > 0 and not production.feedstock.is_double_compte:
        errors.append(
            {
                "error": DoubleCountingError.NOT_DC_FEEDSTOCK,
                "is_blocking": True,
                "line_number": line,
                "meta": {"feedstock": production.feedstock.code},
            }
        )

    if not data.biofuel:
        errors.append(
            {
                "error": DoubleCountingError.MISSING_BIOFUEL,
                "is_blocking": True,
                "line_number": line,
            }
        )
    elif not production.biofuel_id:
        errors.append(
            {
                "error": DoubleCountingError.UNKNOWN_BIOFUEL,
                "is_blocking": True,
                "line_number": line,
                "meta": {"biofuel": data.biofuel},
            }
        )

    return errors
