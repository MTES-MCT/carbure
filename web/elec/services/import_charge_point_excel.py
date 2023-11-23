import os
import requests
import pandas as pd
from dateutil.parser import isoparse
from django.core.files.uploadedfile import UploadedFile


def import_charge_point_excel(excel_file: UploadedFile):
    excel_data = parse_charge_point_excel(excel_file)
    transport_data = download_charge_point_data()
    return validate_charge_points(excel_data, transport_data)


def parse_charge_point_excel(excel_file: UploadedFile):
    EXCEL_COLUMNS = [
        "charge_point_id",
        "current_type",
        "installation_date",
        "lne_certificate",
        "meter_reading_date",
        "meter_reading_energy",
        "is_using_reference_meter",
        "is_auto_consumption",
        "has_article_4_regularization",
        "reference_meter_id",
    ]

    charge_point_data = pd.read_excel(excel_file, skiprows=11, usecols=list(range(1, 11)))
    charge_point_data.rename(columns={charge_point_data.columns[i]: column for i, column in enumerate(EXCEL_COLUMNS)}, inplace=True)  # fmt: skip

    charge_points = charge_point_data.to_dict(orient="records")

    first_id = charge_points[0]["charge_point_id"]
    eighteenth_id = charge_points[17]["charge_point_id"]

    # the example was left in the template, so we remove it
    if first_id == "FRUEXESTATION1P1" and eighteenth_id == "FRUEXESTATION4P4":
        charge_points = charge_points[22:]

    # @TODO convert cell values to match their destination type

    return charge_points


def download_charge_point_data():
    URL = "https://www.data.gouv.fr/api/1/datasets/5448d3e0c751df01f85d0572/"
    api_response = requests.get(URL)

    if api_response.status_code != 200:
        raise Exception("Dataset was not found on data.gouv.fr API")

    data = api_response.json()

    dataset_url: str = data["resources"][0]["latest"]
    last_modified = isoparse(data["resources"][0]["last_modified"])
    file_path = f"/tmp/transport_charge_points_{last_modified:%Y-%m-%d_%H-%M-%S}.csv"

    # cache the csv to the filesystem to avoid refetching it every time
    if not os.path.exists(file_path):
        csv_response = requests.get(dataset_url)
        with open(file_path, "wb") as file:
            file.write(csv_response.content)

    EXCEL_COLUMNS = [
        "id_station_itinerance",
        "nom_station",
        "id_pdc_itinerance",
    ]

    ALIAS = {
        "id_pdc_itinerance": "charge_point_id",
        "id_station_itinerance": "station_id",
        "nom_station": "station_name",
    }

    charge_point_data = pd.read_csv(file_path, sep=",", header=0, usecols=EXCEL_COLUMNS)  # pyright: ignore
    charge_point_data.rename(columns=ALIAS, inplace=True)

    data = charge_point_data.to_dict(orient="records")

    return data


class ExcelChargePointError:
    MISSING_CHARGING_POINT_IN_DATAGOUV = "MISSING_CHARGING_POINT_IN_DATAGOUV"
    MISSING_CHARGING_POINT_DATA = "MISSING_CHARGING_POINT_DATA"


def validate_charge_points(charge_points, transport_data):
    transport_data_index = {row["charge_point_id"]: row for row in transport_data}

    missing_charge_points = []
    invalid_charge_points = []
    valid_charge_points = []

    for charge_point_data in charge_points:
        is_valid = True
        charge_point_transport_data = transport_data_index.get(charge_point_data["charge_point_id"], {})

        if len(charge_point_transport_data) == 0:
            is_valid = False
            missing_charge_points.append(charge_point_data)

        if not is_charge_point_valid(charge_point_data):
            is_valid = False
            invalid_charge_points.append(charge_point_data)

        if is_valid:
            charge_point_data = {**charge_point_transport_data, **charge_point_data}
            valid_charge_points.append(charge_point_data)

    errors = []
    if len(missing_charge_points) > 0:
        errors.append({"error": ExcelChargePointError.MISSING_CHARGING_POINT_IN_DATAGOUV, "meta": missing_charge_points})
    if len(invalid_charge_points) > 0:
        errors.append({"error": ExcelChargePointError.MISSING_CHARGING_POINT_DATA, "meta": invalid_charge_points})

    return valid_charge_points, errors


def is_charge_point_valid(charge_point):
    # @TODO validate field values
    return True
