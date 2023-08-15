from typing import TypedDict

from transactions.helpers import MISSING_COUNTRY_OF_ORIGIN


class DoubleCountingError:
    EXCEL_PARSING_ERROR = "EXCEL_PARSING_ERROR"
    BAD_WORKSHEET_NAME = "BAD_WORKSHEET_NAME"
    MISSING_BIOFUEL = "MISSING_BIOFUEL"
    MISSING_ESTIMATED_PRODUCTION = "MISSING_ESTIMATED_PRODUCTION"
    MISSING_MAX_PRODUCTION_CAPACITY = "MISSING_MAX_PRODUCTION_CAPACITY"
    MISSING_FEEDSTOCK = "MISSING_FEEDSTOCK"
    MISSING_COUNTRY_OF_ORIGIN = "MISSING_COUNTRY_OF_ORIGIN"
    MISSING_DATA = "MISSING_DATA"
    MP_BC_INCOHERENT = "MP_BC_INCOHERENT"
    POME_GT_2000 = "POME_GT_2000"
    PRODUCTION_MISMATCH_QUOTA = "PRODUCTION_MISMATCH_QUOTA"
    PRODUCTION_MISMATCH_SOURCING = "PRODUCTION_MISMATCH_SOURCING"
    UNKNOWN_YEAR = "UNKNOWN_YEAR"
    INVALID_YEAR = "INVALID_YEAR"
    MISSING_TRACEABILITY = "MISSING_TRACEABILITY"


class DcError(TypedDict):
    error: str
    line_number: int
    is_blocking: bool
    meta: dict


def error(type: str, line: int = -1, meta: dict = {}, is_blocking: bool = True) -> DcError:
    return {
        "error": type,
        "line_number": line,
        "is_blocking": is_blocking,
        "meta": meta,
    }
