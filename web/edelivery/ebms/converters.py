import json
from os import environ

from core.models.certificate import GenericCertificate
from core.models.lot import CarbureLot


class UDBConversionError(RuntimeError):
    def __init__(self, message):
        super().__init__(message)
        self.message = message


class BaseConverter:
    def __init__(self, conversion_mapping=None, unknown_entry_error_message=""):
        self.conversion_mapping = conversion_mapping if conversion_mapping else self.default_conversion_mapping()
        self.reverse_conversion_mapping = {v: k for k, v in self.conversion_mapping.items()}
        self.unknown_entry_error_message = unknown_entry_error_message

    def default_conversion_mapping(self):
        return {}

    def to_udb(self, carbure_entry):
        if carbure_entry not in self.reverse_conversion_mapping:
            raise UDBConversionError(f"{self.unknown_entry_error_message}: {carbure_entry}")

        return self.reverse_conversion_mapping[carbure_entry]


class CertificateIssuerConverter(BaseConverter):
    def __init__(self, conversion_mapping=None):
        super().__init__(
            conversion_mapping=conversion_mapping,
            unknown_entry_error_message="Unknown Carbure Certificate Issuer",
        )

    def default_conversion_mapping(self):
        json_string = environ.get("CERTIFICATE_ISSUER_CONVERSION_MAPPING", f"{super().default_conversion_mapping()}")
        return json.loads(json_string)


class CertificateStatusConverter(BaseConverter):
    def __init__(self, conversion_mapping=None):
        super().__init__(conversion_mapping=conversion_mapping, unknown_entry_error_message="Unknown Carbure Status")

    def default_conversion_mapping(self):
        return {
            "Valid": GenericCertificate.VALID,
            "Suspended": GenericCertificate.SUSPENDED,
            "Withdrawn": GenericCertificate.WITHDRAWN,
            "Cancelled": GenericCertificate.TERMINATED,
            "Expired": GenericCertificate.EXPIRED,
        }


class MaterialConverter(BaseConverter):
    def default_conversion_mapping(self):
        return {
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
    def default_conversion_mapping(self):
        return {
            "SL": (CarbureLot.volume.field.name, (lambda x: x)),
            "MWh": (CarbureLot.lhv_amount.field.name, (lambda x: x * 3600)),
        }

    def from_udb(self, unit, quantity):
        if unit not in self.conversion_mapping:
            raise UDBConversionError(f"Unknown UDB Unit: {unit}")

        (attribute, conversion_function) = self.conversion_mapping.get(unit)
        return {attribute: conversion_function(quantity)}


class TransactionStatusConverter(BaseConverter):
    def default_conversion_mapping(self):
        return {
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
