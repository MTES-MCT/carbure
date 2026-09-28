import csv
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import pandas as pd
from pandas.testing import assert_frame_equal

from elec.services.transport_data_gouv import TransportDataGouv

FIXTURE_PATH = Path(os.environ["CARBURE_HOME"]) / "web/elec/fixtures/transport_data_gouv.csv"

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


def transport_data(file_path, charge_point_ids, chunksize=1000):
    charge_points = pd.DataFrame({"charge_point_id": charge_point_ids})
    with patch.object(TransportDataGouv, "download_csv", return_value=str(file_path)):
        return TransportDataGouv.get_transport_data(charge_points, chunksize)


class TransportDataGouvTest(unittest.TestCase):
    def test_selecting_one_charge_point_returns_its_whole_station(self):
        result = transport_data(FIXTURE_PATH, ["FRAAAA111101"])

        self.assertEqual(
            set(result["charge_point_id"]),
            {"FRAAAA111101", "FRAAAA111102", "FRAAAA111103"},
        )
        point = result.set_index("charge_point_id").loc["FRAAAA111101"]
        self.assertEqual(point["station_id"], "FRAAAA1111")
        self.assertEqual(point["station_name"], "Hotel Saint Sauveur")
        self.assertEqual(point["nominal_power"], 22)
        self.assertEqual(point["coordonneesXY"], "[3.407609123225763, 43.41959147913006]")
        self.assertEqual(point["prise_type_combo_ccs"], "FALSE")
        self.assertEqual(point["prise_type_chademo"], "FALSE")
        self.assertEqual(point["cpo_name"], "AMENAGEUR")
        self.assertEqual(point["cpo_siren"], "379629447")
        self.assertTrue(point["is_in_tdg"])

    def test_unknown_charge_point_returns_no_row(self):
        result = transport_data(FIXTURE_PATH, ["DOES_NOT_EXIST"])

        self.assertTrue(result.empty)
        self.assertIn("charge_point_id", result.columns)
        self.assertIn("is_in_tdg", result.columns)

    def test_duplicate_rows_are_merged_per_charge_point(self):
        with synthetic_csv() as file_path:
            result = transport_data(file_path, ["P1"], chunksize=1)

        by_id = result.set_index("charge_point_id")
        self.assertEqual(set(by_id.index), {"P1", "P2"})
        self.assertEqual(by_id.loc["P1", "station_name"], "First")
        self.assertEqual(by_id.loc["P1", "nominal_power"], 150)
        self.assertEqual(by_id.loc["P1", "coordonneesXY"], "[1, 2]")
        self.assertEqual(by_id.loc["P1", "prise_type_combo_ccs"], "TRUE")
        self.assertEqual(by_id.loc["P1", "prise_type_chademo"], "TRUE")
        self.assertEqual(by_id.loc["P1", "cpo_name"], "CPO-A")
        self.assertEqual(by_id.loc["P1", "cpo_siren"], "0123")
        self.assertEqual(pd.Timestamp(by_id.loc["P1", "date_maj"]), pd.Timestamp("2023-06-01"))

    def test_chunk_size_does_not_change_the_result(self):
        with synthetic_csv() as file_path:
            cases = (
                (FIXTURE_PATH, ["FRAAAA111101"]),
                (FIXTURE_PATH, ["FRAAAA111101", "FRBBBB222203"]),
                (FIXTURE_PATH, ["DOES_NOT_EXIST"]),
                (FIXTURE_PATH, []),
                (file_path, ["P1"]),
                (file_path, []),
            )
            for path, charge_point_ids in cases:
                by_one = transport_data(path, charge_point_ids, chunksize=1)
                by_thousand = transport_data(path, charge_point_ids, chunksize=1000)
                assert_frame_equal(by_one, by_thousand, check_dtype=True, check_exact=True)

    def test_download_csv_writes_the_response_body_and_reuses_the_file(self):
        payload = b"id,name\n" + (b"1,station\n" * 200_000)
        last_modified = "2099-12-31T23:59:58+00:00"
        file_path = "/tmp/transport_data_gouv_charge_points_2099-12-31_23-59-58.csv"
        for path in (file_path, f"{file_path}.part"):
            if os.path.exists(path):
                os.remove(path)

        api_payload = {
            "resources": [
                {
                    "latest": "https://example.test/charge-points.csv",
                    "last_modified": last_modified,
                }
            ]
        }

        class Response:
            def __init__(self, content=b"", json_payload=None):
                self.content = content
                self.status_code = 200
                self.json_payload = json_payload

            def json(self):
                return self.json_payload

            def iter_content(self, chunk_size=1):
                for start in range(0, len(self.content), chunk_size):
                    yield self.content[start : start + chunk_size]

            def __enter__(self):
                return self

            def __exit__(self, *args):
                return False

        responses = [
            Response(json_payload=api_payload),
            Response(content=payload),
            Response(json_payload=api_payload),
        ]

        try:
            with patch("elec.services.transport_data_gouv.requests.get", side_effect=responses) as get:
                first_path = TransportDataGouv.download_csv()
                second_path = TransportDataGouv.download_csv()

            self.assertEqual(first_path, file_path)
            self.assertEqual(second_path, file_path)
            self.assertEqual(Path(file_path).read_bytes(), payload)
            self.assertEqual(get.call_count, 3)
        finally:
            for path in (file_path, f"{file_path}.part"):
                if os.path.exists(path):
                    os.remove(path)


