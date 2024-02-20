import traceback
from django import forms
import pandas as pd
from django.core.files.uploadedfile import UploadedFile
from core.utils import Validator
from elec.models.elec_charge_point import ElecChargePoint
from elec.services.transport_data_gouv import TransportDataGouv


class ExcelChargePointError:
    EXCEL_PARSING_FAILED = "EXCEL_PARSING_FAILED"
    DUPLICATE_CHARGE_POINT = "DUPLICATE_CHARGE_POINT"
    MISSING_CHARGE_POINT_ID = "MISSING_CHARGE_POINT_ID"
    MISSING_CHARGE_POINT_IN_DATAGOUV = "MISSING_CHARGE_POINT_IN_DATAGOUV"
    MISSING_CHARGE_POINT_DATA = "MISSING_CHARGE_POINT_DATA"


def import_charge_point_excel(excel_file: UploadedFile, existing_charge_points: list[str]):
    try:
        # return the content of the excel file, indexed by their line number, in the form of a list of dicts holding strings only
        excel_data = ExcelChargePoints.parse_charge_point_excel(excel_file)
        # find the TDG data related to the charge points listed in the imported excel file
        transport_data = TransportDataGouv.find_charge_point_data(excel_data, 1000)
        # parse the data and validate errors
        return ExcelChargePoints.validate_charge_points(excel_data, transport_data, existing_charge_points)  # fmt:skip
    except:
        traceback.print_exc()
        return [], [{"error": ExcelChargePointError.EXCEL_PARSING_FAILED}]


class ExcelChargePoints:
    EXCEL_COLUMNS = {
        "charge_point_id": ["Identifiant du point de recharge communiqué à transport.data.gouv"],
        "installation_date": ["Date d'installation (ou 01/01/2022 si antérieur)"],
        "mid_id": ["Numéro MID du certificat d'examen du type", "Numéro LNE du certificat d'examen du type"],
        "measure_date": ["Date du relevé"],
        "measure_energy": ["Energie active totale soutirée à la date du relevé"],
        "measure_reference_point_id": ["Numéro du point référence mesure du gestionnaire du réseau public de distribution alimentant la station"],  # fmt:skip
    }

    @staticmethod
    def parse_charge_point_excel(excel_file: UploadedFile):
        charge_point_data = pd.read_excel(excel_file, usecols=list(range(1, 7)), dtype=str)

        # check that the template has the right columns
        for i, header in enumerate(ExcelChargePoints.EXCEL_COLUMNS.values()):
            if charge_point_data.iloc[9, i].strip() not in header:
                raise Exception("Invalid template")

        charge_point_data = charge_point_data.drop(charge_point_data.index[:11])
        charge_point_data = charge_point_data.dropna(how="all")  # remove completely empty rows
        charge_point_data = charge_point_data.fillna("")
        charge_point_data["line"] = charge_point_data.index + 2  # add a line number to locate data in the excel file
        charge_point_data.rename(columns={charge_point_data.columns[i]: column for i, column in enumerate(ExcelChargePoints.EXCEL_COLUMNS)}, inplace=True)  # fmt: skip
        charge_point_data = charge_point_data.reset_index(drop=True)

        if len(charge_point_data) >= 18:
            # default template example cells
            first_id = charge_point_data.at[0, "charge_point_id"]
            eighteenth_id = charge_point_data.at[17, "charge_point_id"]

            # the example was left in the template, so we skip it
            if first_id == "FRUEXESTATION1P1" and eighteenth_id == "FRUEXESTATION4P4":
                charge_point_data = charge_point_data.drop(charge_point_data.index[:19])
                charge_point_data = charge_point_data.reset_index(drop=True)

        return charge_point_data.to_dict(orient="records")

    @staticmethod
    def validate_charge_points(charge_points: list[dict], transport_data, existing_charge_points):
        transport_data_index = {row["charge_point_id"]: row for row in transport_data}

        context = {
            "transport_data_index": transport_data_index,
            "existing_charge_points": existing_charge_points,
        }

        return ExcelChargePointValidator.bulk_validate(charge_points, context)


class ExcelChargePointValidator(Validator):
    # fields from charge point excel template
    charge_point_id = forms.CharField(max_length=64)
    installation_date = forms.DateField(input_formats=Validator.DATE_FORMATS)
    mid_id = forms.CharField(required=False, max_length=128)
    measure_date = forms.DateField(input_formats=Validator.DATE_FORMATS, required=False)
    measure_energy = forms.FloatField(required=False, initial=0)
    measure_reference_point_id = forms.CharField(required=False, max_length=64)

    # fields from transport.data.gouv.fr CSV
    is_article_2 = forms.BooleanField(required=False)
    station_id = forms.CharField(required=False)
    station_name = forms.CharField(required=False)
    nominal_power = forms.FloatField(required=False)
    current_type = forms.ChoiceField(required=False, choices=ElecChargePoint.CURRENT_TYPES)
    cpo_name = forms.CharField(required=False)
    cpo_siren = forms.CharField(required=False)
    latitude = forms.DecimalField(required=False)
    longitude = forms.DecimalField(required=False)

    # grab data from transport.data.gouv.fr to enrich the base charge point data
    def extend(self, charge_point):
        charge_point_id = charge_point.get("charge_point_id")
        charge_point_transport_data = self.context.get("transport_data_index", {}).get(charge_point_id)

        if charge_point_transport_data is None:
            return charge_point

        charge_point["station_id"] = charge_point_transport_data["station_id"]
        charge_point["station_name"] = charge_point_transport_data["station_name"]
        charge_point["nominal_power"] = charge_point_transport_data["nominal_power"]
        charge_point["current_type"] = charge_point_transport_data["current_type"]
        charge_point["is_article_2"] = charge_point_transport_data["is_article_2"]
        charge_point["cpo_name"] = charge_point_transport_data["cpo_name"]
        charge_point["cpo_siren"] = charge_point_transport_data["cpo_siren"]
        charge_point["latitude"] = charge_point_transport_data["latitude"]
        charge_point["longitude"] = charge_point_transport_data["longitude"]

        return charge_point

    # check if the different possible charge point configurations are respected
    # and if the new data doesn't conflict with TDG or our own DB
    def validate(self, charge_point):
        existing_charge_points = self.context.get("existing_charge_points", [])
        transport_data_index = self.context.get("transport_data_index", {})

        if charge_point.get("charge_point_id") in existing_charge_points:
            self.add_error("charge_point_id", "Ce point de recharge a déjà été défini dans un autre dossier d'inscription.")
        elif charge_point.get("charge_point_id") not in transport_data_index:
            self.add_error("charge_point_id", "Ce point de recharge n'est pas listé sur transport.data.gouv.fr")
        else:
            if charge_point.get("is_article_2"):
                if not charge_point.get("measure_reference_point_id"):
                    self.add_error("measure_reference_point_id", "L'identifiant du point de mesure est obligatoire pour les stations ayant au moins un point de recharge en courant continu.")  # fmt:skip
            else:
                if not charge_point.get("mid_id"):
                    self.add_error("mid_id", "Le numéro MID est obligatoire pour les points de recharge en courant alternatif.")  # fmt:skip
                if not charge_point.get("measure_date"):
                    self.add_error("measure_date", "La date du dernier relevé est obligatoire pour les points de recharge en courant alternatif.")  # fmt:skip
                if not isinstance(charge_point.get("measure_energy"), float):
                    self.add_error("measure_energy", "L'énergie mesurée lors du dernier relevé est obligatoire pour les points de recharge en courant alternatif.")  # fmt:skip
