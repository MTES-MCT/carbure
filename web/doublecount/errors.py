from typing import TypedDict


class DoubleCountingError:
    EXCEL_PARSING_ERROR = "EXCEL_PARSING_ERROR"
    BAD_WORKSHEET_NAME = "BAD_WORKSHEET_NAME"
    MISSING_BIOFUEL = "MISSING_BIOFUEL"
    MISSING_ESTIMATED_PRODUCTION = "MISSING_ESTIMATED_PRODUCTION"
    MISSING_MAX_PRODUCTION_CAPACITY = "MISSING_MAX_PRODUCTION_CAPACITY"
    MISSING_FEEDSTOCK = "MISSING_FEEDSTOCK"
    MISSING_COUNTRY_OF_ORIGIN = "MISSING_COUNTRY_OF_ORIGIN"
    UNKNOWN_COUNTRY_OF_ORIGIN = "UNKNOWN_COUNTRY_OF_ORIGIN"
    MISSING_DATA = "MISSING_DATA"
    MP_BC_INCOHERENT = "MP_BC_INCOHERENT"
    POME_GT_2000 = "POME_GT_2000"
    PRODUCTION_MISMATCH_QUOTA = "PRODUCTION_MISMATCH_QUOTA"
    PRODUCTION_MISMATCH_SOURCING = "PRODUCTION_MISMATCH_SOURCING"
    PRODUCTION_MISMATCH_PRODUCTION_MAX = "PRODUCTION_MISMATCH_PRODUCTION_MAX"
    UNKNOWN_YEAR = "UNKNOWN_YEAR"
    INVALID_YEAR = "INVALID_YEAR"
    MISSING_TRACEABILITY = "MISSING_TRACEABILITY"
    FEEDSTOCK_NOT_DOUBLE_COUNTING = "FEEDSTOCK_NOT_DOUBLE_COUNTING"
    FEEDSTOCK_UNRECOGNIZED = "FEEDSTOCK_UNRECOGNIZED"
    BIOFUEL_UNRECOGNIZED = "BIOFUEL_UNRECOGNIZED"


class DcError(TypedDict):
    error: str
    line_number: int
    is_blocking: bool
    meta: dict


def error(type: str, line: int = -1, meta: dict = None, is_blocking: bool = True) -> DcError:
    if meta is None:
        meta = {}
    return {
        "error": type,
        "line_number": line,
        "is_blocking": is_blocking,
        "meta": meta,
    }
