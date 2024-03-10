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


def import_charge_point_excel(excel_file: UploadedFile, registered_charge_points: list[str]):
    try:
        # return the content of the excel file, indexed by their line number, in the form of a list of dicts holding strings only
        charge_point_data = ExcelChargePoints.parse_charge_point_excel(excel_file)
        # find the TDG data related to the charge points listed in the imported excel file
        charge_point_data = TransportDataGouv.merge_charge_point_data(charge_point_data)
        # parse the data and validate errors
        return ExcelChargePoints.validate_charge_points(charge_point_data, registered_charge_points)  # fmt:skip
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
        charge_point_data.rename(columns={charge_point_data.columns[i]: column for i, column in enumerate(ExcelChargePoints.EXCEL_COLUMNS)}, inplace=True)  # fmt: skip
        charge_point_data["measure_energy"] = charge_point_data["measure_energy"].fillna(0)
        charge_point_data = charge_point_data.fillna("")
        charge_point_data["line"] = charge_point_data.index + 2  # add a line number to locate data in the excel file
        charge_point_data["is_in_application"] = True
        charge_point_data = charge_point_data.reset_index(drop=True)

        if len(charge_point_data) >= 18:
            # default template example cells
            first_id = charge_point_data.at[0, "charge_point_id"]
            eighteenth_id = charge_point_data.at[17, "charge_point_id"]

            # the example was left in the template, so we skip it
            if first_id == "FRUEXESTATION1P1" and eighteenth_id == "FRUEXESTATION4P4":
                charge_point_data = charge_point_data.drop(charge_point_data.index[:19])
                charge_point_data = charge_point_data.reset_index(drop=True)

        return charge_point_data

    def validate_charge_points(
        charge_point_data: pd.DataFrame,
        registered_charge_points: list[str],
    ):
        charge_points = charge_point_data.to_dict(orient="records")
        context = {"registered_charge_points": registered_charge_points}

        return ExcelChargePointValidator.bulk_validate(charge_points, context)


class ExcelChargePointValidator(Validator):
    # fields from charge point excel template
    charge_point_id = forms.CharField(max_length=64)
    installation_date = forms.DateField(input_formats=Validator.DATE_FORMATS)
    mid_id = forms.CharField(required=False, max_length=128)
    measure_date = forms.DateField(required=False, input_formats=Validator.DATE_FORMATS)
    measure_energy = forms.FloatField(required=False, min_value=0)
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

    # check if the different possible charge point configurations are respected
    # and if the new data doesn't conflict with TDG or our own DB
    def validate(self, charge_point):
        if charge_point.get("charge_point_id") in self.context.get("registered_charge_points", []):
            self.add_error("charge_point_id", "Ce point de recharge a déjà été défini dans un autre dossier d'inscription.")
        elif not self.data.get("is_in_tdg"):
            self.add_error("charge_point_id", "Ce point de recharge n'est pas listé sur transport.data.gouv.fr")
        else:
            if charge_point.get("is_article_2"):
                if not charge_point.get("measure_reference_point_id"):
                    self.add_error("measure_reference_point_id", "L'identifiant du point de mesure est obligatoire pour les stations ayant au moins un point de recharge en courant continu.")  # fmt:skip
            else:
                if not charge_point.get("mid_id"):
                    self.add_error("mid_id", "Le numéro MID est obligatoire.")
                if not charge_point.get("measure_date"):
                    self.add_error("measure_date", "La date du dernier relevé est obligatoire.")
                if not isinstance(charge_point.get("measure_energy"), float):
                    self.add_error("measure_energy", "L'énergie mesurée lors du dernier relevé est obligatoire.")  # fmt:skip
