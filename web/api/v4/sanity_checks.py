import datetime
from email.policy import default
from inspect import trace
from multiprocessing.dummy import Process
import re
import traceback
from django import db
from api.v4.helpers import get_prefetched_data
from core.models import CarbureLot, CarbureLotReliabilityScore, GenericError, Entity
from core.carburetypes import (
    CarbureCertificatesErrors,
    CarbureMLGHGErrors,
    CarbureSanityCheckErrors,
)
from django.db import transaction
from transactions.helpers import check_locked_year

# definitions

oct2015 = datetime.date(year=2015, month=10, day=5)
jan2021 = datetime.date(year=2021, month=1, day=1)
july1st2021 = datetime.date(year=2021, month=7, day=1)
dae_pattern = re.compile("^([a-zA-Z0-9/]+$)")


def generic_error(error, **kwargs):
    d = {
        "display_to_creator": True,
        "display_to_admin": True,
        "display_to_auditor": True,
        "error": error,
    }
    d.update(kwargs)
    return GenericError(**d)


def bulk_sanity_checks(lots, prefetched_data=None, dry_run=False):
    if not prefetched_data:
        prefetched_data = get_prefetched_data()

    results = []
    errors = []

    # cleanup previous errors
    if not dry_run:
        lot_ids = [l.id for l in lots]
        GenericError.objects.filter(lot_id__in=lot_ids).delete()

    for lot in lots:
        try:
            is_sane, sanity_errors = sanity_check(lot, prefetched_data)
            errors += sanity_errors
            results.append(is_sane)
        except:
            traceback.print_exc()

    if not dry_run:
        GenericError.objects.bulk_create(errors, batch_size=1000)

    return errors, results


def bulk_scoring(lots, prefetched_data=None):
    if not prefetched_data:
        prefetched_data = get_prefetched_data()
    # delete scoring entries for the lots
    lotids = [l.id for l in lots]
    CarbureLotReliabilityScore.objects.filter(lot_id__in=lotids).delete()
    # recalc score
    clrs = []
    # bulk update lots
    with transaction.atomic():
        for l in lots:
            clrs_entries = l.recalc_reliability_score(prefetched_data)
            clrs += clrs_entries
        CarbureLot.objects.bulk_update(lots, ["data_reliability_score"])
        CarbureLotReliabilityScore.objects.bulk_create(clrs)


