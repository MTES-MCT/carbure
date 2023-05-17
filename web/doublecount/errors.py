from typing import TypedDict


class DoubleCountingError:
    BAD_WORKSHEET_NAME = "BAD_WORKSHEET_NAME"
    EXCEL_PARSING_ERROR = "EXCEL_PARSING_ERROR"
    LINE_FEEDSTOCKS_INCOHERENT = "LINE_FEEDSTOCKS_INCOHERENT"
    MISSING_BIOFUEL = "MISSING_BIOFUEL"
    MISSING_ESTIMATED_PRODUCTION = "MISSING_ESTIMATED_PRODUCTION"
    MISSING_FEEDSTOCK = "MISSING_FEEDSTOCK"
    MP_BC_INCOHERENT = "MP_BC_INCOHERENT"
    NOT_DC_FEEDSTOCK = "NOT_DC_FEEDSTOCK"
    POME_GT_2000 = "POME_GT_2000"
    PRODUCTION_MISMATCH_QUOTA = "PRODUCTION_MISMATCH_QUOTA"
    PRODUCTION_MISMATCH_SOURCING = "PRODUCTION_MISMATCH_SOURCING"
    UNKNOWN_BIOFUEL = "UNKNOWN_BIOFUEL"
    UNKNOWN_FEEDSTOCK = "UNKNOWN_FEEDSTOCK"
    UNKNOWN_YEAR = "UNKNOWN_YEAR"


class DcError(TypedDict):
    error: str
    line_number: int
    is_blocking: bool
    meta: dict


def error(
    type: str, line: int = -1, meta: dict = {}, is_blocking: bool = True
) -> DcError:
    return {
        "error": type,
        "line_number": line,
        "is_blocking": is_blocking,
        "meta": meta,
    }
