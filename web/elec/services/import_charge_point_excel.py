import traceback

import pandas as pd
from django import forms
from django.core.files.uploadedfile import UploadedFile
from django.utils.translation import gettext_lazy as _

from core.utils import Validator
from elec.models.elec_charge_point import ElecChargePoint
from elec.services.transport_data_gouv import TransportDataGouv

"""
Résumé de l'algo:

- on récupère la liste des stations du dossier d'inscription
- on récupère TOUS les pdc associés à ces stations, en incluant ceux mentionnés uniquement sur TDG
- pour chaque station, on checke:
    - est-ce que tous les points ont un compteur MID => alors pas article 2
    - sinon est-ce que tous les points sont AC => alors pas article 2
    - sinon article 2 (il y a au moins un point DC sans compteur MID dans la station)
"""


class ExcelChargePointError:
    EXCEL_PARSING_FAILED = "EXCEL_PARSING_FAILED"
    DUPLICATE_CHARGE_POINT = "DUPLICATE_CHARGE_POINT"
    MISSING_CHARGE_POINT_ID = "MISSING_CHARGE_POINT_ID"
    MISSING_CHARGE_POINT_IN_DATAGOUV = "MISSING_CHARGE_POINT_IN_DATAGOUV"
    MISSING_CHARGE_POINT_DATA = "MISSING_CHARGE_POINT_DATA"


def import_charge_point_excel(excel_file: UploadedFile):
    try:
        # return the content of the excel file, indexed by their line number, in the form of a list of dicts holding strings only  # noqa: E501
        original_charge_point_data = ExcelChargePoints.parse_charge_point_excel(excel_file)
        # find the TDG data related to the charge points listed in the imported excel file
        merged_charge_point_data = TransportDataGouv.merge_charge_point_data(original_charge_point_data)
        merged_charge_point_data.loc[
            (merged_charge_point_data["nominal_power"].isna()) | (merged_charge_point_data["nominal_power"] == 0),
            "nominal_power",
        ] = merged_charge_point_data["manual_nominal_power"]

        # parse the data and validate errors
        charge_point_data = ExcelChargePoints.validate_charge_points(merged_charge_point_data)
        return charge_point_data[0], charge_point_data[1], original_charge_point_data
    except Exception:
        traceback.print_exc()
        return [], [{"error": ExcelChargePointError.EXCEL_PARSING_FAILED}], []


class ExcelChargePoints:
    EXCEL_COLUMNS = {
        "charge_point_id": ["Identifiant du point de recharge communiqué à transport.data.gouv"],
        "installation_date": ["Date d'installation (ou 01/01/2022 si antérieur)"],
        "mid_id": ["Numéro MID du certificat d'examen du type", "Numéro LNE du certificat d'examen du type"],
        "measure_date": ["Date du relevé"],
        "measure_energy": ["Energie active totale soutirée à la date du relevé"],
        "measure_reference_point_id": [
            "Numéro du point référence mesure du gestionnaire du réseau public de distribution alimentant la station"
        ],
        "_": [""],
        "current_type": ["Type de courant électrique associé au point de recharge"],
        "is_article_2": ["La station du point de recharge est soumise à l'article 2 du décret n°2022-1330"],
        "manual_nominal_power": ["Puissance nominale"],
    }

    @staticmethod
    def parse_charge_point_excel(excel_file: UploadedFile):
        charge_point_data = pd.read_excel(excel_file, dtype=str, header=None)

        # remove empty first column
        charge_point_data.drop(charge_point_data.columns[0], axis=1, inplace=True)

        column_count = len(charge_point_data.columns)
        columns = dict(list(ExcelChargePoints.EXCEL_COLUMNS.items())[0:column_count])

        # remove empty separator column
        if column_count <= 6:
            charge_point_data["current_type"] = ""
            charge_point_data["is_article_2"] = ""

        # check that the template has the right columns
        # for i, header in enumerate(columns.values()):
        #     if charge_point_data.iloc[9, i].strip() not in header:
        #         raise Exception("Invalid template")

        # rename columns with actual names
        charge_point_data.rename(
            columns={charge_point_data.columns[i]: column for i, column in enumerate(columns)}, inplace=True
        )

        charge_point_data["measure_energy"] = charge_point_data["measure_energy"].fillna(0)
        charge_point_data = charge_point_data.fillna("")
        charge_point_data["line"] = charge_point_data.index + 1  # add a line number to locate data in the excel file
        charge_point_data["is_in_application"] = True
        charge_point_data = charge_point_data.reset_index(drop=True)

        # drop example rows
        if len(charge_point_data) >= 24:
            # default template example cells
            first_example_id = charge_point_data.at[12, "charge_point_id"]
            last_example_id = charge_point_data.at[29, "charge_point_id"]

            # the example was left in the template, so we skip it
            if first_example_id == "FRUEXESTATION1P1" and last_example_id == "FRUEXESTATION4P4":
                charge_point_data = charge_point_data.drop(charge_point_data.index[:34])
                charge_point_data = charge_point_data.reset_index(drop=True)

        # strip whitespaces around cell data for better matching later
        charge_point_data = charge_point_data.map(lambda x: x.strip() if isinstance(x, str) else x)

        return charge_point_data.drop_duplicates("charge_point_id")

    def validate_charge_points(
        charge_point_data: pd.DataFrame,
    ):
        charge_points = charge_point_data.to_dict(orient="records")
        return ExcelChargePointValidator.bulk_validate(charge_points)


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
        charge_point_id = charge_point.get("charge_point_id")

        if not self.data.get("is_in_tdg"):
            self.add_error(
                "charge_point_id",
                _(
                    "Le point de recharge {charge_point_id} n'est pas listé dans les données consolidées de transport.data.gouv.fr"  # noqa: E501
                ).format(charge_point_id=charge_point_id),
            )
        else:
            if not charge_point.get("nominal_power"):
                self.add_error("nominal_power", _("La puissance nominale est obligatoire"))
            if charge_point.get("is_article_2"):
                if not charge_point.get("measure_reference_point_id"):
                    self.add_error(
                        "measure_reference_point_id",
                        _(
                            "L'identifiant du point de mesure est obligatoire pour les stations ayant au moins un point de recharge en courant continu."  # noqa: E501
                        ),
                    )
            else:
                if not charge_point.get("mid_id"):
                    self.add_error("mid_id", _("Le numéro MID est obligatoire."))
                if not charge_point.get("measure_date"):
                    self.add_error("measure_date", _("La date du dernier relevé est obligatoire."))
                if not isinstance(charge_point.get("measure_energy"), float):
                    self.add_error("measure_energy", _("L'énergie mesurée lors du dernier relevé est obligatoire."))