def check_ghg_values(prefetched_data, lot, errors):
    etd = prefetched_data["etd"]
    eec = prefetched_data["eec"]
    ep = prefetched_data["ep"]

    #### Machine Learning Stats check
    if lot.feedstock in etd:
        default_value = etd[lot.feedstock]
        if lot.etd > 2 * default_value and lot.etd > 5:
            errors.append(
                generic_error(
                    error=CarbureMLGHGErrors.ETD_ANORMAL_HIGH,
                    lot=lot,
                    display_to_creator=False,
                )
            )
        if lot.country_of_origin:
            if not lot.country_of_origin.is_in_europe and lot.etd < default_value:
                errors.append(
                    generic_error(
                        error=CarbureMLGHGErrors.ETD_NO_EU_TOO_LOW,
                        lot=lot,
                        display_to_creator=False,
                    )
                )
            if lot.country_of_origin.is_in_europe and lot.etd == default_value:
                errors.append(
                    generic_error(
                        error=CarbureMLGHGErrors.ETD_EU_DEFAULT_VALUE,
                        lot=lot,
                        display_to_creator=False,
                    )
                )
    if lot.feedstock and lot.country_of_origin:
        key = lot.feedstock.code + lot.country_of_origin.code_pays
        if key in eec:
            entry = eec[key]
            if lot.eec < 0.8 * min(entry.default_value, entry.average):
                errors.append(
                    generic_error(
                        error=CarbureMLGHGErrors.EEC_ANORMAL_LOW,
                        lot=lot,
                        display_to_creator=False,
                    )
                )
            if lot.eec > 1.2 * max(entry.default_value, entry.average):
                errors.append(
                    generic_error(
                        error=CarbureMLGHGErrors.EEC_ANORMAL_HIGH,
                        lot=lot,
                        display_to_creator=False,
                    )
                )
    if lot.feedstock and lot.biofuel:
        key = lot.feedstock.code + lot.biofuel.code
        if key in ep:
            entry = ep[key]
            if lot.ep < 0.8 * entry.average:
                errors.append(
                    generic_error(
                        error=CarbureMLGHGErrors.EP_ANORMAL_LOW,
                        lot=lot,
                        display_to_creator=False,
                    )
                )
            if lot.ep > 1.2 * entry.default_value_max_ep:
                errors.append(
                    generic_error(
                        error=CarbureMLGHGErrors.EP_ANORMAL_HIGH,
                        lot=lot,
                        display_to_creator=False,
                    )
                )

    #### Absolute values check
    if lot.delivery_date >= july1st2021:
        # RED II
        if lot.ghg_reduction_red_ii >= 100:
            errors.append(generic_error(error=CarbureSanityCheckErrors.GHG_REDUC_SUP_100, lot=lot))
        elif lot.ghg_reduction_red_ii > 99:
            errors.append(generic_error(error=CarbureSanityCheckErrors.GHG_REDUC_SUP_99, lot=lot))
        elif lot.ghg_reduction_red_ii < 50:
            errors.append(
                generic_error(
                    error=CarbureSanityCheckErrors.GHG_REDUC_INF_50,
                    lot=lot,
                    is_blocking=True,
                )
            )
        else:
            # all good
            pass
    else:
        if lot.ghg_reduction >= 100:
            errors.append(generic_error(error=CarbureSanityCheckErrors.GHG_REDUC_SUP_100, lot=lot))
        elif lot.ghg_reduction > 99:
            errors.append(generic_error(error=CarbureSanityCheckErrors.GHG_REDUC_SUP_99, lot=lot))
        elif lot.ghg_reduction < 50:
            errors.append(
                generic_error(
                    error=CarbureSanityCheckErrors.GHG_REDUC_INF_50,
                    lot=lot,
                    is_blocking=True,
                )
            )
        else:
            # all good
            pass

    if lot.etd <= 0:
        errors.append(
            generic_error(
                error=CarbureSanityCheckErrors.GHG_ETD_0,
                lot=lot,
                is_blocking=True,
                field="etd",
            )
        )
    if lot.ep <= 0:
        errors.append(
            generic_error(
                error=CarbureSanityCheckErrors.GHG_EP_0,
                lot=lot,
                is_blocking=True,
                field="ep",
            )
        )
    if lot.el < 0:
        errors.append(generic_error(error=CarbureSanityCheckErrors.GHG_EL_NEG, lot=lot, field="el"))

    if lot.feedstock:
        # 2022-02-01: is_blocking=True sur demande de Guillaume
        if lot.feedstock.category == "CONV" and lot.eec == 0:
            errors.append(
                generic_error(
                    error=CarbureSanityCheckErrors.GHG_EEC_0,
                    lot=lot,
                    is_blocking=True,
                    extra="GES Culture 0 pour MP conventionnelle (%s)" % (lot.feedstock.name),
                    field="eec",
                )
            )

        if lot.feedstock.category != "CONV" and lot.feedstock.code != "EP2" and lot.eec != 0:
            errors.append(
                generic_error(
                    error=CarbureSanityCheckErrors.EEC_WITH_RESIDUE,
                    lot=lot,
                    field="eec",
                )
            )

    commissioning_date = lot.production_site_commissioning_date
    if (
        commissioning_date
        and isinstance(commissioning_date, datetime.datetime)
        or isinstance(commissioning_date, datetime.date)
    ):
        if lot.delivery_date >= july1st2021:
            # RED II
            if commissioning_date > oct2015 and lot.ghg_reduction_red_ii < 60:
                errors.append(
                    generic_error(
                        error=CarbureSanityCheckErrors.GHG_REDUC_INF_60,
                        lot=lot,
                        is_blocking=True,
                    )
                )
            if commissioning_date >= jan2021 and lot.ghg_reduction_red_ii < 65:
                errors.append(
                    generic_error(
                        error=CarbureSanityCheckErrors.GHG_REDUC_INF_65,
                        lot=lot,
                        is_blocking=True,
                    )
                )
        else:
            # RED I
            if commissioning_date > oct2015 and lot.ghg_reduction < 60:
                errors.append(
                    generic_error(
                        error=CarbureSanityCheckErrors.GHG_REDUC_INF_60,
                        lot=lot,
                        is_blocking=True,
                    )
                )
            if commissioning_date >= jan2021 and lot.ghg_reduction < 65:
                errors.append(
                    generic_error(
                        error=CarbureSanityCheckErrors.GHG_REDUC_INF_65,
                        lot=lot,
                        is_blocking=True,
                    )
                )


