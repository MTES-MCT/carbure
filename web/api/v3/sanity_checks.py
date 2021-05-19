import datetime
from django import db
from core.models import GenericError, Entity

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
rules['NOT_ALLOWED'] = "Vous ne pouvez pas ajouter les lots d'un producteur inscrit sur CarbuRe"
rules['DEPRECATED_MP'] = "Les résidus viniques vont disparaître au profit de deux nouvelles matières premières: Marc de raisin et Lies de vin. Merci de mettre à jour vos déclarations en conséquence."


def generic_error(error, **kwargs):
    d = {
        'display_to_creator': True,
        'display_to_admin': True,
        'error': error,
    }
    d.update(kwargs)
    return GenericError(**d)


def bulk_sanity_checks(txs, prefetched_data, background=True):
    results = []
    errors = []
    if background == True:
        db.connections.close_all()
    # cleanup previous errors
    GenericError.objects.filter(tx__in=txs).delete()
    for tx in txs:
        lot_ok, tx_ok, is_sane, validation_errors = sanity_check(tx, prefetched_data)
        errors += validation_errors
        results.append((lot_ok, tx_ok, is_sane))
    GenericError.objects.bulk_create(errors, batch_size=1000)
    return results


def sanity_check(tx, prefetched_data):
    lot = tx.lot
    is_sane = True
    errors = []

    # make sure all mandatory fields are set
    tx_valid = tx_is_valid(tx, prefetched_data)
    lot_valid = lot_is_valid(tx)
    if not lot_valid or not tx_valid:
        # without mandatory fields, we cannot start analyzing for sanity errors. return immediately
        is_sane = False
        return lot_valid, tx_valid, is_sane, errors

    if tx.is_mac and lot.biocarburant and lot.biocarburant.code not in ['ED95', 'B100', 'ETH', 'EMHV', 'EMHU']:
        errors.append(generic_error(error='MAC_BC_WRONG', tx=tx, is_blocking=True))

    # check volume
    if lot.volume < 2000:
        errors.append(generic_error(error='VOLUME_FAIBLE', tx=tx))

    # réduction de GES
    if lot.ghg_reduction >= 100:
        errors.append(generic_error(error='GHG_REDUC_SUP_100', tx=tx))
    elif lot.ghg_reduction > 99:
        errors.append(generic_error(error='GHG_REDUC_SUP_99', tx=tx))
    elif lot.ghg_reduction < 50:
        is_sane = False
        errors.append(generic_error(error='GHG_REDUC_INF_50', tx=tx, is_blocking=True))
    else:
        pass

    if lot.etd == 0:
        is_sane = False
        errors.append(generic_error(error='GHG_ETD_0', tx=tx, is_blocking=True))
    if lot.ep == 0:
        is_sane = False
        errors.append(generic_error(error='GHG_EP_0', tx=tx, is_blocking=True))

    commissioning_date = lot.carbure_production_site.date_mise_en_service if lot.carbure_production_site else lot.unknown_production_site_com_date
    if commissioning_date and isinstance(commissioning_date, datetime.datetime) or isinstance(commissioning_date, datetime.date):
        if commissioning_date > oct2015 and lot.ghg_reduction < 60:
            is_sane = False
            errors.append(generic_error(error='GHG_REDUC_INF_60', tx=tx, is_blocking=True))
        if commissioning_date >= jan2021 and lot.ghg_reduction < 65:
            is_sane = False
            errors.append(generic_error(error='GHG_REDUC_INF_65', tx=tx, is_blocking=True))

    # provenance des matieres premieres
    if lot.matiere_premiere and lot.pays_origine:
        if lot.matiere_premiere.code == "RESIDUS_VINIQUES":
            errors.append(generic_error(error='DEPRECATED_MP', tx=tx))

        if lot.matiere_premiere.category == 'CONV' and lot.eec == 0:
            errors.append(generic_error(error='GHG_EEC_0', tx=tx, extra="GES Culture 0 pour MP conventionnelle (%s)" % (lot.matiere_premiere.name)))

        if lot.matiere_premiere.code == 'SOJA':
            if lot.pays_origine.code_pays not in ['US', 'AR', 'BR', 'UY', 'PY']:
                errors.append(generic_error(error='PROVENANCE_MP', tx=tx, extra="%s de %s" % (lot.matiere_premiere.name, lot.pays_origine.name)))
        elif lot.matiere_premiere.code == 'HUILE_PALME':
            if lot.pays_origine.code_pays not in ['ID', 'MY', 'HN']:
                errors.append(generic_error(error='PROVENANCE_MP', tx=tx, extra="%s de %s" % (lot.matiere_premiere.name, lot.pays_origine.name)))
        elif lot.matiere_premiere.code == 'COLZA':
            if lot.pays_origine.code_pays not in ['US', 'CA', 'AU', 'UA', 'CN', 'IN', 'DE', 'FR', 'PL', 'UK'] and not lot.pays_origine.is_in_europe:
                errors.append(generic_error(error='PROVENANCE_MP', tx=tx, extra="%s de %s" % (lot.matiere_premiere.name, lot.pays_origine.name)))
        elif lot.matiere_premiere.code == 'CANNE_A_SUCRE':
            if lot.pays_origine.code_pays not in ['BR', 'BO']:
                errors.append(generic_error(error='PROVENANCE_MP', tx=tx, extra="%s de %s" % (lot.matiere_premiere.name, lot.pays_origine.name)))
        elif lot.matiere_premiere.code == 'MAIS':
            if not lot.pays_origine.is_in_europe and lot.pays_origine.code_pays not in ['US', 'UA']:
                errors.append(generic_error(error='PROVENANCE_MP', tx=tx, extra="%s de %s" % (lot.matiere_premiere.name, lot.pays_origine.name)))
        elif lot.matiere_premiere.code == 'BETTERAVE':
            if not lot.pays_origine.is_in_europe:
                errors.append(generic_error(error='PROVENANCE_MP', tx=tx, extra="%s de %s" % (lot.matiere_premiere.name, lot.pays_origine.name)))
        else:
            pass

    if lot.biocarburant and lot.matiere_premiere:
        # consistence des matieres premieres avec biocarburant
        if lot.biocarburant.is_alcool and lot.matiere_premiere.compatible_alcool is False:
            is_sane = False
            errors.append(generic_error(error='MP_BC_INCOHERENT', tx=tx, is_blocking=True, extra="%s issu de fermentation et %s n'est pas fermentescible" % (lot.biocarburant.name, lot.matiere_premiere.name)))
        if lot.biocarburant.is_graisse and lot.matiere_premiere.compatible_graisse is False:
            is_sane = False
            errors.append(generic_error(error='MP_BC_INCOHERENT', tx=tx, is_blocking=True, extra="Matière première (%s) incompatible avec Esthers Méthyliques" % (lot.matiere_premiere.name)))

        # double comptage, cas specifiques
        if lot.matiere_premiere.is_double_compte:
            in_carbure_without_dc = lot.production_site_is_in_carbure and lot.carbure_production_site and not lot.carbure_production_site.dc_reference
            not_in_carbure_without_dc = not lot.production_site_is_in_carbure and not lot.unknown_production_site_dbl_counting
            if in_carbure_without_dc or not_in_carbure_without_dc:
                is_sane = False
                errors.append(generic_error(error='MISSING_REF_DBL_COUNTING', tx=tx, is_blocking=True, extra="%s de %s" % (lot.biocarburant.name, lot.matiere_premiere.name)))

        if lot.biocarburant.is_graisse:
            if lot.biocarburant.code == 'EMHU' and lot.matiere_premiere.code != 'HUILE_ALIMENTAIRE_USAGEE':
                is_sane = False
                errors.append(generic_error(error='MP_BC_INCOHERENT', tx=tx, is_blocking=True, extra="%s doit être à base d'huiles alimentaires usagées" % (lot.biocarburant.name)))
            if lot.biocarburant.code == 'EMHV' and lot.matiere_premiere.code not in ['COLZA', 'TOURNESOL', 'SOJA', 'HUILE_PALME']:
                is_sane = False
                errors.append(generic_error(error='MP_BC_INCOHERENT',  tx=tx, is_blocking=True, extra="%s doit être à base de végétaux (Colza, Tournesol, Soja, Huile de Palme)" % (lot.biocarburant.name)))
            if lot.biocarburant.code == 'EMHA' and lot.matiere_premiere.code not in ['HUILES_OU_GRAISSES_ANIMALES_CAT1_CAT2', 'HUILES_OU_GRAISSES_ANIMALES_CAT3']:
                is_sane = False
                errors.append(generic_error(error='MP_BC_INCOHERENT', tx=tx, is_blocking=True, extra="%s doit être à base d'huiles ou graisses animales" % (lot.biocarburant.name)))

        if lot.matiere_premiere.code in ['HUILES_OU_GRAISSES_ANIMALES_CAT1_CAT2', 'HUILES_OU_GRAISSES_ANIMALES_CAT3'] and lot.biocarburant.code not in ['EMHA', 'HOE', 'HOG']:
            is_sane = False
            errors.append(generic_error(error='MP_BC_INCOHERENT', tx=tx, is_blocking=True, extra="Des huiles ou graisses animales ne peuvent donner que des EMHA ou HOG/HOE"))
        if lot.matiere_premiere.code == 'HUILE_ALIMENTAIRE_USAGEE' and lot.biocarburant.code not in ['EMHU', 'HOE', 'HOG']:
            is_sane = False
            errors.append(generic_error(error='MP_BC_INCOHERENT', tx=tx, is_blocking=True, extra="Des huiles alimentaires usagées ne peuvent donner que des EMHU ou HOG/HOE"))

        if lot.matiere_premiere.code in ['MAIS', 'BLE', 'BETTERAVE', 'CANNE_A_SUCRE', 'RESIDUS_VINIQUES', 'LIES_DE_VIN', 'MARC_DE_RAISIN'] and lot.biocarburant.code not in ['ETH', 'ETBE', 'ED95']:
            is_sane = False
            errors.append(generic_error(error='MP_BC_INCOHERENT', tx=tx, is_blocking=True, extra="Maïs, Blé, Betterave, Canne à Sucre ou Résidus Viniques ne peuvent créer que de l'Éthanol ou ETBE"))

        if not lot.matiere_premiere.is_huile_vegetale and lot.biocarburant.code in ['HVOE', 'HVOG']:
            is_sane = False
            errors.append(generic_error(error='MP_BC_INCOHERENT', tx=tx, is_blocking=True, extra="Un HVO doit provenir d'huiles végétales uniquement. Pour les autres huiles hydrotraitées, voir la nomenclature HOE/HOG"))


    # configuration
    if lot.matiere_premiere and lot.carbure_production_site:
        if lot.carbure_production_site.name in prefetched_data['production_sites']:
            mps = [psi.matiere_premiere for psi in prefetched_data['production_sites'][lot.carbure_production_site.name].productionsiteinput_set.all()]
            if lot.matiere_premiere not in mps:
                errors.append(generic_error(error='MP_NOT_CONFIGURED', tx=tx, display_to_recipient=False))
    if lot.biocarburant and lot.carbure_production_site:
        if lot.carbure_production_site.name in prefetched_data['production_sites']:
            bcs = [pso.biocarburant for pso in prefetched_data['production_sites'][lot.carbure_production_site.name].productionsiteoutput_set.all()]
            if lot.biocarburant not in bcs:
                errors.append(generic_error(error='BC_NOT_CONFIGURED', tx=tx, display_to_recipient=False))

    if lot.carbure_production_site:
        # certificates
        certificates = lot.carbure_production_site.productionsitecertificate_set.all()
        if certificates.count() == 0:
            errors.append(generic_error(error='MISSING_PRODSITE_CERTIFICATE', tx=tx))

    if not tx.client_is_in_carbure and not tx.is_mac:
        errors.append(generic_error(error='UNKNOWN_CLIENT', tx=tx, display_to_recipient=False))

    if tx.lot.producer_is_in_carbure and tx.lot.added_by != tx.lot.carbure_producer and not tx.lot.parent_lot:
        is_sane = False
        errors.append(generic_error(error='NOT_ALLOWED', tx=tx, is_blocking=True))
    return lot_valid, tx_valid, is_sane, errors


