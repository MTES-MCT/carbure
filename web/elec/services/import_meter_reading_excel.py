from collections import defaultdict
from datetime import date
from typing import Iterable

import pandas as pd
from django import forms
from django.core.files.uploadedfile import UploadedFile
from django.utils.translation import gettext_lazy as _

from core.utils import Validator
from elec.models.elec_charge_point import ElecChargePoint
from elec.models.elec_meter import ElecMeter
from elec.repositories.meter_reading_repository import MeterReadingRepository


def import_meter_reading_excel(
    excel_file: UploadedFile,
    existing_charge_points: Iterable[ElecChargePoint],
    renewable_share: int = 1,
    beginning_of_quarter: date = None,
    end_of_quarter: date = None,
):
    parsed_meter_readings_data = ExcelMeterReadings.parse_meter_reading_excel(excel_file)

    meter_readings_data = ExcelMeterReadings.validate_meter_readings(
        parsed_meter_readings_data,
        existing_charge_points,
        renewable_share,
        beginning_of_quarter,
        end_of_quarter,
    )

    return meter_readings_data[0], meter_readings_data[1]


class ExcelMeterReadings:
    EXCEL_COLUMNS = [
        "charge_point_id",
        "previous_extracted_energy",
        "extracted_energy",
        "reading_date",
    ]

    @staticmethod
    def parse_meter_reading_excel(excel_file: UploadedFile):
        meter_readings_data = pd.read_excel(excel_file, dtype=str, usecols=list(range(0, 4)))
        meter_readings_data["line"] = meter_readings_data.index + 2  # add a line number to locate data in the excel file
        meter_readings_data.rename(
            columns={meter_readings_data.columns[i]: column for i, column in enumerate(ExcelMeterReadings.EXCEL_COLUMNS)},
            inplace=True,
        )
        meter_readings_data.dropna(inplace=True)

        return meter_readings_data.to_dict(orient="records")

    @staticmethod
    def validate_meter_readings(
        meter_readings: list[dict],
        charge_points: Iterable[ElecChargePoint],
        renewable_share: int = 1,
        beginning_of_quarter: date = None,
        end_of_quarter: date = None,
    ):
        charge_points = MeterReadingRepository.annotate_charge_points_with_latest_index(charge_points)
        charge_point_by_id = {cp.charge_point_id: cp for cp in charge_points}

        lines_by_charge_point = defaultdict(list)
        for reading in meter_readings:
            lines_by_charge_point[reading.get("charge_point_id")].append(reading.get("line"))

        context = {
            "renewable_share": renewable_share,
            "charge_point_by_id": charge_point_by_id,
            "lines_by_charge_point": lines_by_charge_point,
            "beginning_of_quarter": beginning_of_quarter,
            "end_of_quarter": end_of_quarter,
        }

        return ExcelMeterReadingValidator.bulk_validate(meter_readings, context)


class ExcelMeterReadingValidator(Validator):
    meter = forms.ModelChoiceField(queryset=ElecMeter.objects.all(), required=False)
    extracted_energy = forms.FloatField(min_value=0)
    reading_date = forms.DateField(input_formats=Validator.DATE_FORMATS)
    # energy_used_since_last_reading = forms.FloatField()
    # renewable_energy = forms.FloatField()
    charge_point_id = forms.CharField()

    def extend(self, meter_reading):
        meter_reading["meter"] = None
        meter_reading["operating_unit"] = None
        return meter_reading

    def validate(self, meter_reading):
        charge_point_id = meter_reading.get("charge_point_id")

        charge_point = self.context.get("charge_point_by_id").get(charge_point_id)

        lines = self.context.get("lines_by_charge_point").get(charge_point_id)

        meter = charge_point.current_meter if charge_point else None
        charge_point_power = charge_point.nominal_power if charge_point else 0

        previous_extracted_energy = 0
        if charge_point and charge_point.latest_reading_index is not None:
            previous_extracted_energy = charge_point.latest_reading_index
        elif meter:
            previous_extracted_energy = meter.initial_index or 0

        previous_extracted_energy = round(previous_extracted_energy, 3)
        new_extracted_energy = round(meter_reading.get("extracted_energy", 0), 3)
        energy_used_since_last_reading = round(new_extracted_energy - previous_extracted_energy, 3)

        previous_reading_date = date.min
        operating_unit = None
        if charge_point and charge_point.latest_reading_date is not None:
            previous_reading_date = charge_point.latest_reading_date
            operating_unit = charge_point.charge_point_id[:5]
        elif meter:
            previous_reading_date = meter.initial_index_date or date.min
            operating_unit = meter.charge_point.charge_point_id[:5] if meter.charge_point else None

        meter_reading["operating_unit"] = operating_unit

        new_reading_date = meter_reading["reading_date"]
        days_since_last_reading = (new_reading_date - previous_reading_date).days

        facteur_de_charge = 0
        if charge_point_power and days_since_last_reading:
            facteur_de_charge = energy_used_since_last_reading / (charge_point_power * days_since_last_reading * 24)

        meter_reading["meter"] = meter

        reading_date = meter_reading.get("reading_date")

        if charge_point is None:
            self.add_error(
                "charge_point_id",
                _("Le point de recharge n'a pas encore été inscrit sur la plateforme."),
            )
        elif meter is None:
            self.add_error(
                "charge_point_id",
                _(
                    "Ce point de recharge n'a pas de compteur associé, veuillez en ajouter un depuis la page dédiée."  # noqa
                ),
            )
        elif new_extracted_energy < previous_extracted_energy:
            self.add_error("extracted_energy", _("La quantité d'énergie soutirée est inférieure au précédent relevé."))

        if len(lines) > 1:
            self.add_error(
                "charge_point_id",
                _("Ce point de recharge a été défini %(count)d fois (lignes %(lines)s)")
                % {"count": len(lines), "lines": ", ".join(str(num) for num in lines)},
            )

        if reading_date < previous_reading_date:
            self.add_error(
                "reading_date",
                _("Un relevé plus récent est déjà enregistré pour ce point de recharge: %(energy)gkWh, %(date)s")
                % {"energy": previous_extracted_energy, "date": previous_reading_date.strftime("%d/%m/%Y")},
            )

        if facteur_de_charge > 1:
            self.add_error(
                "extracted_energy",
                _(
                    "Le facteur de charge estimé depuis le dernier relevé enregistré est supérieur à 100%. Veuillez vérifier les valeurs du relevé ainsi que la puissance de votre point de recharge, renseignée sur TDG."  # noqa: E501
                ),
            )

        if charge_point is not None and charge_point.is_article_2:
            self.add_error(
                "charge_point_id",
                _("Ce point de recharge n'est pas soumis aux relevés trimestriels, veuillez le supprimer du fichier."),
            )

        beginning_of_quarter = self.context.get("beginning_of_quarter")
        end_of_quarter = self.context.get("end_of_quarter")
        if reading_date and beginning_of_quarter and (reading_date < beginning_of_quarter or reading_date > end_of_quarter):
            self.add_error("reading_date", _("La date du relevé ne correspond pas au trimestre traité actuellement."))
