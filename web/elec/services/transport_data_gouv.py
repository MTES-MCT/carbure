import os
from typing import Iterable
import requests
import pandas as pd
from dateutil.parser import isoparse


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
        "nom_amenageur",
        "siren_amenageur",
    ]

    CSV_COLUMNS_ALIAS = {
        "id_pdc_itinerance": "charge_point_id",
        "id_station_itinerance": "station_id",
        "nom_station": "station_name",
        "puissance_nominale": "nominal_power",
        "nom_amenageur": "cpo_name",
        "siren_amenageur": "cpo_siren",
    }

    @staticmethod
    def find_charge_point_data(charge_points: list[dict], chunksize: int) -> list[dict]:
        file_path = TransportDataGouv.download_csv()

        wanted_ids = [charge_point["charge_point_id"] for charge_point in charge_points]
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
        # fetch latest data about the file from data.gouv.fr API
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
            skip_blank_lines=True,
        )

        return charge_point_data_chunks

    @staticmethod
    def process_charge_point_data(charge_point_data: pd.DataFrame):
        charge_point_data = charge_point_data.rename(columns=TransportDataGouv.CSV_COLUMNS_ALIAS)
        charge_point_data = charge_point_data.sort_values("date_maj", ascending=False)
        charge_point_data = charge_point_data.drop_duplicates("charge_point_id")
        charge_point_data = charge_point_data.fillna("")

        lon = [float(coord.replace("[", "").replace("]", "").split(",")[0]) for coord in charge_point_data.coordonneesXY]
        lat = [float(coord.replace("[", "").replace("]", "").split(",")[1]) for coord in charge_point_data.coordonneesXY]

        charge_point_data["latitude"] = lat
        charge_point_data["longitude"] = lon
        charge_point_data["operating_unit"] = charge_point_data["charge_point_id"].str[:5]

        charge_point_data.loc[charge_point_data.nominal_power > 1000, "nominal_power"] = (
            charge_point_data.loc[charge_point_data.nominal_power > 1000, "nominal_power"] / 1000
        )

        # On détermine pour chaque point de charge s'il utilise du DC
        charge_point_data["prise_type_combo_ccs"] = (charge_point_data["prise_type_combo_ccs"].str.lower() == "true") | (charge_point_data["prise_type_combo_ccs"] == "1")  # fmt:skip
        charge_point_data["prise_type_chademo"] = (charge_point_data["prise_type_chademo"].str.lower() == "true") | (charge_point_data["prise_type_chademo"] == "1")  # fmt:skip
        charge_point_data.insert(0, "DC", charge_point_data["prise_type_combo_ccs"] | charge_point_data["prise_type_chademo"])  # fmt:skip
        charge_point_data["current_type"] = charge_point_data["DC"].apply(lambda is_dc: "DC" if is_dc else "AC")

        # On regarde les stations qui comprennent un point de recharge DC
        stations_art2 = charge_point_data[["station_id", "DC"]].groupby("station_id").max()
        stations_art2 = stations_art2.rename(columns={"DC": "is_article_2"})

        # On marque tous les points de charge de ces stations comme éligible article 2
        return charge_point_data.merge(stations_art2, on="station_id")[
            [
                "charge_point_id",
                "current_type",
                "is_article_2",
                "station_name",
                "station_id",
                "nominal_power",
                "cpo_name",
                "cpo_siren",
                "latitude",
                "longitude",
            ]
        ]