def synthetic_rows():
    return [
        {
            "id_pdc_itinerance": "X",
            "id_station_itinerance": "SX",
            "nom_station": "Nope",
            "coordonneesXY": "[0, 0]",
            "puissance_nominale": "1.5",
            "prise_type_combo_ccs": "FALSE",
            "prise_type_chademo": "FALSE",
            "date_maj": "2020-01-01",
            "last_modified": "2024-01-01T00:00:00+00:00",
            "nom_amenageur": "N",
            "siren_amenageur": "1",
        },
        {
            "id_pdc_itinerance": "P1",
            "id_station_itinerance": "S1",
            "nom_station": "First",
            "coordonneesXY": "[1, 2]",
            "puissance_nominale": "10",
            "prise_type_combo_ccs": "FALSE",
            "prise_type_chademo": "FALSE",
            "date_maj": "2022-01-01",
            "last_modified": "2024-01-01T00:00:00+00:00",
            "nom_amenageur": "CPO-A",
            "siren_amenageur": "0123",
        },
        {
            "id_pdc_itinerance": "P1",
            "id_station_itinerance": "S1",
            "nom_station": "Second",
            "coordonneesXY": "[9, 9]",
            "puissance_nominale": "150",
            "prise_type_combo_ccs": "TRUE",
            "prise_type_chademo": "TRUE",
            "date_maj": "2023-06-01",
            "last_modified": "2024-06-01T00:00:00+00:00",
            "nom_amenageur": "CPO-B",
            "siren_amenageur": "9999",
        },
        {
            "id_pdc_itinerance": "P2",
            "id_station_itinerance": "S1",
            "nom_station": "Sib",
            "coordonneesXY": "[3, 4]",
            "puissance_nominale": "7",
            "prise_type_combo_ccs": "FALSE",
            "prise_type_chademo": "FALSE",
            "date_maj": "2020-05-05",
            "last_modified": "2024-01-02T00:00:00+00:00",
            "nom_amenageur": "Only",
            "siren_amenageur": "0007",
        },
    ]


class synthetic_csv:
    def __enter__(self):
        handle, name = tempfile.mkstemp(suffix=".csv")
        os.close(handle)
        self.path = Path(name)
        with self.path.open("w", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=CSV_COLUMNS)
            writer.writeheader()
            writer.writerows(synthetic_rows())
        return self.path

    def __exit__(self, *args):
        if self.path.exists():
            self.path.unlink()
        return False
