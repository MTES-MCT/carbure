from core.models import CarbureLot


class UDBConversionError(RuntimeError):
    def __init__(self, message):
        super().__init__(message)
        self.message = message


class QuantityConverter:
    _udb_unit_to_conversion_function_mapping = {
        "MWh": (CarbureLot.lhv_amount.field.name, (lambda x: x * 3600)),
    }

    def __init__(self, conversion_mapping=None):
        self.conversion_mapping = conversion_mapping if conversion_mapping else self._udb_unit_to_conversion_function_mapping

    def from_udb(self, unit, quantity):
        if unit not in self.conversion_mapping:
            raise UDBConversionError(f"Unknown UDB Unit: {unit}")

        (attribute, conversion_function) = self.conversion_mapping.get(unit)
        return {attribute: conversion_function(quantity)}
