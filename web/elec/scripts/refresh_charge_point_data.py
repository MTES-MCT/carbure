import argparse
import os

import django
import pandas as pd
from django.db import transaction

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()

from core.utils import bulk_update_or_create
from elec.models.elec_charge_point import ElecChargePoint
from elec.services.transport_data_gouv import TransportDataGouv


@transaction.atomic
def refresh_charge_point_data(cpo, batch):
    print("> Refresh charge point data from TDG")

    charge_points = ElecChargePoint.objects.all().order_by("charge_point_id")
    if cpo:
        charge_points = charge_points.filter(cpo__name=cpo)

    # fix wrong current type
    charge_points.filter(current_type="CC").update(current_type="DC")
    charge_points.filter(current_type="CA").update(current_type="AC")

    # update charge point data from TDG
    charge_point_data = pd.DataFrame([charge_point_to_dict(cp) for cp in charge_points])

    charge_point_data["line"] = charge_point_data.index
    charge_point_data["is_in_application"] = True
    charge_point_data = TransportDataGouv.merge_charge_point_data(charge_point_data)

    charge_points = charge_point_data.to_dict(orient="records")
    charge_points = [extract_charge_point_update(cp) for cp in charge_points]

    bulk_update_or_create(ElecChargePoint, "charge_point_id", charge_points)

    print("> Done")


def charge_point_to_dict(charge_point: ElecChargePoint):
    return {
        "charge_point_id": charge_point.charge_point_id,
        "installation_date": charge_point.installation_date,
        "mid_id": charge_point.mid_id,
        "measure_date": charge_point.measure_date,
        "measure_energy": charge_point.measure_energy,
        "measure_reference_point_id": charge_point.measure_reference_point_id,
        "current_type": charge_point.current_type,
        "is_article_2": charge_point.is_article_2,
        "station_name": charge_point.station_name,
        "station_id": charge_point.station_id,
        "nominal_power": charge_point.nominal_power,
        "cpo_name": charge_point.cpo_name,
        "cpo_siren": charge_point.cpo_siren,
        "latitude": charge_point.latitude,
        "longitude": charge_point.longitude,
    }


def extract_charge_point_update(charge_point_data: dict) -> dict:
    return {
        "charge_point_id": charge_point_data.get("charge_point_id"),
        "mid_id": charge_point_data.get("mid_id"),
        "measure_reference_point_id": charge_point_data.get("measure_reference_point_id"),
        "current_type": charge_point_data.get("current_type"),
        "is_article_2": charge_point_data.get("is_article_2"),
        "station_name": charge_point_data.get("station_name"),
        "station_id": charge_point_data.get("station_id"),
        "nominal_power": charge_point_data.get("nominal_power"),
        "cpo_name": charge_point_data.get("cpo_name"),
        "cpo_siren": charge_point_data.get("cpo_siren"),
        "latitude": charge_point_data.get("latitude") or None,
        "longitude": charge_point_data.get("longitude") or None,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Refresh charge point data and meter readings")
    parser.add_argument("--batch", dest="batch", type=int, action="store", default=10, help="How many operations at a time")  # fmt:skip
    parser.add_argument("--cpo", dest="cpo", type=str, action="store", help="Focus on one CPO")
    args = parser.parse_args()

    refresh_charge_point_data(args.cpo, args.batch)
