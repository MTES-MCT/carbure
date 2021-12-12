import datetime
from inspect import trace
import re
import traceback
from django import db
from core.models import CarbureLot, GenericError, Entity
# definitions

oct2015 = datetime.date(year=2015, month=10, day=5)
jan2021 = datetime.date(year=2021, month=1, day=1)
july1st2021 = datetime.date(year=2021, month=7, day=1)
future = datetime.date.today() + datetime.timedelta(days=15) # docker containers are restarted everyday - not an issue
dae_pattern = re.compile('^([a-zA-Z0-9/]+$)')

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
rules['GHG_EL_NEG'] = "Émissions GES liées à l'Affectation des terres Négatives"
rules['MP_NOT_CONFIGURED'] = "Matière Première non enregistrée sur votre Site de Production"
rules['BC_NOT_CONFIGURED'] = "Biocarburant non enregistré sur votre Site de Production"
rules['DEPOT_NOT_CONFIGURED'] = "Ce site de livraison n'est pas rattaché à votre société"
rules['MISSING_PRODSITE_CERTIFICATE'] = "Aucun certificat n'est associé à ce site de Production"
rules['UNKNOWN_CLIENT'] = "Le client n'est pas enregistré sur Carbure"
rules['UNKNOWN_DELIVERY_SITE'] = "Livraison en France - Dépôt Inconnu"
rules['NOT_ALLOWED'] = "Vous ne pouvez pas ajouter les lots d'un producteur inscrit sur CarbuRe"
rules['DEPRECATED_MP'] = "Les résidus viniques vont disparaître au profit de deux nouvelles matières premières: Marc de raisin et Lies de vin. Merci de mettre à jour vos déclarations en conséquence."

rules['NO_PRODSITE_CERT'] = "Certificat du site de production absent"
rules['UNKNOWN_PRODSITE_CERT'] = "Certificat de site de production inconnu"
rules['EXPIRED_PRODSITE_CERT'] = "Certificat du site de production expiré"
rules['NO_SUPPLIER_CERT'] = "Certificat du fournisseur original absent"
rules['UNKNOWN_SUPPLIER_CERT'] = "Certificat de fournisseur inconnu"
rules['EXPIRED_SUPPLIER_CERT'] = "Certificat du fournisseur expiré"
rules['NO_VENDOR_CERT'] = "Certificat du fournisseur absent"
rules['UNKNOWN_VENDOR_CERT'] = "Certificat inconnu"
rules['EXPIRED_VENDOR_CERT'] = "Certificat du fournisseur expiré"
rules['UNKNOWN_DAE_FORMAT'] = "Le format du numéro douanier semble incorrect"
rules['UNKNOWN_DOUBLE_COUNTING_CERTIFICATE'] = "Le certificat double compte est inconnu"
rules['EXPIRED_DOUBLE_COUNTING_CERTIFICATE'] = "Le certificat double n'est plus valide"
rules['POTENTIAL_DUPLICATE'] = "Doublon potentiel détecté. Un autre lot avec le même numéro douanier, biocarburant, matière première, volume et caractéristiques GES existe."


def generic_error(error, **kwargs):
    d = {
        'display_to_creator': True,
        'display_to_admin': True,
        'error': error,
    }
    d.update(kwargs)
    return GenericError(**d)


def bulk_sanity_checks(lots, prefetched_data, background=True):
    results = []
    errors = []
    if background == True:
        db.connections.close_all()
    # cleanup previous errors
    lot_ids = [l.id for l in lots]
    GenericError.objects.filter(lot_id__in=lot_ids).delete()
    for lot in lots:
        try:
            is_sane, sanity_errors = sanity_check(lot, prefetched_data)
            errors += sanity_errors
            results.append(is_sane)
        except:
            traceback.print_exc()
    GenericError.objects.bulk_create(errors, batch_size=1000)
    return results


