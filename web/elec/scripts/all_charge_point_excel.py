import argparse
import os

import django
from django.db import transaction
from tqdm import tqdm

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()

from core.excel import export_to_excel  # noqa: E402
from elec.models.elec_charge_point import ElecChargePoint  # noqa: E402


@transaction.atomic
def all_charge_point_excel(cpo):
    print("> Refresh charge point data from TDG")

    charge_points = ElecChargePoint.objects.all().order_by("cpo", "charge_point_id")
    if cpo:
        charge_points = charge_points.filter(cpo__name=cpo)

    fields = [
        # cpo excel data
        "charge_point_id",
        "current_type",
        "installation_date",
        "mid_id",
        "measure_date",
        "measure_energy",
        "is_article_2",
        "measure_reference_point_id",
        # transport.data.gouv.fr data
        "station_name",
        "station_id",
        "nominal_power",
        "cpo_name",
        "cpo_siren",
        "latitude",
        "longitude",
    ]

    charge_point_data = []
    for charge_point in tqdm(charge_points.iterator()):
        charge_point_data.append(charge_point_to_dict(charge_point, fields))

    export_to_excel(
        "/tmp/all_charge_points.xlsx",
        [
            {
                "label": "tickets",
                "rows": charge_point_data,
                "columns": [{"label": field, "value": field} for field in fields],
            }
        ],
    )

    print("> Done")


def charge_point_to_dict(charge_point: ElecChargePoint, fields: list[str]):
    charge_point_data = {}
    for field in fields:
        charge_point_data[field] = getattr(charge_point, field)
    return charge_point_data


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Refresh charge point data and meter readings")
    parser.add_argument("--cpo", dest="cpo", type=str, action="store", help="Focus on one CPO")
    args = parser.parse_args()

    all_charge_point_excel(args.cpo)
