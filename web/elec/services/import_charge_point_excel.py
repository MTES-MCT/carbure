import os
import traceback
from typing import Iterable
import requests
import pandas as pd
from dateutil.parser import isoparse
from django.core.files.uploadedfile import UploadedFile
from core.excel import ExcelParser


def import_charge_point_excel(excel_file: UploadedFile):
    try:
        excel_data = ExcelChargePoints.parse_charge_point_excel(excel_file)
        transport_data = TransportDataGouv.find_charge_point_data(excel_data, 1000)
        return ExcelChargePoints.validate_charge_points(excel_data, transport_data)
    except Exception as e:
        traceback.print_exc()
        return [], [{"error": str(e)}]


class ExcelChargePointError:
    MISSING_CHARGING_POINT_IN_DATAGOUV = "MISSING_CHARGING_POINT_IN_DATAGOUV"
    MISSING_CHARGING_POINT_DATA = "MISSING_CHARGING_POINT_DATA"


class ExcelChargePoints:
    @staticmethod
    def parse_charge_point_excel(excel_file: UploadedFile):
        EXCEL_COLUMNS = {
            "charge_point_id": ExcelParser.id,
            "current_type": ExcelParser.str,
            "installation_date": ExcelParser.date,
            "lne_id": ExcelParser.id,
            "measure_date": ExcelParser.date,
            "measure_energy": ExcelParser.float,
            "is_article_2": ExcelParser.bool,
            "is_auto_consumption": ExcelParser.bool,
            "is_article_4": ExcelParser.bool,
            "measure_reference_point_id": ExcelParser.id,
        }

        charge_point_data = pd.read_excel(excel_file, skiprows=11, usecols=list(range(1, 11)))
        charge_point_data["line"] = charge_point_data.index + 11 + 2
        charge_point_data = charge_point_data.dropna()
        charge_point_data.rename(columns={charge_point_data.columns[i]: column for i, column in enumerate(EXCEL_COLUMNS)}, inplace=True)  # fmt: skip
        charge_point_data.fillna("", inplace=True)

        for column, parser in EXCEL_COLUMNS.items():
            charge_point_data[column] = charge_point_data[column].apply(parser)

        charge_points = charge_point_data.to_dict(orient="records")

        if len(charge_points) >= 18:
            # default template example cells
            first_id = charge_points[0]["charge_point_id"]
            eighteenth_id = charge_points[17]["charge_point_id"]

            # the example was left in the template, so we skip it
            if first_id == "FRUEXESTATION1P1" and eighteenth_id == "FRUEXESTATION4P4":
                charge_points = charge_points[22:]

        return charge_points

    @staticmethod
    def validate_charge_points(charge_points: list[dict], transport_data):
        valid_charge_points = []
        charge_points_errors = []

        transport_data_index = {row["charge_point_id"]: row for row in transport_data}

        for charge_point_data in charge_points:
            line = charge_point_data.pop("line")
            charge_point_transport_data = transport_data_index.get(charge_point_data["charge_point_id"])

            errors = []

            if charge_point_transport_data is None:
                error = {"line": line, "error": ExcelChargePointError.MISSING_CHARGING_POINT_IN_DATAGOUV, "meta": charge_point_data["charge_point_id"]}  # fmt:skip
                errors.append(error)
            else:
                charge_point_data["station_id"] = charge_point_transport_data["station_id"]
                charge_point_data["station_name"] = charge_point_transport_data["station_name"]

                # on override la valeur du excel si transport.data.gouv indique que le point de charge est éligible article 2
                if charge_point_transport_data["should_be_article_2"]:
                    charge_point_data["is_article_2"] = True

            missing_fields = list(ExcelChargePoints.validate_charge_point_fields(charge_point_data))

            if len(missing_fields) > 0:
                errors.append({"line": line, "error": ExcelChargePointError.MISSING_CHARGING_POINT_DATA, "meta": missing_fields})  # fmt:skip

            if len(errors) > 0:
                charge_points_errors += errors
            else:
                valid_charge_points.append(charge_point_data)

        return valid_charge_points, charge_points_errors

    @staticmethod
    def validate_charge_point_fields(charge_point):
        if charge_point.get("is_article_2"):
            if not charge_point.get("measure_reference_point_id"):
                yield "measure_reference_point_id"
        else:
            if not charge_point.get("lne_id"):
                yield "lne_id"
            elif not charge_point.get("measure_date"):
                yield "measure_date"
            elif not charge_point.get("measure_energy"):
                yield "measure_energy"


