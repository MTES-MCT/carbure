import datetime
from django import db
from core.models import LotValidationError

# init data cache
# MPS = {m.code: m for m in MatierePremiere.objects.all()}
# BCS = {b.code: b for b in Biocarburant.objects.all()}
# COUNTRIES = {p.code_pays: p for p in Pays.objects.all()}

# definitions

oct2015 = datetime.date(year=2015, month=10, day=5)
jan2021 = datetime.date(year=2021, month=1, day=1)

rules = {}
rules['GHG_REDUC_INF_50'] = "La réduction de gaz à effet de serre est inférieure à 50%, il n'est pas possible d'enregistrer ce lot dans CarbuRe"
rules['GHG_REDUC_SUP_100'] = "La réduction de gaz à effet de serre est supérieure à 100%, il n'est pas possible d'enregistrer ce lot dans CarbuRe"
rules['GHG_REDUC_SUP_99'] = "La réduction de gaz à effet de serre est supérieure à 99%"
rules['PROVENANCE_MP'] = "La provenance de la matière première est inhabituelle"
rules['MP_BC_INCOHERENT'] = "Matière Première incohérente avec le Biocarburant"
rules['GHG_REDUC_INF_60'] = "La réduction de gaz à effet de serre est inférieure à 60% pour une usine dont la date de mise en service est ultérieure au 5 Octobre 2015. Il n'est pas possible d'enregistrer ce lot dans CarbuRe"
rules['GHG_REDUC_INF_65'] = "La réduction de gaz à effet de serre est inférieure à 65% pour une usine dont la date de mise en service est ultérieure au 1er Janvier 2021. Il n'est pas possible d'enregistrer ce lot dans CarbuRe"
rules['MISSING_REF_DBL_COUNTING'] = "Numéro d'enregistrement Double Compte manquant"
rules['VOLUME_FAIBLE'] = "Volume inhabituellement faible."
rules['MAC_BC_WRONG'] = "Biocarburant incompatible avec un mise à consommation (seuls ED95 ou B100 sont autorisés)"


def raise_warning(lot, rule_triggered, details=''):
    d = {'warning_to_user': True,
         'warning_to_admin': True,
         'block_validation': False,
         'message': rules[rule_triggered],
         'details': details,
         'lot': lot,
         'rule_triggered': rule_triggered,
         }
    return LotValidationError(**d)


def raise_error(lot, rule_triggered, details=''):
    d = {'warning_to_user': True,
         'warning_to_admin': True,
         'block_validation': True,
         'message': rules[rule_triggered],
         'details': details,
         'lot': lot,
         'rule_triggered': rule_triggered,
         }
    return LotValidationError(**d)


def bulk_sanity_checks(txs, background=True):
    results = []
    errors = []
    if background == True:
        db.connections.close_all()
    print('starting bulk_sanity_check %s' % (datetime.datetime.now()))
    # cleanup previous errors
    lots = [t.lot for t in txs]
    LotValidationError.objects.filter(lot__in=lots).delete()
    for tx in txs:
        is_sane, validation_errors = sanity_check(tx)
        errors += validation_errors
        results.append(is_sane)
    LotValidationError.objects.bulk_create(errors, batch_size=1000)
    print('finished bulk_sanity_check %s' % (datetime.datetime.now()))
    return results


