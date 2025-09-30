from core.carburetypes import CarbureSanityCheckErrors
from core.models import CarbureLot

from .helpers import PrefetchedData, generic_error


def check_certificate_validity(lot: CarbureLot, prefetched_data: PrefetchedData):
    if not lot.supplier_certificate:
        return

    certificate = prefetched_data["certificates"].get(lot.supplier_certificate.upper())
    delivery_date = lot.delivery_date
    valid_from = certificate["valid_from"] if certificate else None
    valid_until = certificate["valid_until"] if certificate else None

    if not certificate or valid_from > delivery_date or valid_until < delivery_date:
        return generic_error(
            error=CarbureSanityCheckErrors.INVALID_CERTIFICATE,
            lot=lot,
            is_blocking=True,
            field="supplier_certificate",
        )
