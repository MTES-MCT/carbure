import pandas as pd
from typing import Iterable
from django.core.files.uploadedfile import UploadedFile
from django import forms
from core.utils import Validator
from elec.models.elec_charge_point import ElecChargePoint
from elec.models.elec_meter_reading_application import ElecMeterReadingApplication
from elec.services.create_meter_reading_excel import get_previous_readings_by_charge_point


class ExcelMeterReadingError:
    INVALID_METER_READING_DATA = "INVALID_METER_READING_DATA"
    CHARGE_POINT_NOT_REGISTERED = "CHARGE_POINT_NOT_REGISTERED"
    EXTRACTED_ENERGY_LOWER_THAN_BEFORE = "EXTRACTED_ENERGY_LOWER_THAN_BEFORE"


def import_meter_reading_excel(
    excel_file: UploadedFile,
    existing_charge_points: Iterable[ElecChargePoint],
    previous_application: ElecMeterReadingApplication = None,
    renewable_share: int = 1,
):
    meter_readings_data = ExcelMeterReadings.parse_meter_reading_excel(excel_file)
    return ExcelMeterReadings.validate_meter_readings(meter_readings_data, existing_charge_points, previous_application, renewable_share)  # fmt:skip


class ExcelMeterReadings:
    EXCEL_COLUMNS = [
        "charge_point_id",
        "previous_extracted_energy",
        "extracted_energy",
        "reading_date",
    ]

    @staticmethod
    def parse_meter_reading_excel(excel_file: UploadedFile):
        meter_readings_data = pd.read_excel(excel_file, usecols=list(range(0, 4)))
        meter_readings_data["line"] = meter_readings_data.index + 2  # add a line number to locate data in the excel file
        meter_readings_data.rename(columns={meter_readings_data.columns[i]: column for i, column in enumerate(ExcelMeterReadings.EXCEL_COLUMNS)}, inplace=True)  # fmt: skip
        meter_readings_data.dropna(inplace=True)

        return meter_readings_data.to_dict(orient="records")

    @staticmethod
    def validate_meter_readings(
        meter_readings: list[dict],
        existing_charge_points: Iterable[ElecChargePoint],
        previous_application: ElecMeterReadingApplication = None,
        renewable_share: int = 1,
    ):
        charge_point_pks_by_id = {cp.charge_point_id: cp.pk for cp in existing_charge_points}
        previous_readings_by_charge_point = get_previous_readings_by_charge_point(existing_charge_points, previous_application)  # fmt:skip

        context = {
            "renewable_share": renewable_share,
            "charge_point_pks_by_id": charge_point_pks_by_id,
            "previous_readings_by_charge_point": previous_readings_by_charge_point,
        }

        return ExcelMeterReadingValidator.bulk_validate(meter_readings, context)


class ExcelMeterReadingValidator(Validator):
    charge_point_id = forms.CharField()
    extracted_energy = forms.FloatField(min_value=0)
    reading_date = forms.DateField(input_formats=Validator.DATE_FORMATS)
    renewable_energy = forms.FloatField()

    def extend(self, meter_reading):
        renewable_share = self.context.get("renewable_share")

        charge_point_id = meter_reading.get("charge_point_id")
        charge_point_pks_by_id = self.context.get("charge_point_pks_by_id")

        previous_readings_by_charge_point = self.context.get("previous_readings_by_charge_point")
        previous_extracted_energy = previous_readings_by_charge_point.get(charge_point_id) or 0
        self.context["previous_extracted_energy"] = previous_extracted_energy

        meter_reading["charge_point_id"] = charge_point_pks_by_id.get(charge_point_id)
        meter_reading["renewable_energy"] = (meter_reading["extracted_energy"] - previous_extracted_energy) * renewable_share  # fmt:skip

        return meter_reading

    def validate(self, meter_reading):
        previous_extracted_energy = self.context.get("previous_extracted_energy")

        if meter_reading.get("charge_point_id") is None:
            self.add_error("charge_point_id", "Le point de recharge n'a pas été inscrit sur la plateforme ou n'est pas concerné par les relevés trimestriels.")  # fmt:skip
        elif meter_reading.get("extracted_energy", 0) < previous_extracted_energy:
            self.add_error("extracted_energy", "La quantité d'énergie soutirée est inférieure au précédent relevé.")