def sanity_check(tx):
    lot = tx.lot
    is_sane = True
    errors = []

    if tx.is_mac and lot.biocarburant and lot.biocarburant.code not in ['ED95', 'B100']:
        errors.append(raise_error(lot, 'MAC_BC_WRONG'))

    # check volume
    if lot.volume < 2000:
        errors.append(raise_warning(lot, 'VOLUME_FAIBLE'))

    # réduction de GES
    if lot.ghg_reduction > 100:
        is_sane = False
        errors.append(raise_error(lot, 'GHG_REDUC_SUP_100', details="GES reduction %f%%" % (lot.ghg_reduction)))
    if lot.ghg_reduction > 99:
        errors.append(raise_warning(lot, 'GHG_REDUC_SUP_99', details="GES reduction %f%%" % (lot.ghg_reduction)))
    if lot.ghg_reduction < 50:
        is_sane = False
        errors.append(raise_error(lot, 'GHG_REDUC_INF_50', details="GES reduction %f%%" % (lot.ghg_reduction)))

    commissioning_date = lot.carbure_production_site.date_mise_en_service if lot.carbure_production_site else lot.unknown_production_site_com_date
    if commissioning_date and isinstance(commissioning_date, datetime.datetime) or isinstance(commissioning_date, datetime.date):
        if commissioning_date > oct2015 and lot.ghg_reduction < 60:
            is_sane = False
            errors.append(raise_error(lot, 'GHG_REDUC_INF_60', details="GES reduction %f%%" % (lot.ghg_reduction)))
        if commissioning_date >= jan2021 and lot.ghg_reduction < 65:
            is_sane = False
            errors.append(raise_error(lot, 'GHG_REDUC_INF_65', details="GES reduction %f%%" % (lot.ghg_reduction)))

    # provenance des matieres premieres
    if lot.matiere_premiere and lot.pays_origine:
        if lot.matiere_premiere.code == 'SOJA':
            if lot.pays_origine.code_pays not in ['US', 'AR', 'BR', 'UY', 'PY']:
                errors.append(raise_warning(lot, 'PROVENANCE_MP', details="%s de %s" % (lot.matiere_premiere.name, lot.pays_origine.name)))
        elif lot.matiere_premiere.code == 'HUILE_PALME':
            if lot.pays_origine.code_pays not in ['ID', 'MY', 'HN']:
                errors.append(raise_warning(lot, 'PROVENANCE_MP', details="%s de %s" % (lot.matiere_premiere.name, lot.pays_origine.name)))
        elif lot.matiere_premiere.code == 'COLZA':
            if lot.pays_origine.code_pays not in ['US', 'CA', 'AU', 'UA', 'CN', 'IN', 'DE', 'FR', 'PL', 'UK'] and not lot.pays_origine.is_in_europe:
                errors.append(raise_warning(lot, 'PROVENANCE_MP', details="%s de %s" % (lot.matiere_premiere.name, lot.pays_origine.name)))
        elif lot.matiere_premiere.code == 'CANNE_A_SUCRE':
            if lot.pays_origine.code_pays not in ['BR', 'BO']:
                errors.append(raise_warning(lot, 'PROVENANCE_MP', details="%s de %s" % (lot.matiere_premiere.name, lot.pays_origine.name)))
        elif lot.matiere_premiere.code == 'MAIS':
            if not lot.pays_origine.is_in_europe and lot.pays_origine.code_pays != 'US':
                errors.append(raise_warning(lot, 'PROVENANCE_MP', details="%s de %s" % (lot.matiere_premiere.name, lot.pays_origine.name)))
        elif lot.matiere_premiere.code == 'BETTERAVE':
            if not lot.pays_origine.is_in_europe:
                errors.append(raise_warning(lot, 'PROVENANCE_MP', details="%s de %s" % (lot.matiere_premiere.name, lot.pays_origine.name)))
        else:
            pass

    if lot.biocarburant and lot.matiere_premiere:
        # consistence des matieres premieres avec biocarburant
        if lot.biocarburant.is_alcool and lot.matiere_premiere.compatible_alcool is False:
            is_sane = False
            errors.append(raise_error(lot, 'MP_BC_INCOHERENT', details="%s de %s" % (lot.biocarburant.name, lot.matiere_premiere.name)))
        if lot.biocarburant.is_graisse and lot.matiere_premiere.compatible_graisse is False:
            is_sane = False
            errors.append(raise_error(lot, 'MP_BC_INCOHERENT', details="%s de %s" % (lot.biocarburant.name, lot.matiere_premiere.name)))

        # double comptage, cas specifiques
        if lot.matiere_premiere.is_double_compte:
            if lot.unknown_production_site_dbl_counting is None or (lot.carbure_production_site and not lot.carbure_production_site.dc_reference):
                is_sane = False
                errors.append(raise_error(lot, 'MISSING_REF_DBL_COUNTING', details="%s de %s" % (lot.biocarburant.name, lot.matiere_premiere.name)))

        if lot.biocarburant.code in ['ETH'] and lot.matiere_premiere.code in ['RESIDUS_VINIQUES']:
            if lot.unknown_production_site_dbl_counting is None or (lot.carbure_production_site and not lot.carbure_production_site.dc_reference):
                is_sane = False
                errors.append(raise_error(lot, 'MISSING_REF_DBL_COUNTING', details="%s de %s" % (lot.biocarburant.name, lot.matiere_premiere.name)))

        if lot.biocarburant.is_graisse:
            if lot.biocarburant.code == 'EMHU' and lot.matiere_premiere.code != 'HUILE_ALIMENTAIRE_USAGEE':
                is_sane = False
                errors.append(raise_error(lot, 'MP_BC_INCOHERENT', details="%s de %s" % (lot.biocarburant.name, lot.matiere_premiere.name)))
            if lot.biocarburant.code == 'EMHV' and lot.matiere_premiere.code not in ['COLZA', 'TOURNESOL', 'SOJA', 'HUILE_PALME', 'EFFLUENTS_HUILERIES_PALME_RAFLE']:
                is_sane = False
                errors.append(raise_error(lot, 'MP_BC_INCOHERENT',  details="%s de %s" % (lot.biocarburant.name, lot.matiere_premiere.name)))
            if lot.biocarburant.code == 'EMHA' and lot.matiere_premiere.code not in ['HUILES_OU_GRAISSES_ANIMALES_CAT1_CAT2', 'HUILES_OU_GRAISSES_ANIMALES_CAT3']:
                is_sane = False
                errors.append(raise_error(lot, 'MP_BC_INCOHERENT', details="%s de %s" % (lot.biocarburant.name, lot.matiere_premiere.name)))

        if lot.matiere_premiere.code in ['HUILES_OU_GRAISSES_ANIMALES_CAT1_CAT2', 'HUILES_OU_GRAISSES_ANIMALES_CAT3'] and lot.biocarburant.code not in ['EMHA', 'HOE', 'HOG']:
            is_sane = False
            errors.append(raise_error(lot, 'MP_BC_INCOHERENT', details="%s de %s" % (lot.biocarburant.name, lot.matiere_premiere.name)))
        if lot.matiere_premiere.code == 'HUILE_ALIMENTAIRE_USAGEE' and lot.biocarburant.code not in ['EMHU', 'HOE', 'HOG']:
            is_sane = False
            errors.append(raise_error(lot, 'MP_BC_INCOHERENT', details="%s de %s" % (lot.biocarburant.name, lot.matiere_premiere.name)))

        if lot.matiere_premiere.code in ['MAIS', 'BLE', 'BETTERAVE', 'CANNE_A_SUCRE', 'RESIDUS_VINIQUES'] and lot.biocarburant.code not in ['ETH', 'ETBE']:
            is_sane = False
            errors.append(raise_error(lot, 'MP_BC_INCOHERENT', details="%s de %s" % (lot.biocarburant.name, lot.matiere_premiere.name)))

        if not lot.matiere_premiere.is_huile_vegetale and lot.biocarburant.code in ['HVOE', 'HVOG']:
            is_sane = False
            errors.append(raise_error(lot, 'MP_BC_INCOHERENT', details="%s de %s" % (lot.biocarburant.name, lot.matiere_premiere.name)))
    return is_sane, errors
