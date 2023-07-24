from core.carburetypes import CarbureCertificatesErrors, CarbureSanityCheckErrors
from core.models import CarbureLot
from .helpers import generic_error


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
    dc_cert = lot.production_site_double_counting_certificate

    # we append the production site id to differentiate certificates
    # for the specific case of duplicated production sites for Ryssen and BAE
    if lot.carbure_production_site:
        dc_cert = f"{dc_cert}_{lot.carbure_production_site.pk}"

    return is_dc, prefetched_data["double_counting_certificates"].get(dc_cert)
