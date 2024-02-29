import argparse
from collections import defaultdict
import django
import os
from tqdm import tqdm
from django.db import transaction
from django.core.paginator import Paginator

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()

from elec.models.elec_charge_point import ElecChargePoint
from elec.services.transport_data_gouv import TransportDataGouv


@transaction.atomic
def refresh_charge_point_data(batch):
    print(f"> Refresh charge point data from TDG")

    charge_points = ElecChargePoint.objects.all().order_by("charge_point_id")

    update_fields = [
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

    # fix wrong current type
    charge_points.filter(current_type="CC").update(current_type="DC")
    charge_points.filter(current_type="CA").update(current_type="AC")

    # group charge points by their station
    charge_points_by_stations = defaultdict(list[ElecChargePoint])

    # update charge point data from TDG
    paginator = Paginator(charge_points, batch)
    for page_number in tqdm(paginator.page_range):
        page = paginator.page(page_number)
        page_charge_points = page.object_list
        charge_point_summary = [{"charge_point_id": c.charge_point_id} for c in page_charge_points]
        charge_point_data = TransportDataGouv.find_charge_point_data(charge_point_summary, batch)
        charge_point_data_by_id = {c["charge_point_id"]: c for c in charge_point_data}
        charge_points_to_update = []

        for charge_point in page_charge_points:
            tdg_data = charge_point_data_by_id.get(charge_point.charge_point_id)
            if tdg_data:
                updated_charge_point = update_charge_point(charge_point, tdg_data)
                charge_points_to_update.append(updated_charge_point)
                charge_points_by_stations[updated_charge_point.station_id].append(updated_charge_point)

        ElecChargePoint.objects.bulk_update(charge_points_to_update, update_fields)

    print("> Check if applications have readings for all charge points of a same station")
    for station, charge_points in tqdm(charge_points_by_stations.items()):
        if all([cp.mid_id and cp.measure_date and cp.measure_energy is not None for cp in charge_points]):
            charge_points_to_update = []
            for charge_point in charge_points:
                charge_points_to_update.append(update_charge_point(charge_point, {"is_article_2": False}))
            ElecChargePoint.objects.bulk_update(charge_points_to_update, ["is_article_2"])

    print("> Done")


def update_charge_point(charge_point: ElecChargePoint, data: dict):
    for key, value in data.items():
        setattr(charge_point, key, value)
    return charge_point


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Refresh charge point data and meter readings")
    parser.add_argument("--batch", dest="batch", type=int, action="store", default=1000, help="How many operations at a time")  # fmt:skip
    args = parser.parse_args()

    refresh_charge_point_data(args.batch)
