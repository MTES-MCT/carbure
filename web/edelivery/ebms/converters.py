from core.models import Biocarburant, CarbureLot, MatierePremiere


class UDBConversionError(RuntimeError):
    def __init__(self, message):
        super().__init__(message)
        self.message = message


class BaseConverter:
    _default_conversion_mapping = {}

    def __init__(self, conversion_mapping=None):
        self.conversion_mapping = conversion_mapping if conversion_mapping else self._default_conversion_mapping


class MaterialConverter(BaseConverter):
    _default_conversion_mapping = {
        "FBM0003": "EMAG",
        "SFC0015": "BG",
        "URWR001": "COLZA",
        "URWS023": "BETTERAVE",
    }

    def _from_udb_material(self, udb_code):
        if udb_code not in self.conversion_mapping:
            raise UDBConversionError(f"Unknown UDB Material code: {udb_code}")

        return self.conversion_mapping[udb_code]

    def from_udb_biofuel_code(self, udb_code):
        carbure_code = self._from_udb_material(udb_code)
        return Biocarburant.objects.get(code=carbure_code)

    def from_udb_feedstock_code(self, udb_code):
        carbure_code = self._from_udb_material(udb_code)
        return MatierePremiere.biofuel.get(code=carbure_code)


class QuantityConverter(BaseConverter):
    _default_conversion_mapping = {
        "SL": (CarbureLot.volume.field.name, (lambda x: x)),
        "MWh": (CarbureLot.lhv_amount.field.name, (lambda x: x * 3600)),
    }

    def from_udb(self, unit, quantity):
        if unit not in self.conversion_mapping:
            raise UDBConversionError(f"Unknown UDB Unit: {unit}")

        (attribute, conversion_function) = self.conversion_mapping.get(unit)
        return {attribute: conversion_function(quantity)}
