import pandas as pd
from django.core.management.base import BaseCommand
from django.forms import model_to_dict
from simple_history.utils import bulk_update_with_history

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
        parser.add_argument(
            "--apply",
            type=bool,
            default=False,
            help="Save the results in the database",
        )

    def handle(self, *args, **options):
        cpo = options["cpo"]
        batch = options["batch"]
        apply = options["apply"]

        print("> Refresh charge point data from TDG")

        pdcs = ElecChargePoint.objects.filter(is_deleted=False).order_by("charge_point_id")
        if cpo:
            pdcs = pdcs.filter(cpo__name=cpo)

        pdcs_df = pd.DataFrame([model_to_dict(cp) for cp in pdcs])
        tdg_df = TransportDataGouv.get_transport_data(pdcs_df)

        updated = []
        power_changed = 0
        not_found = 0

        for cp in pdcs:
            pdc_df = tdg_df[tdg_df["charge_point_id"] == cp.charge_point_id]
            try:
                tdg_pdc = pdc_df.iloc[0].to_dict()
                nominal_power = tdg_pdc.get("nominal_power")
                if nominal_power > 1000:
                    nominal_power /= 1000
                if nominal_power != 0 and nominal_power != cp.nominal_power:
                    power_changed += 1
                    cp.nominal_power = nominal_power
                    updated.append(cp)
            except Exception:
                not_found += 1

        if apply:
            bulk_update_with_history(updated, ElecChargePoint, ["nominal_power"], batch)

        print(f"> {power_changed} nominal power changed")
        print(f"> {not_found} charge point ids not found")
        print("> Done")
