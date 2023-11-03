from certificates.models import DoubleCountingRegistration
from core.carburetypes import CarbureCertificatesErrors, CarbureSanityCheckErrors
from core.models import CarbureLot
from doublecount.factories import production
from doublecount.models import DoubleCountingApplication, DoubleCountingProduction
from .helpers import generic_error
from django.db.models.aggregates import Count, Sum
import pandas as pd


def check_missing_ref_dbl_counting(lot: CarbureLot):
    if lot.feedstock and lot.feedstock.is_double_compte:
        if not lot.production_site_double_counting_certificate:
            return generic_error(
                error=CarbureSanityCheckErrors.MISSING_REF_DBL_COUNTING,
                lot=lot,
                is_blocking=True,
                extra="%s de %s" % (lot.biofuel, lot.feedstock),
                field="production_site_double_counting_certificate",
            )


def check_unknown_double_counting_certificate(lot: CarbureLot, prefetched_data):
    is_dc, certificate = get_dc(lot, prefetched_data)

    if is_dc and certificate is None:
        return generic_error(
            error=CarbureCertificatesErrors.UNKNOWN_DOUBLE_COUNTING_CERTIFICATE,
            lot=lot,
            is_blocking=True,
            display_to_recipient=True,
            field="production_site_double_counting_certificate",
        )


def check_expired_double_counting_certificate(lot: CarbureLot, prefetched_data):
    is_dc, certificate = get_dc(lot, prefetched_data)
    if not is_dc or certificate is None:
        return

    dc_last_period = certificate.valid_until.year * 100 + certificate.valid_until.month  # ex 202012

    if dc_last_period < lot.period:
        # 2022-03-22: GC requests that expired dc certificates are blocking after the next declaration.
        # Ex: a certificate expiring at the beginning of June is valid for the June declaration
        return generic_error(
            error=CarbureCertificatesErrors.EXPIRED_DOUBLE_COUNTING_CERTIFICATE,
            display_to_recipient=True,
            is_blocking=True,
            lot=lot,
            field="production_site_double_counting_certificate",
        )
    elif certificate.valid_until < lot.delivery_date:
        # Non blocking
        return generic_error(
            error=CarbureCertificatesErrors.EXPIRED_DOUBLE_COUNTING_CERTIFICATE,
            display_to_recipient=True,
            lot=lot,
            field="production_site_double_counting_certificate",
        )


def check_invalid_double_counting_certificate(lot: CarbureLot, prefetched_data):
    is_dc, certificate = get_dc(lot, prefetched_data)
    if not is_dc or certificate is None:
        return

    if certificate.valid_from > lot.delivery_date:
        return generic_error(
            error=CarbureCertificatesErrors.INVALID_DOUBLE_COUNTING_CERTIFICATE,
            display_to_recipient=True,
            is_blocking=True,
            lot=lot,
        )


def get_dc(lot: CarbureLot, prefetched_data):
    # only focus on the original lot, ignore children
    if lot.parent_lot or lot.parent_stock:
        return False, None

    is_dc = lot.feedstock and lot.feedstock.is_double_compte
    dc_cert_id = lot.production_site_double_counting_certificate

    dc_cert_variations = prefetched_data["double_counting_certificates"].get(dc_cert_id, [])

    if len(dc_cert_variations) == 0:
        return is_dc, None

    # pick the DC certificate matching the lot production site
    for dc_cert in dc_cert_variations:
        if (
            not lot.carbure_production_site
            or not dc_cert.production_site
            or dc_cert.production_site == lot.carbure_production_site
        ):
            return is_dc, dc_cert

    return is_dc, None


def check_double_counting_quotas(lot: CarbureLot, prefetched_data):
    is_dc, certificate = get_dc(lot, prefetched_data)
    if not is_dc or certificate is None:
        return

    quotas_is_excedeed = check_excedeed_quotas(lot, certificate)
    if quotas_is_excedeed:
        return generic_error(
            error=CarbureSanityCheckErrors.EXCEEDED_DOUBLE_COUNTING_QUOTAS,
            lot=lot,
            fields=["production_site_double_counting_certificate"],
        )


def check_excedeed_quotas(lot: CarbureLot, agreement: DoubleCountingRegistration):
    application = agreement.application
    if not application or application.status != DoubleCountingApplication.ACCEPTED:
        return None

    # tous les couples BC / MP pour le site de production sur une année
    targeted_quotas = DoubleCountingProduction.objects.values("approved_quota").get(
        dca_id=application.id, approved_quota__gt=0, feedstock_id=lot.feedstock_id, biofuel_id=lot.biofuel_id, year=lot.year
    )

    # tous les lots pour des MP double compté pour le site de production regroupé par couple et par année
    production_lots = (
        CarbureLot.objects.filter(
            lot_status__in=[CarbureLot.ACCEPTED, CarbureLot.FROZEN],
            carbure_production_site_id=application.production_site,
        )
        .values("weight", "id")
        .filter(
            feedstock_id=lot.feedstock_id,
            biofuel_id=lot.biofuel_id,
            year=lot.year,
        )
        .exclude(id=lot.id)
    )

    max_production = targeted_quotas["approved_quota"]

    if len(production_lots) == 0:
        production_kg = lot.weight
    else:
        production_kg = int(production_lots.aggregate(total_weight=Sum("weight"))["total_weight"]) + lot.weight

    return production_kg > max_production
