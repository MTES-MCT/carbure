from core.models.certificate import GenericCertificate
from core.models.lot import CarbureLot


class UDBConversionError(RuntimeError):
    def __init__(self, message):
        super().__init__(message)
        self.message = message


class BaseConverter:
    _default_conversion_mapping = {}

    def __init__(self, conversion_mapping=None):
        self.conversion_mapping = conversion_mapping if conversion_mapping else self._default_conversion_mapping


class CertificateStatusConverter(BaseConverter):
    _default_conversion_mapping = {
        "Valid": GenericCertificate.VALID,
        "Suspended": GenericCertificate.SUSPENDED,
        "Withdrawn": GenericCertificate.WITHDRAWN,
        "Cancelled": GenericCertificate.TERMINATED,
        "Expired": GenericCertificate.EXPIRED,
    }

    def to_udb(self, carbure_status):
        reverse_mapping = {v: k for k, v in self.conversion_mapping.items()}
        if carbure_status not in reverse_mapping:
            raise UDBConversionError(f"Unknown Carbure Status: {carbure_status}")

        return reverse_mapping[carbure_status]


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
        return self._from_udb_material(udb_code)

    def from_udb_feedstock_code(self, udb_code):
        return self._from_udb_material(udb_code)


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


class StatusConverter(BaseConverter):
    _default_conversion_mapping = {
        "CREATED": "DRAFT",
        "PROVISIONAL": "DRAFT",
        "PENDING": "PENDING",
        "IN_TRANSIT": "PENDING",
        "ACCEPTED": "ACCEPTED",
        "REJECTED": "REJECTED",
        "CANCELLED": "DELETED",
    }

    def from_udb(self, udb_status):
        if udb_status not in self.conversion_mapping:
            raise UDBConversionError(f"Unknown UDB Status: {udb_status}")

        return self.conversion_mapping[udb_status]