def check_certificates(prefetched_data, lot, errors):
    # PRODUCTION SITE CERTIFICATES
    if not lot.production_site_certificate:
        errors.append(generic_error(error='NO_PRODSITE_CERT', lot=lot, field='production_site_certificate'))
    else:
        cert = lot.production_site_certificate
        if cert not in prefetched_data['certificates']:
            errors.append(generic_error(error='UNKNOWN_PRODSITE_CERT', lot=lot, field='production_site_certificate'))
        else:
            # certificate is set and exists. is it valid?
            c = prefetched_data['certificates'][cert]
            if c.valid_until < lot.delivery_date:
                 errors.append(generic_error(error='EXPIRED_PRODSITE_CERT', lot=lot, field='production_site_certificate'))

    # SUPPLIER CERT
    if not lot.supplier_certificate:
        errors.append(generic_error(error='NO_SUPPLIER_CERT', lot=lot, field='supplier_certificate'))
    else:
        cert = lot.supplier_certificate
        if cert not in prefetched_data['certificates']:
            errors.append(generic_error(error='UNKNOWN_SUPPLIER_CERT', lot=lot, field='supplier_certificate'))
        else:
            # certificate is set and exists. is it valid?
            c = prefetched_data['certificates'][cert]
            if c.valid_until < lot.delivery_date:
                 errors.append(generic_error(error='EXPIRED_SUPPLIER_CERT', lot=lot, field='supplier_certificate'))

    # DOUBLE COUNTING CERTIFICATES
    if lot.feedstock and lot.feedstock.is_double_compte:
        # identify where the certificate is (attached to prod site or attached to lot)
        dc_cert = lot.production_site_double_counting_certificate
        if not dc_cert:
            errors.append(generic_error(error='MISSING_REF_DBL_COUNTING', lot=lot, field='dc_reference'))
        else:
            if dc_cert not in prefetched_data['double_counting_certificates']:
                errors.append(generic_error(error='UNKNOWN_DOUBLE_COUNTING_CERTIFICATE', lot=lot, field='dc_reference'))
            else:
                dcc = prefetched_data['double_counting_certificates'][dc_cert]
                if dcc.valid_until < lot.delivery_date:
                    errors.append(generic_error(error='EXPIRED_DOUBLE_COUNTING_CERTIFICATE', lot=lot))
    return errors

