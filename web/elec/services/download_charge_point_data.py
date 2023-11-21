import requests
import pandas as pd
from io import StringIO

URL = "https://www.data.gouv.fr/api/1/datasets/5448d3e0c751df01f85d0572/"


def download_charge_point_data():
    api_response = requests.get(URL)

    if api_response.status_code != 200:
        raise Exception("Dataset was not found on data.gouv.fr API")

    data = api_response.json()
    dataset_url: str = data["resources"][0]["latest"]

    csv_response = requests.get(dataset_url)

    csv = StringIO(csv_response.text)

    charge_point_data = pd.read_csv(csv, sep=",", header=0, usecols=COLUMNS)  # pyright: ignore
    charge_point_data.rename(columns=ALIAS, inplace=True)

    data = charge_point_data.to_dict(orient="records")

    return data


ALIAS = {
    "id_pdc_itinerance": "charge_point_id",
    "id_station_itinerance": "station_id",
    "nom_station": "station_name",
}

COLUMNS = [
    # "nom_amenageur",
    # "siren_amenageur",
    # "contact_amenageur",
    # "nom_operateur",
    # "contact_operateur",
    # "telephone_operateur",
    # "nom_enseigne",
    "id_station_itinerance",
    # "id_station_local",
    "nom_station",
    # "implantation_station",
    # "adresse_station",
    # "code_insee_commune",
    # "coordonneesXY",
    # "nbre_pdc",
    "id_pdc_itinerance",
    # "id_pdc_local",
    # "puissance_nominale",
    # "prise_type_ef",
    # "prise_type_2",
    # "prise_type_combo_ccs",
    # "prise_type_chademo",
    # "prise_type_autre",
    # "gratuit",
    # "paiement_acte",
    # "paiement_cb",
    # "paiement_autre",
    # "tarification",
    # "condition_acces",
    # "reservation",
    # "horaires",
    # "accessibilite_pmr",
    # "restriction_gabarit",
    # "station_deux_roues",
    # "raccordement",
    # "num_pdl",
    # "date_mise_en_service",
    # "observations",
    # "date_maj",
    # "cable_t2_attache",
    # "last_modified",
    # "datagouv_dataset_id",
    # "datagouv_resource_id",
    # "datagouv_organization_or_owner",
    # "created_at",
    # "consolidated_longitude",
    # "consolidated_latitude",
    # "consolidated_code_postal",
    # "consolidated_commune",
    # "consolidated_is_lon_lat_correct",
    # "consolidated_is_code_insee_verified",
]
