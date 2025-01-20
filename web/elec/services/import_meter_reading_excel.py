from collections import defaultdict
from datetime import date
from typing import Iterable

import pandas as pd
from django import forms
from django.core.files.uploadedfile import UploadedFile
from django.db.models import Max, QuerySet
from django.utils.translation import gettext_lazy as _

from core.utils import Validator
from elec.models.elec_charge_point import ElecChargePoint
from elec.models.elec_meter import ElecMeter
from elec.models.elec_meter_reading import ElecMeterReading


def import_meter_reading_excel(
    excel_file: UploadedFile,
    existing_charge_points: Iterable[ElecChargePoint],
    past_readings: QuerySet[ElecMeterReading],
    renewable_share: int = 1,
    beginning_of_quarter: date = None,
):
    parsed_meter_readings_data = ExcelMeterReadings.parse_meter_reading_excel(excel_file)

    meter_readings_data = ExcelMeterReadings.validate_meter_readings(
        parsed_meter_readings_data,
        existing_charge_points,
        past_readings,
        renewable_share,
        beginning_of_quarter,
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
        registered_charge_points: Iterable[ElecChargePoint],
        past_readings: QuerySet[ElecMeterReading],
        renewable_share: int = 1,
        beginning_of_quarter: date = None,
    ):
        charge_point_by_id = {cp.charge_point_id: cp for cp in registered_charge_points}

        previous_readings = (
            past_readings.order_by("-reading_date")
            .values("meter_id")
            .annotate(Max("reading_date"))
            .values("meter__charge_point__charge_point_id", "extracted_energy", "reading_date")
        )

        previous_readings_by_charge_point = {}
        for previous_reading in previous_readings:
            previous_readings_by_charge_point[previous_reading["meter__charge_point__charge_point_id"]] = previous_reading

        lines_by_charge_point = defaultdict(list)
        for reading in meter_readings:
            lines_by_charge_point[reading.get("charge_point_id")].append(reading.get("line"))

        context = {
            "renewable_share": renewable_share,
            "charge_point_by_id": charge_point_by_id,
            "previous_readings_by_charge_point": previous_readings_by_charge_point,
            "lines_by_charge_point": lines_by_charge_point,
            "beginning_of_quarter": beginning_of_quarter,
        }

        return ExcelMeterReadingValidator.bulk_validate(meter_readings, context)


class ExcelMeterReadingValidator(Validator):
    meter = forms.ModelChoiceField(queryset=ElecMeter.objects.all(), required=False)
    extracted_energy = forms.FloatField(min_value=0)
    reading_date = forms.DateField(input_formats=Validator.DATE_FORMATS)
    energy_used_since_last_reading = forms.FloatField()
    renewable_energy = forms.FloatField()
    charge_point_id = forms.CharField()

    def extend(self, meter_reading):
        meter_reading["meter"] = None
        meter_reading["energy_used_since_last_reading"] = 0
        meter_reading["days_since_last_reading"] = 0
        meter_reading["facteur_de_charge"] = 0
        meter_reading["renewable_energy"] = 0
        return meter_reading

    def validate(self, meter_reading):
        charge_point_id = meter_reading.get("charge_point_id")

        renewable_share = self.context.get("renewable_share")
        charge_point = self.context.get("charge_point_by_id").get(charge_point_id)
        previous_readings = self.context.get("previous_readings_by_charge_point").get(charge_point_id)
        lines = self.context.get("lines_by_charge_point").get(charge_point_id)

        meter = charge_point.current_meter if charge_point else None
        charge_point_power = charge_point.nominal_power if charge_point else 0

        # in case there was no registered reading for this charge point yet
        # prepare an object that looks like previous_readings_by_charge_point based on the inital meter data,
        previous_reading = previous_readings or {
            "extracted_energy": meter.initial_index if meter else 0,
            "reading_date": meter.initial_index_date if meter else date.min,  # not sure about date.today() here
        }

        previous_extracted_energy = previous_reading["extracted_energy"]
        new_extracted_energy = meter_reading["extracted_energy"]
        energy_used_since_last_reading = new_extracted_energy - previous_extracted_energy

        previous_reading_date = previous_reading["reading_date"]
        new_reading_date = meter_reading["reading_date"]
        days_since_last_reading = (new_reading_date - previous_reading_date).days

        facteur_de_charge = 0
        if charge_point_power and days_since_last_reading:
            facteur_de_charge = energy_used_since_last_reading / (charge_point_power * days_since_last_reading * 24)

        meter_reading["meter"] = meter
        meter_reading["energy_used_since_last_reading"] = energy_used_since_last_reading
        meter_reading["days_since_last_reading"] = days_since_last_reading
        meter_reading["facteur_de_charge"] = facteur_de_charge
        meter_reading["renewable_energy"] = energy_used_since_last_reading * renewable_share

        # charge_point = self.context.get("charge_point")
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
        elif meter_reading.get("extracted_energy", 0) < previous_extracted_energy:
            self.add_error(
                "extracted_energy",
                _("La quantité d'énergie soutirée est inférieure au précédent relevé."),
            )

        if len(lines) > 1:
            self.add_error(
                "charge_point_id",
                _(f"Ce point de recharge a été défini {len(lines)} fois (lignes {', '.join(str(num) for num in lines)})"),
            )

        if reading_date < previous_reading_date:
            self.add_error(
                "reading_date",
                _(
                    f"Un relevé plus récent est déjà enregistré pour ce point de recharge: {previous_extracted_energy}kWh, {previous_reading_date:%d/%m/%Y}"  # noqa
                ),
            )

        if facteur_de_charge > 1:
            self.add_error(
                "extracted_energy",
                _(
                    f"Le facteur de charge estimé depuis le dernier relevé enregistré est supérieur à 100%. Veuillez vérifier les valeurs du relevé ainsi que la puissance de votre point de recharge, renseignée sur TDG."  # noqa
                ),
            )

        beginning_of_quarter = self.context.get("beginning_of_quarter")
        if reading_date and beginning_of_quarter and reading_date < beginning_of_quarter:
            self.add_error("reading_date", _("La date du relevé ne correspond pas au trimestre traité actuellement."))
