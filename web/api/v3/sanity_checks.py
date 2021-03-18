import datetime
from django import db
from core.models import LotValidationError, LotV2Error, TransactionError

# init data cache
# MPS = {m.code: m for m in MatierePremiere.objects.all()}
# BCS = {b.code: b for b in Biocarburant.objects.all()}
# COUNTRIES = {p.code_pays: p for p in Pays.objects.all()}

# definitions

oct2015 = datetime.date(year=2015, month=10, day=5)
jan2021 = datetime.date(year=2021, month=1, day=1)

rules = {}
rules['GHG_REDUC_INF_50'] = "La réduction de gaz à effet de serre est inférieure à 50%, il n'est pas possible d'enregistrer ce lot dans CarbuRe"
rules['GHG_REDUC_SUP_100'] = "La réduction de gaz à effet de serre est supérieure à 100%"
rules['GHG_REDUC_SUP_99'] = "La réduction de gaz à effet de serre est supérieure à 99%"
rules['PROVENANCE_MP'] = "La provenance de la matière première est inhabituelle"
rules['MP_BC_INCOHERENT'] = "Matière Première incohérente avec le Biocarburant"
rules['GHG_REDUC_INF_60'] = "La réduction de gaz à effet de serre est inférieure à 60% pour une usine dont la date de mise en service est ultérieure au 5 Octobre 2015. Il n'est pas possible d'enregistrer ce lot dans CarbuRe"
rules['GHG_REDUC_INF_65'] = "La réduction de gaz à effet de serre est inférieure à 65% pour une usine dont la date de mise en service est ultérieure au 1er Janvier 2021. Il n'est pas possible d'enregistrer ce lot dans CarbuRe"
rules['MISSING_REF_DBL_COUNTING'] = "Numéro d'enregistrement Double Compte manquant"
rules['VOLUME_FAIBLE'] = "Volume inhabituellement faible."
rules['MAC_BC_WRONG'] = "Biocarburant incompatible avec un mise à consommation (seuls ED95 ou B100 sont autorisés)"
rules['GHG_ETD_0'] = "Émissions GES liées au Transport et à la Distribution nulles"
rules['GHG_EP_0'] = "Émissions GES liées à la Transformation de la matière première nulles"
rules['GHG_EEC_0'] = "Émissions GES liées à l'Extraction et la Culture nulles"
rules['MP_NOT_CONFIGURED'] = "Matière Première non enregistrée sur votre Site de Production"
rules['BC_NOT_CONFIGURED'] = "Biocarburant non enregistré sur votre Site de Production"
rules['MISSING_PRODSITE_CERTIFICATE'] = "Aucun certificat n'est associé à ce site de Production"
rules['UNKNOWN_CLIENT'] = "Le client n'est pas enregistré sur Carbure"
rules['UNKNOWN_CERTIFICATE'] = "Certificat fournisseur inconnu"
rules['NOT_ALLOWED'] = "Vous ne pouvez pas ajouter les lots d'un producteur inscrit sur CarbuRe"


