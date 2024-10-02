from collections import defaultdict
import pandas as pd
from typing import Iterable
from django.core.files.uploadedfile import UploadedFile
from django.utils.translation import gettext_lazy as _
from django import forms
from django.db.models import QuerySet
from core.utils import Validator
from elec.models.elec_charge_point import ElecChargePoint
from elec.models.elec_meter_reading import ElecMeterReading
from elec.models.elec_meter_reading_application import ElecMeterReadingApplication
from elec.services.create_meter_reading_excel import (
    get_previous_readings_by_charge_point,
)


def import_meter_reading_excel(
    excel_file: UploadedFile,
    existing_charge_points: Iterable[ElecChargePoint],
    previous_readings: QuerySet[ElecMeterReading],
    previous_application: ElecMeterReadingApplication = None,
    renewable_share: int = 1,
):
    original_meter_readings_data = ExcelMeterReadings.parse_meter_reading_excel(
        excel_file
    )
    meter_readings_data = ExcelMeterReadings.validate_meter_readings(
        original_meter_readings_data,
        existing_charge_points,
        previous_readings,
        previous_application,
        renewable_share,
    )
    return meter_readings_data[0], meter_readings_data[1], original_meter_readings_data  # fmt:skip


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
        meter_readings_data["line"] = (
            meter_readings_data.index + 2
        )  # add a line number to locate data in the excel file
        meter_readings_data.rename(
            columns={
                meter_readings_data.columns[i]: column
                for i, column in enumerate(ExcelMeterReadings.EXCEL_COLUMNS)
            },
            inplace=True,
        )
        meter_readings_data["reading_date"] = meter_readings_data[
            "reading_date"
        ].astype(str)
        meter_readings_data = meter_readings_data.drop_duplicates("charge_point_id")
        meter_readings_data.dropna(inplace=True)

        return meter_readings_data.to_dict(orient="records")

    @staticmethod
    def validate_meter_readings(
        meter_readings: list[dict],
        registered_charge_points: Iterable[ElecChargePoint],
        previous_readings: QuerySet[ElecMeterReading],
        previous_application: ElecMeterReadingApplication = None,
        renewable_share: int = 1,
    ):
        charge_point_by_id = {cp.charge_point_id: cp for cp in registered_charge_points}
        previous_readings_by_charge_point = get_previous_readings_by_charge_point(
            registered_charge_points, previous_application
        )

        previous_reading_dates_by_charge_point = defaultdict(list)
        for reading in previous_readings:
            previous_reading_dates_by_charge_point[reading.charge_point_id].append(
                reading.reading_date
            )

        context = {
            "renewable_share": renewable_share,
            "charge_point_by_id": charge_point_by_id,
            "previous_readings_by_charge_point": previous_readings_by_charge_point,
            "previous_reading_dates_by_charge_point": previous_reading_dates_by_charge_point,
        }

        return ExcelMeterReadingValidator.bulk_validate(meter_readings, context)


class ExcelMeterReadingValidator(Validator):
    charge_point_id = forms.IntegerField()
    extracted_energy = forms.FloatField(min_value=0)
    reading_date = forms.DateField(input_formats=Validator.DATE_FORMATS)
    renewable_energy = forms.FloatField()

    def extend(self, meter_reading):
        renewable_share = self.context.get("renewable_share")

        charge_point_id = meter_reading.get("charge_point_id")
        charge_point_by_id = self.context.get("charge_point_by_id")
        charge_point = charge_point_by_id.get(charge_point_id)

        previous_readings_by_charge_point = self.context.get(
            "previous_readings_by_charge_point"
        )
        previous_extracted_energy = (
            previous_readings_by_charge_point.get(charge_point_id) or 0
        )

        self.context["charge_point"] = charge_point
        self.context["previous_extracted_energy"] = previous_extracted_energy

        meter_reading["charge_point_id"] = charge_point.pk if charge_point else None
        meter_reading["renewable_energy"] = (meter_reading["extracted_energy"] - previous_extracted_energy) * renewable_share  # fmt:skip

        return meter_reading

    def validate(self, meter_reading):
        charge_point = self.context.get("charge_point")
        previous_extracted_energy = self.context.get("previous_extracted_energy")
        previous_reading_dates_by_charge_point = self.context.get(
            "previous_reading_dates_by_charge_point"
        )

        if charge_point is None:
            self.add_error(
                "charge_point_id",
                _("Le point de recharge n'a pas encore été inscrit sur la plateforme."),
            )
        elif meter_reading.get("extracted_energy", 0) < previous_extracted_energy:
            self.add_error(
                "extracted_energy",
                _("La quantité d'énergie soutirée est inférieure au précédent relevé."),
            )

        charge_point_reading_dates = previous_reading_dates_by_charge_point.get(
            meter_reading.get("charge_point_id"), []
        )
        if meter_reading.get("reading_date") in charge_point_reading_dates:
            self.add_error(
                "reading_date",
                _(f"Le relevé du {meter_reading.get("reading_date")} existe déjà"),
            )