def lot_is_valid(tx):
    lot = tx.lot
    is_valid = True
    errors = []
    if not lot.volume:
        errors.append(generic_error(error='MISSING_VOLUME', tx=tx, field='volume', extra='Veuillez renseigner le volume', is_blocking=True))
        is_valid = False

    if not lot.parent_lot:
        if not lot.biocarburant:
            errors.append(generic_error(error='MISSING_BIOFUEL', tx=tx, field='biocarburant_code', extra='Veuillez renseigner le type de biocarburant', is_blocking=True))
            is_valid = False
        if not lot.matiere_premiere:
            errors.append(generic_error(error='MISSING_FEEDSTOCK', tx=tx, field='matiere_premiere_code', extra='Veuillez renseigner la matière première', is_blocking=True))
            is_valid = False
        if lot.producer_is_in_carbure and lot.carbure_production_site is None:
            extra = 'Site de production %s inconnu pour %s' % (lot.unknown_production_site, lot.carbure_producer.name)
            errors.append(generic_error(error='UNKNOWN_PRODUCTION_SITE', tx=tx, field='carbure_production_site', extra=extra, is_blocking=True))
            is_valid = False
        if not lot.production_site_is_in_carbure:
            if not lot.unknown_production_site_com_date:
                extra = "Veuillez renseigner la date de mise en service de l'usine"
                errors.append(generic_error(error='MISSING_PRODUCTION_SITE_COMDATE', tx=tx, field='unknown_production_site_com_date', extra=extra, is_blocking=True))
                is_valid = False
    if len(errors):
        GenericError.objects.bulk_create(errors)
    return is_valid