def sanity_check(lot, prefetched_data):
    is_sane = True
    errors = []

    # make sure all mandatory fields are set
    valid, reqfielderrors = sanity_check_mandatory_fields(lot)
    if not valid:
        is_sane = False
        errors += reqfielderrors
        return is_sane, errors

    if lot.delivery_type == CarbureLot.RFC and lot.biofuel.code not in ['ED95', 'B100', 'ETH', 'EMHV', 'EMHU']:
        errors.append(generic_error(error='MAC_BC_WRONG', lot=lot, is_blocking=True, fields=['biofuel', 'delivery_type']))

    # check volume
    if lot.volume < 2000 and lot.delivery_type not in [CarbureLot.RFC, CarbureLot.FLUSHED]:
        errors.append(generic_error(error='VOLUME_FAIBLE', lot=lot, field='volume'))

    # réduction de GES
    if lot.delivery_date >= july1st2021:
        # RED II
        if lot.ghg_reduction_red_ii >= 100:
            errors.append(generic_error(error='GHG_REDUC_SUP_100', lot=lot))
        elif lot.ghg_reduction_red_ii > 99:
            errors.append(generic_error(error='GHG_REDUC_SUP_99', lot=lot))
        elif lot.ghg_reduction_red_ii < 50:
            is_sane = False
            errors.append(generic_error(error='GHG_REDUC_INF_50', lot=lot, is_blocking=True))
        else:
            # all good
            pass
    else:
        if lot.ghg_reduction >= 100:
            errors.append(generic_error(error='GHG_REDUC_SUP_100', lot=lot))
        elif lot.ghg_reduction > 99:
            errors.append(generic_error(error='GHG_REDUC_SUP_99', lot=lot))
        elif lot.ghg_reduction < 50:
            is_sane = False
            errors.append(generic_error(error='GHG_REDUC_INF_50', lot=lot, is_blocking=True))
        else:
            # all good
            pass

    if lot.etd <= 0:
        is_sane = False
        errors.append(generic_error(error='GHG_ETD_0', lot=lot, is_blocking=True, field='etd'))
    if lot.ep <= 0:
        is_sane = False
        errors.append(generic_error(error='GHG_EP_0', lot=lot, is_blocking=True, field='ep'))
    if lot.el < 0:
        errors.append(generic_error(error='GHG_EL_NEG', lot=lot, field='el'))

    commissioning_date = lot.production_site_commissioning_date
    if commissioning_date and isinstance(commissioning_date, datetime.datetime) or isinstance(commissioning_date, datetime.date):
        if commissioning_date > oct2015 and lot.ghg_reduction < 60:
            is_sane = False
            errors.append(generic_error(error='GHG_REDUC_INF_60', lot=lot, is_blocking=True))
        if commissioning_date >= jan2021 and lot.ghg_reduction < 65:
            is_sane = False
            errors.append(generic_error(error='GHG_REDUC_INF_65', lot=lot, is_blocking=True))

    # provenance des matieres premieres
    if lot.feedstock and lot.country_of_origin:
        if lot.feedstock.code == "RESIDUS_VINIQUES":
            errors.append(generic_error(error='DEPRECATED_MP', lot=lot, field='feedstock'))

        if lot.feedstock.category == 'CONV' and lot.eec == 0:
            errors.append(generic_error(error='GHG_EEC_0', lot=lot, extra="GES Culture 0 pour MP conventionnelle (%s)" % (lot.feedstock.name), field='eec'))

        if lot.feedstock.code == 'SOJA':
            if lot.country_of_origin.code_pays not in ['US', 'AR', 'BR', 'UY', 'PY']:
                errors.append(generic_error(error='PROVENANCE_MP', lot=lot, extra="%s de %s" % (lot.feedstock.name, lot.country_of_origin.name), field='country_of_origin'))
        elif lot.feedstock.code == 'HUILE_PALME':
            if lot.country_of_origin.code_pays not in ['ID', 'MY', 'HN']:
                errors.append(generic_error(error='PROVENANCE_MP', lot=lot, extra="%s de %s" % (lot.feedstock.name, lot.country_of_origin.name), field='country_of_origin'))
        elif lot.feedstock.code == 'COLZA':
            if lot.country_of_origin.code_pays not in ['US', 'CA', 'AU', 'UA', 'CN', 'IN', 'DE', 'FR', 'PL', 'UK'] and not lot.country_of_origin.is_in_europe:
                errors.append(generic_error(error='PROVENANCE_MP', lot=lot, extra="%s de %s" % (lot.feedstock.name, lot.country_of_origin.name), field='country_of_origin'))
        elif lot.feedstock.code == 'CANNE_A_SUCRE':
            if lot.country_of_origin.code_pays not in ['BR', 'BO']:
                errors.append(generic_error(error='PROVENANCE_MP', lot=lot, extra="%s de %s" % (lot.feedstock.name, lot.country_of_origin.name), field='country_of_origin'))
        elif lot.feedstock.code == 'MAIS':
            if not lot.country_of_origin.is_in_europe and lot.country_of_origin.code_pays not in ['US', 'UA']:
                errors.append(generic_error(error='PROVENANCE_MP', lot=lot, extra="%s de %s" % (lot.feedstock.name, lot.country_of_origin.name), field='country_of_origin'))
        elif lot.feedstock.code == 'BETTERAVE':
            if not lot.country_of_origin.is_in_europe:
                errors.append(generic_error(error='PROVENANCE_MP', lot=lot, extra="%s de %s" % (lot.feedstock.name, lot.country_of_origin.name), field='country_of_origin'))
        else:
            pass

    if lot.biofuel and lot.feedstock:
        # consistence des matieres premieres avec biocarburant
        if lot.biofuel.is_alcool and lot.feedstock.compatible_alcool is False:
            is_sane = False
            errors.append(generic_error(error='MP_BC_INCOHERENT', lot=lot, is_blocking=True, extra="%s issu de fermentation et %s n'est pas fermentescible" % (lot.biofuel.name, lot.feedstock.name), fields=['biofuel_code', 'feedstock_code']))
        if lot.biofuel.is_graisse and lot.feedstock.compatible_graisse is False:
            is_sane = False
            errors.append(generic_error(error='MP_BC_INCOHERENT', lot=lot, is_blocking=True, extra="Matière première (%s) incompatible avec Esthers Méthyliques" % (lot.feedstock.name), fields=['biofuel_code', 'feedstock_code']))

        # double comptage, cas specifiques
        if lot.feedstock.is_double_compte:
            in_carbure_without_dc = lot.carbure_production_site and not lot.carbure_production_site.dc_reference
            not_in_carbure_without_dc = lot.unknown_production_site and not lot.unknown_production_site_dbl_counting
            if in_carbure_without_dc or not_in_carbure_without_dc:
                is_sane = False
                errors.append(generic_error(error='MISSING_REF_DBL_COUNTING', lot=lot, is_blocking=True, extra="%s de %s" % (lot.biofuel.name, lot.feedstock.name), field='production_site_dbl_counting'))

        if lot.biofuel.is_graisse:
            if lot.biofuel.code == 'EMHU' and lot.feedstock.code != 'HUILE_ALIMENTAIRE_USAGEE':
                is_sane = False
                errors.append(generic_error(error='MP_BC_INCOHERENT', lot=lot, is_blocking=True, extra="%s doit être à base d'huiles alimentaires usagées" % (lot.biofuel.name), fields=['biofuel_code', 'feedstock_code']))
            if lot.biofuel.code == 'EMHV' and lot.feedstock.code not in ['COLZA', 'TOURNESOL', 'SOJA', 'HUILE_PALME']:
                is_sane = False
                errors.append(generic_error(error='MP_BC_INCOHERENT',  lot=lot, is_blocking=True, extra="%s doit être à base de végétaux (Colza, Tournesol, Soja, Huile de Palme)" % (lot.biofuel.name), fields=['biofuel_code', 'feedstock_code']))
            if lot.biofuel.code == 'EMHA' and lot.feedstock.code not in ['HUILES_OU_GRAISSES_ANIMALES_CAT1_CAT2', 'HUILES_OU_GRAISSES_ANIMALES_CAT3']:
                is_sane = False
                errors.append(generic_error(error='MP_BC_INCOHERENT', lot=lot, is_blocking=True, extra="%s doit être à base d'huiles ou graisses animales" % (lot.biofuel.name), fields=['biofuel_code', 'feedstock_code']))

        if lot.feedstock.code in ['HUILES_OU_GRAISSES_ANIMALES_CAT1_CAT2', 'HUILES_OU_GRAISSES_ANIMALES_CAT3'] and lot.biofuel.code not in ['EMHA', 'HOE', 'HOG']:
            is_sane = False
            errors.append(generic_error(error='MP_BC_INCOHERENT', lot=lot, is_blocking=True, extra="Des huiles ou graisses animales ne peuvent donner que des EMHA ou HOG/HOE", fields=['biofuel_code', 'feedstock_code']))
        if lot.feedstock.code == 'HUILE_ALIMENTAIRE_USAGEE' and lot.biofuel.code not in ['EMHU', 'HOE', 'HOG']:
            is_sane = False
            errors.append(generic_error(error='MP_BC_INCOHERENT', lot=lot, is_blocking=True, extra="Des huiles alimentaires usagées ne peuvent donner que des EMHU ou HOG/HOE", fields=['biofuel_code', 'feedstock_code']))

        if lot.feedstock.code in ['MAIS', 'BLE', 'BETTERAVE', 'CANNE_A_SUCRE', 'RESIDUS_VINIQUES', 'LIES_DE_VIN', 'MARC_DE_RAISIN'] and lot.biofuel.code not in ['ETH', 'ETBE', 'ED95']:
            is_sane = False
            errors.append(generic_error(error='MP_BC_INCOHERENT', lot=lot, is_blocking=True, extra="Maïs, Blé, Betterave, Canne à Sucre ou Résidus Viniques ne peuvent créer que de l'Éthanol ou ETBE", fields=['biofuel_code', 'feedstock_code']))

        if not lot.feedstock.is_huile_vegetale and lot.biofuel.code in ['HVOE', 'HVOG']:
            is_sane = False
            errors.append(generic_error(error='MP_BC_INCOHERENT', lot=lot, is_blocking=True, extra="Un HVO doit provenir d'huiles végétales uniquement. Pour les autres huiles hydrotraitées, voir la nomenclature HOE/HOG", fields=['biofuel_code', 'feedstock_code']))

    # configuration
    if lot.feedstock and lot.carbure_production_site:
        if lot.carbure_production_site.name in prefetched_data['my_production_sites']:
            mps = [psi.matiere_premiere for psi in prefetched_data['my_production_sites'][lot.carbure_production_site.name].productionsiteinput_set.all()]
            if lot.feedstock not in mps:
                errors.append(generic_error(error='MP_NOT_CONFIGURED', lot=lot, display_to_recipient=False, field='feedstock_code'))
    if lot.biofuel and lot.carbure_production_site:
        if lot.carbure_production_site.name in prefetched_data['my_production_sites']:
            bcs = [pso.biocarburant for pso in prefetched_data['my_production_sites'][lot.carbure_production_site.name].productionsiteoutput_set.all()]
            if lot.biofuel not in bcs:
                errors.append(generic_error(error='BC_NOT_CONFIGURED', lot=lot, display_to_recipient=False, field='biofuel_code'))
    if lot.carbure_client:
        if lot.carbure_client.id not in prefetched_data['depotsbyentity']:
            # not a single delivery sites linked to entity
            errors.append(generic_error(error='DEPOT_NOT_CONFIGURED', lot=lot, display_to_recipient=True, display_to_creator=False, field='delivery_site'))
        else:
            # some delivery sites linked to entity
            if lot.carbure_delivery_site.id not in prefetched_data['depotsbyentity'][lot.carbure_client.id]:
                # this specific delivery site is not linked
                errors.append(generic_error(error='DEPOT_NOT_CONFIGURED', lot=lot, display_to_recipient=True, display_to_creator=False, field='delivery_site'))
    # CERTIFICATES CHECK
    check_certificates(prefetched_data, lot, errors)
    if lot.delivery_date > future:
        is_sane = False
        errors.append(GenericError(lot=lot, field='delivery_date', error="DELIVERY_IN_THE_FUTURE", extra="La date de livraison est dans le futur", value=lot.delivery_date, display_to_creator=True, is_blocking=True))
    return is_sane, errors


