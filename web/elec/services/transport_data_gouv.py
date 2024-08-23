import os
from typing import Iterable

import pandas as pd
import requests
from dateutil.parser import isoparse

from core.utils import is_true


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

    CSV_COLUMNS_MERGE = {
        "id_station_itinerance": "first",
        "nom_station": "first",
        "id_pdc_itinerance": "first",
        "coordonneesXY": "first",
        "puissance_nominale": "max",
        "prise_type_combo_ccs": "max",
        "prise_type_chademo": "max",
        "date_maj": "max",
        "last_modified": "max",
        "nom_amenageur": "first",
        "siren_amenageur": "first",
    }

    DB_COLUMNS = [
        "line",
        "charge_point_id",
        "installation_date",
        "mid_id",
        "measure_date",
        "measure_energy",
        "measure_reference_point_id",
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
        "is_in_tdg",
    ]

    @staticmethod
    def merge_charge_point_data(charge_point_data: pd.DataFrame, chunksize=1000):
        file_path = TransportDataGouv.download_csv()

        # list the different charge point ids from the application
        wanted_ids = charge_point_data["charge_point_id"].unique().tolist()

        # find all the different stations for the application's charge points
        wanted_stations = set()
        for chunk in TransportDataGouv.read_transport_data_chunks(file_path, chunksize):
            wanted_chunk = chunk[chunk["id_pdc_itinerance"].isin(wanted_ids)]
            wanted_stations.update(wanted_chunk["id_station_itinerance"].unique())

        # find all the charge points for all these stations
        transport_data = pd.DataFrame(columns=TransportDataGouv.CSV_COLUMNS)
        for chunk in TransportDataGouv.read_transport_data_chunks(file_path, chunksize):
            station_charge_points = chunk[chunk["id_station_itinerance"].isin(wanted_stations)]
            transport_data = pd.concat([transport_data, station_charge_points], ignore_index=True)

        # instead of droping duplicate rows, merge their values so we get as much data as possible
        transport_data = (
            transport_data.groupby("id_pdc_itinerance", as_index=False)
            .agg(TransportDataGouv.CSV_COLUMNS_MERGE)
            .reset_index()
        )

        transport_data = transport_data.rename(columns=TransportDataGouv.CSV_COLUMNS_ALIAS)
        transport_data = transport_data.sort_values("date_maj", ascending=False)

        transport_data = transport_data.fillna("")

        # mark the charge points as coming from TDG
        transport_data["is_in_tdg"] = True

        return TransportDataGouv.enrich_charge_point_data(charge_point_data, transport_data)

    @staticmethod
    def download_csv():
        # fetch latest data about the file from data.gouv.fr API
        api_response = requests.get(TransportDataGouv.URL)

        if api_response.status_code != 200:
            raise Exception("Dataset was not found on data.gouv.fr API")

        data = api_response.json()

        dataset_url: str = data["resources"][0]["latest"]
        last_modified = isoparse(data["resources"][0]["last_modified"])
        file_path = f"/tmp/transport_data_gouv_charge_points_{last_modified:%Y-%m-%d_%H-%M-%S}.csv"

        # cache the csv to the filesystem to avoid refetching it every time
        if not os.path.exists(file_path):
            csv_response = requests.get(dataset_url)
            with open(file_path, "wb") as file:
                file.write(csv_response.content)

        return file_path

    @staticmethod
    def read_transport_data_chunks(file_path: str, chunksize=1000) -> Iterable[pd.DataFrame]:
        transport_data = pd.read_csv(
            file_path,
            sep=",",
            header=0,
            usecols=TransportDataGouv.CSV_COLUMNS,
            parse_dates=["last_modified", "date_maj"],
            dayfirst=False,
            encoding="utf-8",
            engine="python",
            dtype={"prise_type_combo_ccs": "str", "prise_type_chademo": "str", "siren_amenageur": "str"},
            skip_blank_lines=True,
            chunksize=chunksize,
        )

        return transport_data

    @staticmethod
    def enrich_charge_point_data(charge_point_data: pd.DataFrame, transport_data: pd.DataFrame):
        longitude = [coord.replace("[", "").replace("]", "").replace(u'\xa0', u'').split(",")[0] for coord in transport_data.coordonneesXY]  # fmt:skip
        latitude = [coord.replace("[", "").replace("]", "").replace(u'\xa0', u'').split(",")[1] for coord in transport_data.coordonneesXY]  # fmt:skip

        transport_data["latitude"] = latitude
        transport_data["longitude"] = longitude

        transport_data["operating_unit"] = transport_data["charge_point_id"].str[:5]

        # convert nominal power to always be in megawatts
        transport_data.loc[transport_data.nominal_power > 1000, "nominal_power"] = (
            transport_data.loc[transport_data.nominal_power > 1000, "nominal_power"] / 1000
        )

        # check if each charge point is using direct current
        transport_data["prise_type_combo_ccs"] = is_true(transport_data, "prise_type_combo_ccs")
        transport_data["prise_type_chademo"] = is_true(transport_data, "prise_type_chademo")
        transport_data.insert(0, "DC", transport_data["prise_type_combo_ccs"] | transport_data["prise_type_chademo"])  # fmt:skip
        transport_data["guessed_current_type"] = transport_data["DC"].apply(lambda is_dc: "DC" if is_dc else "AC")

        # find all stations that contain at least one DC point
        stations_art2 = transport_data[["station_id", "DC"]].groupby("station_id").max()
        stations_art2 = stations_art2.rename(columns={"DC": "guessed_is_article_2"})

        # mark all the charge points of these stations as eligible to article 2
        transport_data = transport_data.merge(stations_art2, on="station_id")

        # merge the imported excel data with transport.data.gouv data to have all info in one place
        merged_data = charge_point_data.merge(transport_data, on="charge_point_id", how="outer", suffixes=("_old", "_new"))

        # get the newest value for each column shared between the application charge point data and TDG
        shared_columns = charge_point_data.columns.intersection(transport_data.columns).difference(["charge_point_id"])
        for col in shared_columns:
            merged_data[col] = merged_data[col + "_new"].combine_first(merged_data[col + "_old"])

        # remove the duplicated columns
        merged_data = merged_data.drop(
            columns=[col + "_old" for col in shared_columns] + [col + "_new" for col in shared_columns]
        )

        # for current type, use the data filled by the user, or use the one guessed from TDG
        merged_data["current_type"] = merged_data["current_type"].replace("CC", "DC").replace("CA", "AC")
        merged_data["current_type"] = merged_data["current_type"].replace("", pd.NA)
        merged_data["current_type"] = merged_data["current_type"].fillna(merged_data["guessed_current_type"])

        # deal with when a charge point was not found on TDG to compute its guessed_is_article_2 column
        if "guessed_is_article_2" in merged_data.columns:
            merged_data["guessed_is_article_2"] = merged_data["guessed_is_article_2"].fillna(merged_data["current_type"] != "AC")  # fmt:skip
        else:
            merged_data["guessed_is_article_2"] = merged_data["current_type"] != "AC"

        # tag the origin of the data
        merged_data["is_in_tdg"] = merged_data["is_in_tdg"] is True
        merged_data["is_in_application"] = merged_data["is_in_application"] is True

        # clear the mid and prm columns if they contain data that is too short
        # merged_data["mid_id"] = merged_data["mid_id"].apply(lambda x: "" if not x or len(str(x)) < 3 else x)
        # merged_data["measure_reference_point_id"] = merged_data["measure_reference_point_id"].apply(lambda x: "" if not x or len(str(x)) < 3 else x)  # fmt:skip

        # find which rows have all data defined for a first meter reading
        merged_data["has_reading"] = (merged_data["current_type"] == "AC") | (
            (merged_data["mid_id"] != "") & merged_data["measure_date"].notna() & merged_data["measure_energy"].notna()
        )

        # fill the empty cells now that all transformation requiring NaN checks are done
        merged_data = merged_data.fillna("")

        # check if all the charge points of a same station all have readings defined
        # in that case, they won't be considered for article 2, even if there are DC charge points
        merged_data["whole_station_has_readings"] = (
            merged_data.groupby("station_id")["has_reading"]
            .transform(lambda x: all(x is not False))
            .reset_index()["has_reading"]
        )

        # for article 2, use the data filled by the user or combine the info we get from TDG with the computations above
        merged_data["guessed_is_article_2"] = (
            ~merged_data["whole_station_has_readings"] & merged_data["guessed_is_article_2"]
        )

        merged_data["is_article_2"] = merged_data["is_article_2"].replace("", pd.NA)
        merged_data["is_article_2"] = merged_data["is_article_2"].fillna(merged_data["guessed_is_article_2"])
        merged_data["is_article_2"] = is_true(merged_data, "is_article_2")

        # remove the charge points that were not listed in the original imported excel file
        return merged_data[merged_data["is_in_application"] is True][TransportDataGouv.DB_COLUMNS]
