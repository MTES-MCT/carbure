from typing import Any
import pandas as pd
from django.core.files.uploadedfile import UploadedFile, SimpleUploadedFile

# Excel file columns:
# Identifiant du point de recharge communiqué à transport.data.gouv
# Type de courant
# Date d'installation (ou 01/01/2022 si antérieur)
# Numéro LNE du certificat d'examen du type
# Date du relevé
# Energie active totale soutirée à la date du relevé
# Décompte à partir du compteur point référence mesure du gestionnaire du réseau de distribution
# Auto-consommation
# Demande de régularisation prévue par l'article 4 (du 1er janvier 2022 à la date de publication du décret
# Numéro du point référence mesure du gestionnaire du réseau public de distribution alimentant la station

COLUMNS = {
    0: "charge_point_id",
    1: "current_type",
    2: "installation_date",
    3: "lne_certificate",
    4: "meter_reading_date",
    5: "meter_reading_energy",
    6: "is_using_reference_meter",
    7: "is_auto_consumption",
    8: "has_article_4_regularization",
    9: "reference_meter_id",
}


def parse_charge_point_excel(excel_file: UploadedFile):
    charge_point_data = pd.read_excel(excel_file, skiprows=11, usecols=list(range(1, 11)))
    charge_point_data.rename(columns={charge_point_data.columns[i]: COLUMNS[i] for i in COLUMNS}, inplace=True)

    charge_points = charge_point_data.to_dict(orient="records")

    first_id = charge_points[0]["charge_point_id"]
    eighteenth_id = charge_points[17]["charge_point_id"]

    # the example was left in the template, so we remove it
    if first_id == "FRUEXESTATION1P1" and eighteenth_id == "FRUEXESTATION4P4":
        charge_points = charge_points[22:]

    # @TODO convert cell values to match their destination type

    return charge_points