def check_certificates(prefetched_data, lot, errors):
    # PRODUCTION SITE CERTIFICATES
    if lot.production_site_certificate:
        cert = lot.production_site_certificate
        if cert is not None:
            cert = cert.upper()
        if cert not in prefetched_data["certificates"]:
            errors.append(
                generic_error(
                    error=CarbureCertificatesErrors.UNKNOWN_PRODSITE_CERT,
                    lot=lot,
                    display_to_recipient=True,
                    field="production_site_certificate",
                )
            )
        else:
            # certificate is set and exists. is it valid?
            c = prefetched_data["certificates"][cert]
            if c["valid_until"] < lot.delivery_date:
                errors.append(
                    generic_error(
                        error=CarbureCertificatesErrors.EXPIRED_PRODSITE_CERT,
                        lot=lot,
                        display_to_recipient=True,
                        field="production_site_certificate",
                    )
                )

    # SUPPLIER CERT
    if not lot.supplier_certificate:
        errors.append(
            generic_error(
                error=CarbureCertificatesErrors.NO_SUPPLIER_CERT,
                lot=lot,
                display_to_recipient=True,
                field="supplier_certificate",
            )
        )  # blocking in check_mandatory_fields if client is an operator
    else:
        cert = lot.supplier_certificate
        if cert is not None:
            cert = cert.upper()
        if cert not in prefetched_data["certificates"]:
            errors.append(
                generic_error(
                    error=CarbureCertificatesErrors.UNKNOWN_SUPPLIER_CERT,
                    lot=lot,
                    display_to_recipient=True,
                    field="supplier_certificate",
                )
            )
        else:
            # certificate is set and exists. is it valid?
            c = prefetched_data["certificates"][cert]
            if c["valid_until"] < lot.delivery_date:
                errors.append(
                    generic_error(
                        error=CarbureCertificatesErrors.EXPIRED_SUPPLIER_CERT,
                        lot=lot,
                        display_to_recipient=True,
                        field="supplier_certificate",
                    )
                )

    # check if mapping of SUPPLIER CERT / ENTITY has been rejected by admin
    if (
        lot.carbure_supplier
        and lot.carbure_supplier.id in prefetched_data["entity_certificates"]
        and lot.supplier_certificate in prefetched_data["entity_certificates"][lot.carbure_supplier.id]
        and prefetched_data["entity_certificates"][lot.carbure_supplier.id][lot.supplier_certificate].rejected_by_admin
    ):
        errors.append(
            generic_error(
                error=CarbureCertificatesErrors.REJECTED_SUPPLIER_CERTIFICATE,
                lot=lot,
                is_blocking=True,
                field="supplier_certificate",
            )
        )

    # DOUBLE COUNTING CERTIFICATES
    if lot.feedstock and lot.feedstock.is_double_compte:
        # identify where the certificate is (attached to prod site or attached to lot)
        dc_cert = lot.production_site_double_counting_certificate
        if not dc_cert:
            errors.append(
                generic_error(
                    error=CarbureCertificatesErrors.MISSING_REF_DBL_COUNTING,
                    lot=lot,
                    display_to_recipient=True,
                    field="dc_reference",
                )
            )
        else:
            if dc_cert not in prefetched_data["double_counting_certificates"]:
                # 2022-03-22: GC requests that this is a blocking error
                errors.append(
                    generic_error(
                        error=CarbureCertificatesErrors.UNKNOWN_DOUBLE_COUNTING_CERTIFICATE,
                        lot=lot,
                        is_blocking=True,
                        display_to_recipient=True,
                        field="dc_reference",
                    )
                )
            elif not lot.parent_lot and not lot.parent_stock:
                dcc = prefetched_data["double_counting_certificates"][dc_cert]

                dcc_period = dcc.valid_until.year * 100 + dcc.valid_until.month  # ex 202012

                # certificat expiré
                if dcc_period < lot.period:
                    # 2022-03-22: GC requests that expired dc certificates are blocking after the next declaration.
                    # Ex: a certificate expiring at the beginning of June is valid for the June declaration
                    errors.append(
                        generic_error(
                            error=CarbureCertificatesErrors.EXPIRED_DOUBLE_COUNTING_CERTIFICATE,
                            display_to_recipient=True,
                            is_blocking=True,
                            lot=lot,
                        )
                    )
                # certificat a expiré dans le mois en cours (donc invalide au mois suivant )
                elif dcc.valid_until < lot.delivery_date:
                    # Non blocking
                    errors.append(
                        generic_error(
                            error=CarbureCertificatesErrors.EXPIRED_DOUBLE_COUNTING_CERTIFICATE,
                            display_to_recipient=True,
                            lot=lot,
                        )
                    )
                # certificat pas encore valide
                elif dcc.valid_from > lot.delivery_date:
                    errors.append(
                        generic_error(
                            error=CarbureCertificatesErrors.INVALID_DOUBLE_COUNTING_CERTIFICATE,
                            display_to_recipient=True,
                            is_blocking=True,
                            lot=lot,
                        )
                    )
                else:
                    pass
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

    if lot.delivery_type == CarbureLot.RFC and lot.biofuel.code not in [
        "ED95",
        "B100",
        "ETH",
        "EMHV",
        "EMHU",
    ]:
        errors.append(
            generic_error(
                error=CarbureSanityCheckErrors.MAC_BC_WRONG,
                lot=lot,
                is_blocking=True,
                fields=["biofuel", "delivery_type"],
            )
        )

    if (
        lot.delivery_type == CarbureLot.RFC
        and lot.carbure_delivery_site
        and lot.carbure_delivery_site.depot_type != "EFPE"
    ):
        errors.append(
            generic_error(
                error=CarbureSanityCheckErrors.MAC_NOT_EFPE,
                lot=lot,
                fields=["delivery_type"],
            )
        )
    # check volume
    if lot.volume < 2000 and lot.delivery_type not in [
        CarbureLot.RFC,
        CarbureLot.FLUSHED,
    ]:
        errors.append(generic_error(error=CarbureSanityCheckErrors.VOLUME_FAIBLE, lot=lot, field="volume"))

    # check year
    if lot.year in prefetched_data["locked_years"] or lot.year <= 2015:
        errors.append(
            generic_error(
                error=CarbureSanityCheckErrors.YEAR_LOCKED,
                lot=lot,
                field="delivery_date",
                is_blocking=True,
            )
        )  # TODO passer des variables pour custom les messages d'erreur fields = {"year":lot.year}

    # provenance des matieres premieres
    if lot.feedstock and lot.country_of_origin:
        if lot.feedstock.code == "RESIDUS_VINIQUES":
            errors.append(
                generic_error(
                    error=CarbureSanityCheckErrors.DEPRECATED_MP,
                    lot=lot,
                    field="feedstock",
                )
            )

        if lot.feedstock.code == "SOJA":
            if lot.country_of_origin.code_pays not in ["US", "AR", "BR", "UY", "PY"]:
                errors.append(
                    generic_error(
                        error=CarbureSanityCheckErrors.PROVENANCE_MP,
                        lot=lot,
                        extra="%s de %s" % (lot.feedstock.name, lot.country_of_origin.name),
                        field="country_of_origin",
                    )
                )
        elif lot.feedstock.code == "HUILE_PALME":
            if lot.country_of_origin.code_pays not in ["ID", "MY", "HN"]:
                errors.append(
                    generic_error(
                        error=CarbureSanityCheckErrors.PROVENANCE_MP,
                        lot=lot,
                        extra="%s de %s" % (lot.feedstock.name, lot.country_of_origin.name),
                        field="country_of_origin",
                    )
                )
        elif lot.feedstock.code == "COLZA":
            if (
                lot.country_of_origin.code_pays not in ["US", "CA", "AU", "UA", "CN", "IN", "DE", "FR", "PL", "UK"]
                and not lot.country_of_origin.is_in_europe
            ):
                errors.append(
                    generic_error(
                        error=CarbureSanityCheckErrors.PROVENANCE_MP,
                        lot=lot,
                        extra="%s de %s" % (lot.feedstock.name, lot.country_of_origin.name),
                        field="country_of_origin",
                    )
                )
        elif lot.feedstock.code == "CANNE_A_SUCRE":
            if lot.country_of_origin.code_pays not in ["BR", "BO"]:
                errors.append(
                    generic_error(
                        error=CarbureSanityCheckErrors.PROVENANCE_MP,
                        lot=lot,
                        extra="%s de %s" % (lot.feedstock.name, lot.country_of_origin.name),
                        field="country_of_origin",
                    )
                )
        elif lot.feedstock.code == "MAIS":
            if not lot.country_of_origin.is_in_europe and lot.country_of_origin.code_pays not in ["US", "UA"]:
                errors.append(
                    generic_error(
                        error=CarbureSanityCheckErrors.PROVENANCE_MP,
                        lot=lot,
                        extra="%s de %s" % (lot.feedstock.name, lot.country_of_origin.name),
                        field="country_of_origin",
                    )
                )
        elif lot.feedstock.code == "BETTERAVE":
            if not lot.country_of_origin.is_in_europe:
                errors.append(
                    generic_error(
                        error=CarbureSanityCheckErrors.PROVENANCE_MP,
                        lot=lot,
                        extra="%s de %s" % (lot.feedstock.name, lot.country_of_origin.name),
                        field="country_of_origin",
                    )
                )
        else:
            pass

    if lot.biofuel and lot.feedstock:
        # consistence des matieres premieres avec biocarburant
        if lot.biofuel.is_alcool and lot.feedstock.compatible_alcool is False:
            errors.append(
                generic_error(
                    error=CarbureSanityCheckErrors.MP_BC_INCOHERENT,
                    lot=lot,
                    is_blocking=True,
                    extra="%s issu de fermentation et %s n'est pas fermentescible"
                    % (lot.biofuel.name, lot.feedstock.name),
                    fields=["biofuel_code", "feedstock_code"],
                )
            )
        if lot.biofuel.is_graisse and lot.feedstock.compatible_graisse is False:
            errors.append(
                generic_error(
                    error=CarbureSanityCheckErrors.MP_BC_INCOHERENT,
                    lot=lot,
                    is_blocking=True,
                    extra="Matière première (%s) incompatible avec Esthers Méthyliques" % (lot.feedstock.name),
                    fields=["biofuel_code", "feedstock_code"],
                )
            )

        # double comptage, cas specifiques
        if lot.feedstock.is_double_compte:
            in_carbure_without_dc = lot.carbure_production_site and not lot.carbure_production_site.dc_reference
            not_in_carbure_without_dc = (
                lot.unknown_production_site and not lot.production_site_double_counting_certificate
            )
            if in_carbure_without_dc or not_in_carbure_without_dc:
                errors.append(
                    generic_error(
                        error=CarbureSanityCheckErrors.MISSING_REF_DBL_COUNTING,
                        lot=lot,
                        is_blocking=True,
                        extra="%s de %s" % (lot.biofuel.name, lot.feedstock.name),
                        field="production_site_dbl_counting",
                    )
                )

        if lot.biofuel.is_graisse:
            if lot.biofuel.code == "EMHU" and lot.feedstock.code != "HUILE_ALIMENTAIRE_USAGEE":
                errors.append(
                    generic_error(
                        error=CarbureSanityCheckErrors.MP_BC_INCOHERENT,
                        lot=lot,
                        is_blocking=True,
                        extra="%s doit être à base d'huiles alimentaires usagées" % (lot.biofuel.name),
                        fields=["biofuel_code", "feedstock_code"],
                    )
                )
            if lot.biofuel.code == "EMHV" and lot.feedstock.code not in [
                "COLZA",
                "TOURNESOL",
                "SOJA",
                "HUILE_PALME",
                "CARINATA",
            ]:
                errors.append(
                    generic_error(
                        error=CarbureSanityCheckErrors.MP_BC_INCOHERENT,
                        lot=lot,
                        is_blocking=True,
                        extra="%s doit être à base de végétaux (Colza, Tournesol, Soja, Huile de Palme)"
                        % (lot.biofuel.name),
                        fields=["biofuel_code", "feedstock_code"],
                    )
                )
            if lot.biofuel.code == "EMHA" and lot.feedstock.code not in [
                "HUILES_OU_GRAISSES_ANIMALES_CAT1_CAT2",
                "HUILES_OU_GRAISSES_ANIMALES_CAT3",
            ]:
                errors.append(
                    generic_error(
                        error=CarbureSanityCheckErrors.MP_BC_INCOHERENT,
                        lot=lot,
                        is_blocking=True,
                        extra="%s doit être à base d'huiles ou graisses animales" % (lot.biofuel.name),
                        fields=["biofuel_code", "feedstock_code"],
                    )
                )

        if lot.feedstock.code in [
            "HUILES_OU_GRAISSES_ANIMALES_CAT1_CAT2",
            "HUILES_OU_GRAISSES_ANIMALES_CAT3",
        ] and lot.biofuel.code not in [
            "EMHA",
            "HOE",
            "HOG",
            "HOC",
            "HCC",
            "HCG",
            "HCE",
            "B100",
        ]:
            errors.append(
                generic_error(
                    error=CarbureSanityCheckErrors.MP_BC_INCOHERENT,
                    lot=lot,
                    is_blocking=True,
                    extra="Des huiles ou graisses animales ne peuvent donner que des EMHA, B100 ou HOG/HOE/HOC",
                    fields=["biofuel_code", "feedstock_code"],
                )
            )
        if lot.feedstock.code == "HUILE_ALIMENTAIRE_USAGEE" and lot.biofuel.code not in [
            "EMHU",
            "HOE",
            "HOG",
            "HOC",
            "HCC",
            "HCG",
            "HCE",
            "B100",
        ]:
            errors.append(
                generic_error(
                    error=CarbureSanityCheckErrors.MP_BC_INCOHERENT,
                    lot=lot,
                    is_blocking=True,
                    extra="Des huiles alimentaires usagées ne peuvent donner que des EMHU, B100 ou HOG/HOE/HOC",
                    fields=["biofuel_code", "feedstock_code"],
                )
            )

        if lot.feedstock.code in [
            "MAIS",
            "BLE",
            "BETTERAVE",
            "CANNE_A_SUCRE",
            "RESIDUS_VINIQUES",
            "LIES_DE_VIN",
            "MARC_DE_RAISIN",
        ] and lot.biofuel.code not in ["ETH", "ETBE", "ED95"]:
            errors.append(
                generic_error(
                    error=CarbureSanityCheckErrors.MP_BC_INCOHERENT,
                    lot=lot,
                    is_blocking=True,
                    extra="Maïs, Blé, Betterave, Canne à Sucre ou Résidus Viniques ne peuvent créer que de l'Éthanol ou ETBE",
                    fields=["biofuel_code", "feedstock_code"],
                )
            )

        if not lot.feedstock.is_huile_vegetale and lot.biofuel.code in [
            "HVOE",
            "HVOG",
            "HVOC",
        ]:
            errors.append(
                generic_error(
                    error=CarbureSanityCheckErrors.MP_BC_INCOHERENT,
                    lot=lot,
                    is_blocking=True,
                    extra="Un HVO doit provenir d'huiles végétales uniquement. Pour les autres huiles hydrotraitées, voir la nomenclature HOE/HOG/HOC",
                    fields=["biofuel_code", "feedstock_code"],
                )
            )

    # configuration
    if lot.feedstock and lot.carbure_production_site:
        if lot.carbure_production_site.name in prefetched_data["my_production_sites"]:
            mps = [
                psi.matiere_premiere
                for psi in prefetched_data["my_production_sites"][
                    lot.carbure_production_site.name
                ].productionsiteinput_set.all()
            ]
            if lot.feedstock not in mps:
                errors.append(
                    generic_error(
                        error=CarbureSanityCheckErrors.MP_NOT_CONFIGURED,
                        lot=lot,
                        display_to_recipient=False,
                        field="feedstock_code",
                    )
                )
    if lot.biofuel and lot.carbure_production_site:
        if lot.carbure_production_site.name in prefetched_data["my_production_sites"]:
            bcs = [
                pso.biocarburant
                for pso in prefetched_data["my_production_sites"][
                    lot.carbure_production_site.name
                ].productionsiteoutput_set.all()
            ]
            if lot.biofuel not in bcs:
                errors.append(
                    generic_error(
                        error=CarbureSanityCheckErrors.BC_NOT_CONFIGURED,
                        lot=lot,
                        display_to_recipient=False,
                        field="biofuel_code",
                    )
                )
    if lot.carbure_client and lot.delivery_type != CarbureLot.TRADING:  # ignore delivery issues for trading
        if lot.carbure_client.id not in prefetched_data["depotsbyentity"]:
            # not a single delivery sites linked to entity
            errors.append(
                generic_error(
                    error=CarbureSanityCheckErrors.DEPOT_NOT_CONFIGURED,
                    lot=lot,
                    display_to_recipient=True,
                    display_to_creator=False,
                    field="delivery_site",
                )
            )
        else:
            # some delivery sites linked to entity
            if (
                lot.carbure_delivery_site
                and lot.carbure_delivery_site.depot_id not in prefetched_data["depotsbyentity"][lot.carbure_client.id]
            ):
                # this specific delivery site is not linked
                errors.append(
                    generic_error(
                        error=CarbureSanityCheckErrors.DEPOT_NOT_CONFIGURED,
                        lot=lot,
                        display_to_recipient=True,
                        display_to_creator=False,
                        field="delivery_site",
                    )
                )
    in_two_weeks = datetime.date.today() + datetime.timedelta(days=15)
    if lot.delivery_date > in_two_weeks:
        errors.append(
            GenericError(
                lot=lot,
                field="delivery_date",
                error=CarbureSanityCheckErrors.DELIVERY_IN_THE_FUTURE,
                extra="La date de livraison est dans le futur",
                value=lot.delivery_date,
                display_to_creator=True,
                is_blocking=True,
            )
        )

    # CERTIFICATES CHECK
    check_certificates(prefetched_data, lot, errors)
    # GHG STATS CHECK
    check_ghg_values(prefetched_data, lot, errors)
    for e in errors:
        if e.is_blocking:
            is_sane = False
            break
    return is_sane, errors