def tx_is_valid(tx, prefetched_data):
    is_valid = True
    today = datetime.date.today()
    errors = []

    # make sure all mandatory fields are set
    if not tx.dae:
        extra = 'DAE manquant'
        errors.append(generic_error(error='MISSING_DAE', tx=tx, field='dae', extra=extra))
        is_valid = False
    if not tx.is_mac:
        if not tx.delivery_site_is_in_carbure and not tx.unknown_delivery_site:
            extra = 'Site de livraison manquant'
            errors.append(generic_error(error='MISSING_UNKNOWN_DELIVERY_SITE', tx=tx, field='unknown_delivery_site', extra=extra, is_blocking=True))
            is_valid = False
        if tx.delivery_site_is_in_carbure and not tx.carbure_delivery_site:
            extra = 'Site de livraison manquant'
            errors.append(generic_error(error='MISSING_CARBURE_DELIVERY_SITE', tx=tx, field='carbure_delivery_site', extra=extra, is_blocking=True))
            is_valid = False
    if not tx.delivery_date or tx.delivery_date is None:
        extra = 'Date de livraison manquante'
        errors.append(generic_error(error='MISSING_DELIVERY_DATE', tx=tx, field='delivery_date', extra=extra, is_blocking=True))
        is_valid = False
    else:
        if (tx.delivery_date - today) > datetime.timedelta(days=3650) or (tx.delivery_date - today) < datetime.timedelta(days=-3650):
            extra = "Date incorrecte [%s]" % (tx.delivery_date.strftime('%d/%m/%Y'))
            errors.append(generic_error(error='WRONG_DELIVERY_DATE', tx=tx, field='delivery_date', extra=extra, is_blocking=True))
            is_valid = False

    if tx.client_is_in_carbure and not tx.carbure_client:
        extra = 'Veuillez renseigner un client'
        errors.append(generic_error(error='MISSING_CARBURE_CLIENT', tx=tx, field='carbure_client', extra=extra, is_blocking=True))
        is_valid = False
    if not tx.client_is_in_carbure and not tx.unknown_client:
        extra = 'Veuillez renseigner un client'
        errors.append(generic_error(error='MISSING_UNKNOWN_CLIENT', tx=tx, field='unknown_client', extra=extra, is_blocking=True))
        is_valid = False

    if not tx.delivery_site_is_in_carbure and not tx.unknown_delivery_site and not tx.is_mac:
        extra = 'Veuillez renseigner un site de livraison'
        errors.append(generic_error(error='MISSING_UNKNOWN_DELIVERY_SITE', tx=tx, field='unknown_delivery_site', extra=extra, is_blocking=True))
        is_valid = False

    if not tx.delivery_site_is_in_carbure and not tx.unknown_delivery_site_country and not tx.is_mac:
        extra = 'Veuillez renseigner un pays de livraison'
        errors.append(generic_error(error='MISSING_UNKNOWN_DELIVERY_SITE_COUNTRY', tx=tx, field='unknown_delivery_site_country', extra=extra, is_blocking=True))
        is_valid = False

    if tx.unknown_delivery_site_country and tx.unknown_delivery_site_country.is_in_europe and tx.lot.pays_origine is None:
        extra = "Veuillez renseigner le pays d'origine de la matière première - Marché européen"
        errors.append(generic_error(error='MISSING_FEEDSTOCK_COUNTRY_OF_ORIGIN', tx=tx, field='pays_origine_code', extra=extra, is_blocking=True))
        is_valid = False
    if tx.carbure_delivery_site and tx.carbure_delivery_site.country.is_in_europe and tx.lot.pays_origine is None:
        extra = "Veuillez renseigner le pays d'origine de la matière première - Marché européen"
        errors.append(generic_error(error='MISSING_FEEDSTOCK_COUNTRY_OF_ORIGIN', tx=tx, field='pays_origine_code', extra=extra, is_blocking=True))
        is_valid = False

    if tx.carbure_client and tx.carbure_client.entity_type == Entity.OPERATOR:
        # client is an operator
        # make sure we have a certificate
        if not tx.carbure_vendor_certificate and not tx.lot.unknown_supplier_certificate:
            # if I am an operator, I am the one who uploaded the file. request the certificate in excel file
            if tx.lot.added_by.entity_type == Entity.OPERATOR:
                extra = "Veuillez renseigner le certificat du fournisseur"
                errors.append(generic_error(error='MISSING_SUPPLIER_CERTIFICATE', tx=tx, field='unknown_supplier_certificate', extra=extra, is_blocking=True))
                is_valid = False
            else:
                # I am a producer or trader
                # I need to either set the certificate in the file or add them in my account
                extra = "Veuillez renseigner votre certificat de fournisseur ou ajouter un certificat sur votre compte"
                errors.append(generic_error(error='MISSING_SUPPLIER_CERTIFICATE', tx=tx, field='carbure_vendor_certificate', extra=extra, is_blocking=True))
                is_valid = False
    if len(errors):
        GenericError.objects.bulk_create(errors)
    return is_valid

