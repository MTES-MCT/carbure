import json

import pandas as pd
from django.core.management.base import BaseCommand
from django.db.models import ExpressionWrapper, F, FloatField
from django.db.models.aggregates import Sum
from django.db.models.functions import Coalesce

from elec.models import ElecCertificateReadjustment, ElecMeterReading, ElecProvisionCertificate
from elec.models.elec_meter_reading_application import ElecMeterReadingApplication


def _get_real_total_energy_declared(cpo_id, year):
    energy_queryset = (
        ElecMeterReading.extended_objects.select_related("application")
        .filter(cpo_id=cpo_id, application__status=ElecMeterReadingApplication.ACCEPTED, application__year=year)
        .annotate(
            renewable_energy_value=ExpressionWrapper(
                F("renewable_energy"),
                output_field=FloatField(),
            ),
            non_renewable_energy_value=ExpressionWrapper(
                F("current_index") - F("prev_index"),
                output_field=FloatField(),
            ),
        )
    )

    result = energy_queryset.aggregate(
        renewable_energy=Coalesce(Sum("renewable_energy_value"), 0.0),
        non_renewable_energy=Coalesce(Sum("non_renewable_energy_value"), 0.0),
    )

    return result["renewable_energy"], result["non_renewable_energy"]


def _get_certificates_energy_amount_by_source(cpo_id, year, source):
    certificate_queryset = ElecProvisionCertificate.objects.filter(
        cpo_id=cpo_id,
        source=source,
        year=year,
    ).annotate(
        renewable_energy_value=ExpressionWrapper(
            F("energy_amount"),
            output_field=FloatField(),
        ),
        non_renewable_energy_value=ExpressionWrapper(
            F("energy_amount") / F("enr_ratio"),
            output_field=FloatField(),
        ),
    )

    result = certificate_queryset.aggregate(
        renewable_energy=Coalesce(Sum("renewable_energy_value"), 0.0),
        non_renewable_energy=Coalesce(Sum("non_renewable_energy_value"), 0.0),
    )

    return result["renewable_energy"] * 1000, result["non_renewable_energy"] * 1000


def _get_meter_readings_readjustment_energy(cpo_id, year):
    result = ElecCertificateReadjustment.objects.filter(
        cpo_id=cpo_id,
        error_source=ElecCertificateReadjustment.METER_READINGS,
        year=year,
    ).aggregate(
        renewable_energy=Coalesce(Sum("energy_amount"), 0.0),
        non_renewable_energy=Coalesce(
            ExpressionWrapper(
                Sum(Coalesce(F("non_renewable_energy_amount"), F("energy_amount"))),
                output_field=FloatField(),
            ),
            0.0,
        ),
    )
    return result["renewable_energy"] * 1000, result["non_renewable_energy"] * 1000


class Command(BaseCommand):
    # Command : python web/manage.py generate_meter_readings_report --year 2025 --log
    help = "Generate a report for all the meter readings registered in Carbure"

    def add_arguments(self, parser):
        parser.add_argument(
            "--year",
            type=int,
            required=True,
            help="Year of meter readings to include in the report",
        )
        parser.add_argument(
            "--log",
            default=False,
            action="store_true",
            help="Print logs during execution",
        )
        parser.add_argument(
            "--csv",
            default=False,
            action="store_true",
            help="Store meter reading details in a CSV file at /tmp/readings.csv",
        )
        parser.add_argument(
            "--cpo",
            type=int,
            default=None,
            help="Cpo to filter readings",
        )
        parser.add_argument(
            "--apply",
            default=False,
            action="store_true",
            help="Create readjustments in the table elec_certificate_readjustment for each cpo",
        )

    def handle(self, *args, **options):
        log = options.get("log")
        csv = options.get("csv")
        cpo = options.get("cpo")
        apply_readjustments = options.get("apply")
        year = options.get("year")

        cpo_with_readings = (
            ElecMeterReading.objects.select_related("cpo").values("cpo_id", "cpo__name").filter(application__year=year)
        )

        if cpo is not None:
            cpo_with_readings = cpo_with_readings.filter(cpo_id=cpo)

        cpo_with_readings = cpo_with_readings.distinct()

        report = {}
        total_surplus = 0

        for cpo in cpo_with_readings:
            total_meter_reading_energy, total_non_renewable_meter_reading_energy = _get_real_total_energy_declared(
                cpo["cpo_id"], year
            )
            total_provision_certificate_energy, total_non_renewable_provision_certificate_energy = (
                _get_certificates_energy_amount_by_source(cpo["cpo_id"], year, ElecProvisionCertificate.METER_READINGS)
            )
            total_admin_error_readjustment, total_non_renewable_admin_error_readjustment = (
                _get_certificates_energy_amount_by_source(
                    cpo["cpo_id"], year, ElecProvisionCertificate.ADMIN_ERROR_COMPENSATION
                )
            )
            total_cpo_readjustment, total_non_renewable_cpo_readjustment = _get_meter_readings_readjustment_energy(
                cpo["cpo_id"], year
            )

            diff = (
                total_provision_certificate_energy
                - total_meter_reading_energy
                - total_cpo_readjustment
                + total_admin_error_readjustment
            )

            non_renewable_diff = (
                total_non_renewable_provision_certificate_energy
                - total_non_renewable_meter_reading_energy
                - total_non_renewable_cpo_readjustment
                + total_non_renewable_admin_error_readjustment
            )

            # if diff is more than 100 kWh, it's a significant difference
            if abs(diff) >= 100:
                total_surplus += diff
                report[cpo["cpo__name"]] = {
                    "certificats": total_provision_certificate_energy,
                    "real_energy_must_be_declared": total_meter_reading_energy,
                    "surplus": round(diff, 3),
                }

                # create a readjustment only if the cpo has a positive surplus
                if apply_readjustments and diff > 0:
                    ElecCertificateReadjustment.objects.create(
                        cpo_id=cpo["cpo_id"],
                        error_source=ElecCertificateReadjustment.METER_READINGS,
                        # back to MWh to match the energy_amount field
                        energy_amount=round(diff / 1000, 2),
                        non_renewable_energy_amount=round(non_renewable_diff / 1000, 2),
                        reason="Différence entre l'énergie générée par certificats et l'énergie déclarée dans les relevés",
                        year=year,
                    )

        if log:
            items = []
            for cpo, data in report.items():
                items.append(
                    {
                        "Aménageur": cpo,
                        "Energie générée par certificats (kWh)": data["certificats"],
                        "Énergie déclarée (kWh)": data["real_energy_must_be_declared"],
                        "Surplus (kWh)": data["surplus"],
                    }
                )

            sorted_items = sorted(items, key=lambda x: x["Surplus (kWh)"], reverse=True)
            df = pd.DataFrame(sorted_items)

            pd.options.display.float_format = "{:,.3f}".format
            print(df.to_string(index=False))
            print(f"Soit un total de {round(total_surplus / 1000, 1):,} MWh\n")

        if csv:
            arr = []
            for cpo, data in report.items():
                arr.append([cpo, data["certificats"], data["real_energy_must_be_declared"], data["surplus"]])
            df = pd.DataFrame(
                arr,
                columns=["Aménageur", "Energie générée par certificats (kWh)", "Énergie déclarée (kWh)", "Surplus (kWh)"],
            )
            df.to_csv("/tmp/readings.csv", index=False)

        return json.dumps({cpo: data["surplus"] for cpo, data in report.items()})