class TransportDataGouv:
    URL = "https://www.data.gouv.fr/api/1/datasets/5448d3e0c751df01f85d0572/"

    CSV_COLUMNS = [
        "id_station_itinerance",
        "nom_station",
        "id_pdc_itinerance",
        "coordonneesXY",
        "puissance_nominale",
        "prise_type_combo_ccs",
        "prise_type_chademo",
        "date_maj",
        "last_modified",
    ]

    CSV_COLUMNS_ALIAS = {
        "id_pdc_itinerance": "charge_point_id",
        "id_station_itinerance": "station_id",
        "nom_station": "station_name",
    }

    @staticmethod
    def find_charge_point_data(excel_data: list[dict], chunksize: int) -> list[dict]:
        file_path = TransportDataGouv.download_csv()

        wanted_ids = [charge_point["charge_point_id"] for charge_point in excel_data]
        wanted_stations = set()  # list the stations of the wanted charge points

        relevant_charge_points = pd.DataFrame(columns=TransportDataGouv.CSV_COLUMNS)
        chunks = TransportDataGouv.read_charge_point_data(file_path, chunksize)

        for chunk in chunks:
            wanted_chunk = chunk[chunk["id_pdc_itinerance"].isin(wanted_ids)]
            wanted_stations.update(wanted_chunk["id_station_itinerance"].unique())
            station_charge_points = chunk[chunk["id_station_itinerance"].isin(wanted_stations)]
            relevant_charge_points = pd.concat([relevant_charge_points, station_charge_points], ignore_index=True)

        relevant_charge_points = TransportDataGouv.process_charge_point_data(relevant_charge_points)

        return relevant_charge_points.to_dict(orient="records")

    @staticmethod
    def download_csv():
        api_response = requests.get(TransportDataGouv.URL)

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

        return file_path

    @staticmethod
    def read_charge_point_data(file_path: str, chunksize: int = 1000) -> Iterable[pd.DataFrame]:
        charge_point_data_chunks = pd.read_csv(
            file_path,
            sep=",",
            header=0,
            usecols=TransportDataGouv.CSV_COLUMNS,
            parse_dates=["last_modified", "date_maj"],
            dayfirst=False,
            encoding="utf-8",
            engine="python",
            dtype={"prise_type_combo_ccs": "str", "prise_type_chademo": "str"},
            chunksize=chunksize,
        )

        return charge_point_data_chunks

    @staticmethod
    def process_charge_point_data(charge_point_data: pd.DataFrame):
        charge_point_data = charge_point_data.rename(columns=TransportDataGouv.CSV_COLUMNS_ALIAS)
        charge_point_data = charge_point_data.dropna()
        charge_point_data = charge_point_data.sort_values("date_maj", ascending=False)
        charge_point_data = charge_point_data.drop_duplicates("charge_point_id")
        charge_point_data = charge_point_data.fillna("")

        lon = [float(coord.replace("[", "").replace("]", "").split(",")[0]) for coord in charge_point_data.coordonneesXY]
        lat = [float(coord.replace("[", "").replace("]", "").split(",")[1]) for coord in charge_point_data.coordonneesXY]

        charge_point_data["latitude"] = lat
        charge_point_data["longitude"] = lon
        charge_point_data["operating_unit"] = charge_point_data["charge_point_id"].str[:5]

        charge_point_data.loc[charge_point_data.puissance_nominale > 1000, "puissance_nominale"] = (
            charge_point_data.loc[charge_point_data.puissance_nominale > 1000, "puissance_nominale"] / 1000
        )

        # On détermine pour chaque point de charge s'il utilise du DC
        charge_point_data["prise_type_combo_ccs"] = (charge_point_data["prise_type_combo_ccs"].str.lower() == "true") | (charge_point_data["prise_type_combo_ccs"] == "1")  # fmt:skip
        charge_point_data["prise_type_chademo"] = (charge_point_data["prise_type_chademo"].str.lower() == "true") | (charge_point_data["prise_type_chademo"] == "1")  # fmt:skip
        charge_point_data.insert(0, "DC", charge_point_data["prise_type_combo_ccs"] | charge_point_data["prise_type_chademo"])  # fmt:skip

        # On regarde les stations qui comprennent un point de recharge DC
        stations_art2 = charge_point_data[["charge_point_id", "DC"]].groupby("charge_point_id").max()
        stations_art2 = stations_art2.rename(columns={"DC": "should_be_article_2"})

        # On marque tous les points de charge de ces stations comme éligible article 2
        return charge_point_data.merge(stations_art2, on="charge_point_id")[
            ["charge_point_id", "should_be_article_2", "station_name", "station_id"]
        ]