def raise_warning(lot, rule_triggered, details='', tx=None, show_recipient=True):
    d = {'warning_to_user': True,
         'warning_to_recipient': show_recipient,
         'warning_to_admin': True,
         'block_validation': False,
         'message': rules[rule_triggered],
         'details': details,
         'lot': lot,
         'rule_triggered': rule_triggered,
         'tx': tx,
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


def bulk_sanity_checks(txs, prefetched_data, background=True):
    results = []
    errors = []
    if background == True:
        db.connections.close_all()
    #print('starting bulk_sanity_check %s' % (datetime.datetime.now()))
    # cleanup previous errors
    lots = [t.lot for t in txs]
    LotValidationError.objects.filter(lot__in=lots).delete()
    for tx in txs:
        lot_ok, tx_ok, is_sane, validation_errors = sanity_check(tx, prefetched_data)
        errors += validation_errors
        results.append((lot_ok, tx_ok, is_sane))
    LotValidationError.objects.bulk_create(errors, batch_size=1000)
    #print('finished bulk_sanity_check %s' % (datetime.datetime.now()))
    return results


def sanity_check(tx, prefetched_data):
    lot = tx.lot
    is_sane = True
    errors = []

    # make sure all mandatory fields are set
    tx_valid = tx_is_valid(tx)
    lot_valid = lot_is_valid(tx.lot)
    if not lot_valid or not tx_valid:
        # without mandatory fields, we cannot start analyzing for sanity errors. return immediately
        is_sane = False
        return lot_valid, tx_valid, is_sane, errors

    if tx.is_mac and lot.biocarburant and lot.biocarburant.code not in ['ED95', 'B100']:
        errors.append(raise_error(lot, 'MAC_BC_WRONG'))

    # check volume
    if lot.volume < 2000:
        errors.append(raise_warning(lot, 'VOLUME_FAIBLE'))

    # réduction de GES
    if lot.ghg_reduction >= 100:
        errors.append(raise_error(lot, 'GHG_REDUC_SUP_100', details="GES reduction %f%%" % (lot.ghg_reduction)))
    elif lot.ghg_reduction > 99:
        errors.append(raise_warning(lot, 'GHG_REDUC_SUP_99', details="GES reduction %f%%" % (lot.ghg_reduction)))
    elif lot.ghg_reduction < 50:
        is_sane = False
        errors.append(raise_error(lot, 'GHG_REDUC_INF_50', details="GES reduction %f%%" % (lot.ghg_reduction)))
    else:
        pass

    if lot.etd == 0:
        is_sane = False
        errors.append(raise_error(lot, 'GHG_ETD_0', details="GES Transport et Distribution nuls"))
    if lot.ep == 0:
        is_sane = False
        errors.append(raise_error(lot, 'GHG_EP_0', details="GES Transformation/Production"))

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
        if lot.matiere_premiere.category == 'CONV' and lot.eec == 0:
            errors.append(raise_warning(lot, 'GHG_EEC_0', details="GES Culture 0 pour MP conventionnelle (%s)" % (lot.matiere_premiere.name)))

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
            if not lot.pays_origine.is_in_europe and lot.pays_origine.code_pays not in ['US', 'UA']:
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
            errors.append(raise_error(lot, 'MP_BC_INCOHERENT', details="%s issu de fermentation et %s n'est pas fermentescible" % (lot.biocarburant.name, lot.matiere_premiere.name)))
        if lot.biocarburant.is_graisse and lot.matiere_premiere.compatible_graisse is False:
            is_sane = False
            errors.append(raise_error(lot, 'MP_BC_INCOHERENT', details="Matière première (%s) incompatible avec Esthers Méthyliques" % (lot.matiere_premiere.name)))

        # double comptage, cas specifiques
        if lot.matiere_premiere.is_double_compte:
            in_carbure_without_dc = lot.production_site_is_in_carbure and lot.carbure_production_site and not lot.carbure_production_site.dc_reference
            not_in_carbure_without_dc = not lot.production_site_is_in_carbure and not lot.unknown_production_site_dbl_counting
            if in_carbure_without_dc or not_in_carbure_without_dc:
                is_sane = False
                errors.append(raise_error(lot, 'MISSING_REF_DBL_COUNTING', details="%s de %s" % (lot.biocarburant.name, lot.matiere_premiere.name)))

        if lot.biocarburant.is_graisse:
            if lot.biocarburant.code == 'EMHU' and lot.matiere_premiere.code != 'HUILE_ALIMENTAIRE_USAGEE':
                is_sane = False
                errors.append(raise_error(lot, 'MP_BC_INCOHERENT', details="%s doit être à base d'huiles alimentaires usagées" % (lot.biocarburant.name)))
            if lot.biocarburant.code == 'EMHV' and lot.matiere_premiere.code not in ['COLZA', 'TOURNESOL', 'SOJA', 'HUILE_PALME']:
                is_sane = False
                errors.append(raise_error(lot, 'MP_BC_INCOHERENT',  details="%s doit être à base de végétaux (Colza, Tournesol, Soja, Huile de Palme)" % (lot.biocarburant.name)))
            if lot.biocarburant.code == 'EMHA' and lot.matiere_premiere.code not in ['HUILES_OU_GRAISSES_ANIMALES_CAT1_CAT2', 'HUILES_OU_GRAISSES_ANIMALES_CAT3']:
                is_sane = False
                errors.append(raise_error(lot, 'MP_BC_INCOHERENT', details="%s doit être à base d'huiles ou graisses animales" % (lot.biocarburant.name)))

        if lot.matiere_premiere.code in ['HUILES_OU_GRAISSES_ANIMALES_CAT1_CAT2', 'HUILES_OU_GRAISSES_ANIMALES_CAT3'] and lot.biocarburant.code not in ['EMHA', 'HOE', 'HOG']:
            is_sane = False
            errors.append(raise_error(lot, 'MP_BC_INCOHERENT', details="Des huiles ou graisses animales ne peuvent donner que des EMHA ou HOG/HOE"))
        if lot.matiere_premiere.code == 'HUILE_ALIMENTAIRE_USAGEE' and lot.biocarburant.code not in ['EMHU', 'HOE', 'HOG']:
            is_sane = False
            errors.append(raise_error(lot, 'MP_BC_INCOHERENT', details="Des huiles alimentaires usagées ne peuvent donner que des EMHU ou HOG/HOE"))

        if lot.matiere_premiere.code in ['MAIS', 'BLE', 'BETTERAVE', 'CANNE_A_SUCRE', 'RESIDUS_VINIQUES', 'LIES_DE_VIN', 'MARC_DE_RAISIN'] and lot.biocarburant.code not in ['ETH', 'ETBE', 'ED95']:
            is_sane = False
            errors.append(raise_error(lot, 'MP_BC_INCOHERENT', details="Maïs, Blé, Betterave, Canne à Sucre ou Résidus Viniques ne peuvent créer que de l'Éthanol ou ETBE"))

        if not lot.matiere_premiere.is_huile_vegetale and lot.biocarburant.code in ['HVOE', 'HVOG']:
            is_sane = False
            errors.append(raise_error(lot, 'MP_BC_INCOHERENT', details="Un HVO doit provenir d'huiles végétales uniquement. Pour les autres huiles hydrotraitées, voir la nomenclature HOE/HOG"))


    # configuration
    if lot.matiere_premiere and lot.carbure_production_site:
        if lot.carbure_production_site.name in prefetched_data['production_sites']:
            mps = [psi.matiere_premiere for psi in prefetched_data['production_sites'][lot.carbure_production_site.name].productionsiteinput_set.all()]
            if lot.matiere_premiere not in mps:
                errors.append(raise_warning(lot, 'MP_NOT_CONFIGURED', show_recipient=False))
    if lot.biocarburant and lot.carbure_production_site:
        if lot.carbure_production_site.name in prefetched_data['production_sites']:
            bcs = [pso.biocarburant for pso in prefetched_data['production_sites'][lot.carbure_production_site.name].productionsiteoutput_set.all()]
            if lot.biocarburant not in bcs:
                errors.append(raise_warning(lot, 'BC_NOT_CONFIGURED', show_recipient=False))

    if lot.carbure_production_site:
        # certificates
        certificates = lot.carbure_production_site.productionsitecertificate_set.all()
        if certificates.count() == 0:
            errors.append(raise_warning(lot, 'MISSING_PRODSITE_CERTIFICATE'))

    if not tx.client_is_in_carbure:
        errors.append(raise_warning(lot, 'UNKNOWN_CLIENT', tx=tx))

    # check certificate
    if not tx.lot.producer_is_in_carbure:
        # certificate association has not been checked manually by our admins. make sure the certificate exists
        certificate_id = tx.lot.unknown_production_site_reference.upper()
        if certificate_id not in prefetched_data['iscc_certificates'] and certificate_id not in prefetched_data['2bs_certificates']:
            errors.append(raise_warning(lot, 'UNKNOWN_CERTIFICATE'))


    # check rights
    if tx.lot.producer_is_in_carbure and tx.lot.added_by != tx.lot.carbure_producer:
        is_sane = False
        errors.append(raise_error(lot, 'NOT_ALLOWED'))
    return lot_valid, tx_valid, is_sane, errors


def lot_is_valid(lot):
    is_valid = True
    if not lot.volume:
        LotV2Error.objects.update_or_create(lot=lot, field='volume', value='', error='Veuillez renseigner le volume')
        is_valid = False

    if not lot.parent_lot:
        if not lot.biocarburant:
            error = 'Veuillez renseigner le type de biocarburant'
            LotV2Error.objects.update_or_create(lot=lot, field='biocarburant_code', value='', error=error)
            is_valid = False
        if not lot.matiere_premiere:
            error = 'Veuillez renseigner la matière première'
            LotV2Error.objects.update_or_create(lot=lot, field='matiere_premiere_code', value='', error=error)
            is_valid = False
        if lot.producer_is_in_carbure and lot.carbure_production_site is None:
            error = 'Site de production %s inconnu pour %s' % (lot.unknown_production_site, lot.carbure_producer.name)
            LotV2Error.objects.update_or_create(lot=lot, field='carbure_production_site', value='', error=error)
            is_valid = False
        if not lot.producer_is_in_carbure:
            if not lot.unknown_production_site_com_date:
                error = "Veuillez renseigner la date de mise en service de l'usine"
                LotV2Error.objects.update_or_create(lot=lot, field='unknown_production_site_com_date', defaults={'value':'', 'error':error})
                is_valid = False
            if not lot.unknown_production_site_reference: # and not lot.unknown_supplier_certificate:
                error = "Veuillez renseigner le certificat de l'usine de production ou du fournisseur"
                LotV2Error.objects.update_or_create(lot=lot, field='unknown_production_site_reference', defaults={'value':'', 'error':error})
                # LotV2Error.objects.update_or_create(lot=lot, field='unknown_supplier_certificate', defaults={'value':'', 'error':error})
                is_valid = False
        # else:
        #     if not lot.carbure_production_site_reference:
        #         error = "Veuillez renseigner le certificat de l'usine de production"
        #         LotV2Error.objects.update_or_create(lot=lot, field='carbure_production_site_reference', defaults={'value':'', 'error':error})
        #         is_valid = False
    return is_valid


def tx_is_valid(tx):
    is_valid = True
    today = datetime.date.today()

    # make sure all mandatory fields are set
    if not tx.dae:
        error = 'DAE manquant'
        TransactionError.objects.update_or_create(tx=tx, field='dae', value='', error=error)
        is_valid = False
    if not tx.delivery_site_is_in_carbure and not tx.unknown_delivery_site:
        error = 'Site de livraison manquant'
        TransactionError.objects.update_or_create(tx=tx, field='unknown_delivery_site', value='', error=error)
        is_valid = False
    if tx.delivery_site_is_in_carbure and not tx.carbure_delivery_site:
        error = 'Site de livraison manquant'
        TransactionError.objects.update_or_create(tx=tx, field='carbure_delivery_site', value='', error=error)
        is_valid = False
    if not tx.delivery_date or tx.delivery_date is None:
        error = 'Date de livraison manquante'
        TransactionError.objects.update_or_create(tx=tx, field='delivery_date', value='', error=error)
        is_valid = False
    else:
        if (tx.delivery_date - today) > datetime.timedelta(days=3650) or (tx.delivery_date - today) < datetime.timedelta(days=-3650):
            error = "Date incorrecte: veuillez entrer des données récentes (%s)" % (tx.delivery_date.strftime('%d/%m/%Y'))
            TransactionError.objects.update_or_create(tx=tx, field='delivery_date', value='', error=error)
            is_valid = False

    if tx.client_is_in_carbure and not tx.carbure_client:
        error = 'Veuillez renseigner un client'
        TransactionError.objects.update_or_create(tx=tx, field='carbure_client', value='', error=error)
        is_valid = False
    if not tx.client_is_in_carbure and not tx.unknown_client:
        error = 'Veuillez renseigner un client'
        TransactionError.objects.update_or_create(tx=tx, field='unknown_client', value='', error=error)
        is_valid = False

    if not tx.delivery_site_is_in_carbure and not tx.unknown_delivery_site:
        error = 'Veuillez renseigner un site de livraison'
        TransactionError.objects.update_or_create(tx=tx, field='unknown_delivery_site', value='', error=error)
        is_valid = False

    if not tx.delivery_site_is_in_carbure and not tx.unknown_delivery_site_country:
        error = 'Veuillez renseigner un pays de livraison'
        TransactionError.objects.update_or_create(tx=tx, field='unknown_delivery_site_country', value='', error=error)
        is_valid = False

    if tx.unknown_delivery_site_country is not None and tx.unknown_delivery_site_country.is_in_europe and tx.lot.pays_origine is None:
        error = "Veuillez renseigner le pays d'origine de la matière première - Marché européen"
        TransactionError.objects.update_or_create(tx=tx, field='unknown_delivery_site_country', value='', error=error)
        is_valid = False
    if tx.carbure_delivery_site is not None and tx.carbure_delivery_site.country.is_in_europe and tx.lot.pays_origine is None:
        error = "Veuillez renseigner le pays d'origine de la matière première - Marché européen"
        TransactionError.objects.update_or_create(tx=tx, field='carbure_delivery_site', value='', error=error)
        is_valid = False

    # if not tx.lot.producer_is_in_carbure and not tx.carbure_vendor_certificate:
    #     error = "Veuillez renseigner votre certificat de trading"
    #     TransactionError.objects.update_or_create(tx=tx, field='carbure_vendor_certificate', value='', error=error)
    #     is_valid = False

    return is_valid