def sanity_check_mandatory_fields(lot):
    is_valid = True
    today = datetime.date.today()
    errors = []

    if lot.lot_status == CarbureLot.FLUSHED:
        return True, []

    if not lot.volume:
        errors.append(
            generic_error(
                error=CarbureSanityCheckErrors.MISSING_VOLUME,
                lot=lot,
                field="volume",
                is_blocking=True,
            )
        )
        is_valid = False
    if not lot.biofuel:
        errors.append(
            generic_error(
                error=CarbureSanityCheckErrors.MISSING_BIOFUEL,
                lot=lot,
                field="biofuel_code",
                is_blocking=True,
            )
        )
        is_valid = False
    if not lot.feedstock:
        errors.append(
            generic_error(
                error=CarbureSanityCheckErrors.MISSING_FEEDSTOCK,
                lot=lot,
                field="feedstock_code",
                is_blocking=True,
            )
        )
        is_valid = False
    if lot.carbure_producer and lot.carbure_production_site is None:
        errors.append(
            generic_error(
                error=CarbureSanityCheckErrors.UNKNOWN_PRODUCTION_SITE,
                lot=lot,
                field="carbure_production_site",
                is_blocking=True,
            )
        )
        is_valid = False
    if not lot.carbure_production_site and not lot.production_site_commissioning_date:
        errors.append(
            generic_error(
                error=CarbureSanityCheckErrors.MISSING_PRODUCTION_SITE_COMDATE,
                lot=lot,
                field="production_site_commissioning_date",
                is_blocking=True,
            )
        )
        is_valid = False

    if lot.delivery_type not in [CarbureLot.RFC, CarbureLot.FLUSHED] and lot.transport_document_reference is None:
        errors.append(
            generic_error(
                error=CarbureSanityCheckErrors.MISSING_TRANSPORT_DOCUMENT_REFERENCE,
                lot=lot,
                field="transport_document_reference",
                is_blocking=True,
            )
        )
        is_valid = False
    if lot.delivery_type in [
        CarbureLot.BLENDING,
        CarbureLot.TRADING,
        CarbureLot.STOCK,
        CarbureLot.DIRECT,
        CarbureLot.UNKNOWN,
    ]:
        if lot.delivery_site_country and lot.delivery_site_country.code_pays == "FR":
            # we need to know the Depot
            if not lot.carbure_delivery_site:
                errors.append(
                    generic_error(
                        error=CarbureSanityCheckErrors.MISSING_CARBURE_DELIVERY_SITE,
                        lot=lot,
                        field="carbure_delivery_site",
                        is_blocking=True,
                    )
                )
                is_valid = False
            # and we need to know the client
            if not lot.carbure_client:
                errors.append(
                    generic_error(
                        error=CarbureSanityCheckErrors.MISSING_CARBURE_CLIENT,
                        lot=lot,
                        field="carbure_client",
                        is_blocking=True,
                    )
                )
                is_valid = False
    if not lot.delivery_date:
        errors.append(
            generic_error(
                error=CarbureSanityCheckErrors.MISSING_DELIVERY_DATE,
                lot=lot,
                field="delivery_date",
                is_blocking=True,
            )
        )
        is_valid = False
    if (lot.delivery_date - today) > datetime.timedelta(days=3650) or (lot.delivery_date - today) < datetime.timedelta(
        days=-3650
    ):
        errors.append(
            generic_error(
                error=CarbureSanityCheckErrors.WRONG_DELIVERY_DATE,
                lot=lot,
                field="delivery_date",
                is_blocking=True,
            )
        )
        is_valid = False

    if not lot.delivery_site_country:
        errors.append(
            generic_error(
                error=CarbureSanityCheckErrors.MISSING_DELIVERY_SITE_COUNTRY,
                lot=lot,
                field="delivery_site_country",
                is_blocking=True,
            )
        )
        is_valid = False
    if lot.delivery_site_country and lot.delivery_site_country.is_in_europe and not lot.country_of_origin:
        errors.append(
            generic_error(
                error=CarbureSanityCheckErrors.MISSING_FEEDSTOCK_COUNTRY_OF_ORIGIN,
                lot=lot,
                field="country_of_origin",
                is_blocking=True,
            )
        )
        is_valid = False

    if lot.carbure_client and lot.carbure_client.entity_type == Entity.OPERATOR:
        # client is an operator
        # make sure we have a certificate
        if not lot.supplier_certificate and not lot.vendor_certificate:
            errors.append(
                generic_error(
                    error=CarbureCertificatesErrors.MISSING_SUPPLIER_CERTIFICATE,
                    lot=lot,
                    field="supplier_certificate",
                    is_blocking=True,
                )
            )
            is_valid = False
    return is_valid, errors
