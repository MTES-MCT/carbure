from core.models import Biocarburant, MatierePremiere

_udb_code_to_carbure_code_mapping = {
    "SFC0015": "BG",
    "URWS023": "BETTERAVE",
}


class UDBConversionError(RuntimeError):
    def __init__(self, message):
        super().__init__(message)
        self.message = message


def _from_UDB_material(udb_code):
    if udb_code not in _udb_code_to_carbure_code_mapping:
        raise UDBConversionError(f"Unknown UDB Material code: {udb_code}")

    return _udb_code_to_carbure_code_mapping[udb_code]


def from_UDB_biofuel_code(udb_code):
    carbure_code = _from_UDB_material(udb_code)
    return Biocarburant.objects.get(code=carbure_code)


def from_UDB_feedstock_code(udb_code):
    carbure_code = _from_UDB_material(udb_code)
    return MatierePremiere.objects.get(code=carbure_code)
