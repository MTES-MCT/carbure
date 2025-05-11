import pandas as pd
from django.core.management.base import BaseCommand
from django.forms import model_to_dict

from core.utils import bulk_update_or_create
from elec.models.elec_charge_point import ElecChargePoint
from elec.services.transport_data_gouv import TransportDataGouv


class Command(BaseCommand):
    help = "Refresh charge point data from transport.data.gouv.fr"

    def add_arguments(self, parser):
        parser.add_argument(
            "--cpo",
            type=str,
            help="Specify the CPO to focus on (optional)",
        )
        parser.add_argument(
            "--batch",
            type=int,
            default=1000,
            help="How many rows updated at once",
        )

    def handle(self, *args, **options):
        cpo = options["cpo"]
        batch = options["batch"]

        print("> Refresh charge point data from TDG")

        charge_points = ElecChargePoint.objects.filter(is_deleted=False).order_by("charge_point_id")
        if cpo:
            charge_points = charge_points.filter(cpo__name=cpo)

        cp_df = pd.DataFrame([model_to_dict(cp) for cp in charge_points])
        tdg_df = TransportDataGouv.get_transport_data(cp_df)

        diff_nps = 0
        not_found = 0

        changed_cps = set()

        for cp in charge_points:
            tdg_cp_df = tdg_df[tdg_df["charge_point_id"] == cp.charge_point_id]
            try:
                tdg_cp = tdg_cp_df.iloc[0].to_dict()
                nominal_power = tdg_cp.get("nominal_power")
                if nominal_power > 1000:
                    nominal_power /= 1000
                if nominal_power != 0 and nominal_power != cp.nominal_power:
                    diff_nps += 1
                    cp.nominal_power = nominal_power
                    changed_cps.add(cp)
            except Exception:
                not_found += 1

        bulk_update_or_create(ElecChargePoint, "charge_point_id", list(charge_points), batch)

        print(f"> {diff_nps} nominal power changed")
        print(f"> {not_found} charge point ids not found")
        print("> Done")