def sanity_check_mandatory_fields(lot):
    is_valid = True
    today = datetime.date.today()
    errors = []

    if not lot.volume:
        errors.append(generic_error(error='MISSING_VOLUME', lot=lot, field='volume', is_blocking=True))
        is_valid = False
    if not lot.biofuel:
        errors.append(generic_error(error='MISSING_BIOFUEL', lot=lot, field='biofuel_code', is_blocking=True))
        is_valid = False
    if not lot.feedstock:
        errors.append(generic_error(error='MISSING_FEEDSTOCK', lot=lot, field='feedstock_code', is_blocking=True))
        is_valid = False
    if lot.carbure_producer and lot.carbure_production_site is None:
        errors.append(generic_error(error='UNKNOWN_PRODUCTION_SITE', lot=lot, field='carbure_production_site', is_blocking=True))
        is_valid = False
    if not lot.carbure_production_site and not lot.production_site_commissioning_date:
        errors.append(generic_error(error='MISSING_PRODUCTION_SITE_COMDATE', lot=lot, field='production_site_commissioning_date', is_blocking=True))
        is_valid = False

    if lot.delivery_type not in [CarbureLot.RFC, CarbureLot.FLUSHED] and lot.transport_document_reference is None:
        errors.append(generic_error(error='MISSING TRANSPORT DOCUMENT REFERENCE', lot=lot, field='transport_document_reference', is_blocking=True))
        is_valid = False
    if lot.delivery_type in [CarbureLot.BLENDING, CarbureLot.TRADING, CarbureLot.STOCK, CarbureLot.DIRECT]:
        # we need to know the Depot
        if not lot.carbure_delivery_site:
            errors.append(generic_error(error='MISSING_CARBURE_DELIVERY_SITE', lot=lot, field='carbure_delivery_site', is_blocking=True))
            is_valid = False
        # and we need to know the client
        if not lot.carbure_client:
            errors.append(generic_error(error='MISSING_CARBURE_CLIENT', lot=lot, field='carbure_client', is_blocking=True))
            is_valid = False
    if not lot.delivery_date:
        errors.append(generic_error(error='MISSING_DELIVERY_DATE', lot=lot, field='delivery_date', is_blocking=True))
        is_valid = False
    if (lot.delivery_date - today) > datetime.timedelta(days=3650) or (lot.delivery_date - today) < datetime.timedelta(days=-3650):
        errors.append(generic_error(error='WRONG_DELIVERY_DATE', lot=lot, field='delivery_date', is_blocking=True))
        is_valid = False

    if not lot.delivery_site_country:
        errors.append(generic_error(error='MISSING_DELIVERY_SITE_COUNTRY', lot=lot, field='delivery_site_country', is_blocking=True))
        is_valid = False
    if lot.delivery_site_country.is_in_europe and not lot.country_of_origin:
        errors.append(generic_error(error='MISSING_FEEDSTOCK_COUNTRY_OF_ORIGIN', lot=lot, field='country_of_origin', is_blocking=True))
        is_valid = False

    if lot.carbure_client and lot.carbure_client.entity_type == Entity.OPERATOR:
        # client is an operator
        # make sure we have a certificate
        if not lot.supplier_certificate:
            errors.append(generic_error(error='MISSING_SUPPLIER_CERTIFICATE', lot=lot, field='supplier_certificate', is_blocking=True))
            is_valid = False
    if len(errors):
        GenericError.objects.bulk_create(errors)
    return is_valid, errors

