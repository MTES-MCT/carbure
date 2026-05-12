import json

import pandas as pd
from django.core.management.base import BaseCommand, CommandError
from django.db.models.aggregates import Sum

from elec.models import ElecCertificateReadjustment, ElecMeterReading, ElecProvisionCertificate
from elec.models.elec_meter_reading_application import ElecMeterReadingApplication


def _get_real_energy_declared_by_group(cpo_ids=None, year=None):
    readings = ElecMeterReading.extended_objects.select_related("application").filter(
        application__status=ElecMeterReadingApplication.ACCEPTED
    )
    if cpo_ids:
        readings = readings.filter(cpo_id__in=cpo_ids)
    if year is not None:
        readings = readings.filter(application__year=year)

    grouped_readings = (
        readings.order_by()
        .values("cpo_id", "application__year", "application__quarter", "operating_unit")
        .annotate(energy_amount=Sum("renewable_energy"))
    )

    return {
        (reading["cpo_id"], reading["application__year"], reading["application__quarter"], reading["operating_unit"]): (
            reading["energy_amount"] or 0
        )
        for reading in grouped_readings
    }


def _get_admin_error_by_group(cpo_ids=None, year=None):
    admin_error_certificates = ElecProvisionCertificate.objects.filter(
        source=ElecProvisionCertificate.ADMIN_ERROR_COMPENSATION
    )
    if cpo_ids:
        admin_error_certificates = admin_error_certificates.filter(cpo_id__in=cpo_ids)
    if year is not None:
        admin_error_certificates = admin_error_certificates.filter(year=year)

    grouped_admin_error = admin_error_certificates.values("cpo_id", "year", "quarter", "operating_unit").annotate(
        energy_amount=Sum("energy_amount")
    )

    return {
        (certificate["cpo_id"], certificate["year"], certificate["quarter"], certificate["operating_unit"]): (
            certificate["energy_amount"] or 0
        )
        * 1000
        for certificate in grouped_admin_error
    }


def _get_readjustments_by_certificate(certificate_ids):
    grouped_readjustments = (
        ElecCertificateReadjustment.objects.filter(
            error_source=ElecCertificateReadjustment.METER_READINGS,
            provision_certificate_id__in=certificate_ids,
        )
        .values("provision_certificate_id")
        .annotate(energy_amount=Sum("energy_amount"))
    )

    return {
        item["provision_certificate_id"]: (item["energy_amount"] or 0) * 1000
        for item in grouped_readjustments
        if item["provision_certificate_id"] is not None
    }


class Command(BaseCommand):
    help = "Generate a report for all the meter readings registered in Carbure"

    def add_arguments(self, parser):
        parser.add_argument(
            "--year",
            type=int,
            default=None,
            help="Year of meter readings to include in the report",
        )
        parser.add_argument(
            "--log",
            default=False,
            action="store_true",
            help="Print logs during execution",
        )
        parser.add_argument(
            "--detail",
            default=False,
            action="store_true",
            help="Avec --log, affiche aussi le détail du calcul par certificat",
        )
        parser.add_argument(
            "--csv",
            default=False,
            action="store_true",
            help="Store summary at /tmp/readings.csv and per-certificate detail at /tmp/readings_by_certificate.csv",
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
        log_detail = options.get("detail")
        if log_detail and not log:
            raise CommandError("--detail nécessite --log")
        csv = options.get("csv")
        cpo_filter = options.get("cpo")
        year_filter = options.get("year")
        apply_readjustments = options.get("apply")

        certificates = ElecProvisionCertificate.objects.select_related("cpo").filter(
            source=ElecProvisionCertificate.METER_READINGS
        )
        if cpo_filter is not None:
            certificates = certificates.filter(cpo_id=cpo_filter)
        if year_filter is not None:
            certificates = certificates.filter(year=year_filter)
        certificates = list(certificates)

        report = {}
        total_surplus = 0
        certificates_to_create = []
        unmatched_certificate_keys = []
        unmatched_reading_keys = []

        cpo_ids = {certificate.cpo_id for certificate in certificates}
        real_energy_by_group = _get_real_energy_declared_by_group(cpo_ids=cpo_ids, year=year_filter)

        admin_error_by_group = _get_admin_error_by_group(cpo_ids=cpo_ids, year=year_filter)
        readjustment_by_certificate = _get_readjustments_by_certificate([certificate.id for certificate in certificates])
        certificates_by_cpo = {}
        for certificate in certificates:
            certificates_by_cpo.setdefault(certificate.cpo_id, []).append(certificate)

        for cpo_id, cpo_certificates in certificates_by_cpo.items():
            cpo_name = cpo_certificates[0].cpo.name if cpo_certificates[0].cpo_id else str(cpo_id)

            total_meter_reading_energy = 0
            total_provision_certificate_energy = 0
            total_diff = 0
            certificate_diffs = []
            certificate_details = []
            certificate_keys = set()

            for certificate in cpo_certificates:
                group_key = (certificate.cpo_id, certificate.year, certificate.quarter, certificate.operating_unit)
                certificate_keys.add(group_key)
                if group_key not in real_energy_by_group:
                    unmatched_certificate_keys.append((cpo_name, *group_key))
                    continue

                certificate_energy = certificate.energy_amount * 1000

                meter_reading_energy = real_energy_by_group.get(group_key, 0)
                admin_error_energy = admin_error_by_group.get(group_key, 0)
                already_readjusted_energy = readjustment_by_certificate.get(certificate.id, 0)

                diff = certificate_energy - meter_reading_energy - already_readjusted_energy + admin_error_energy
                certificate_diffs.append((certificate, diff))
                certificate_details.append(
                    {
                        "provision_certificate_id": certificate.id,
                        "year": certificate.year,
                        "quarter": certificate.quarter,
                        "operating_unit": certificate.operating_unit,
                        "certificate_energy_kwh": certificate_energy,
                        "meter_reading_energy_kwh": meter_reading_energy,
                        "already_readjusted_energy_kwh": already_readjusted_energy,
                        "admin_error_energy_kwh": admin_error_energy,
                        "difference_kwh": diff,
                    }
                )

                total_provision_certificate_energy += certificate_energy
                total_meter_reading_energy += meter_reading_energy
                total_diff += diff

            reading_keys_for_cpo = {key for key in real_energy_by_group.keys() if key[0] == cpo_id}
            unmatched_reading_keys.extend((cpo_name, *key) for key in sorted(reading_keys_for_cpo - certificate_keys))

            # if total diff is more than 100 kWh for the cpo, it's a significant difference
            if abs(total_diff) >= 100:
                total_surplus += total_diff
                report[cpo_name] = {
                    "certificats": total_provision_certificate_energy,
                    "real_energy_must_be_declared": total_meter_reading_energy,
                    "surplus": round(total_diff, 3),
                    "detail_par_certificat": certificate_details,
                }

                # create a readjustment only for certificates with a positive delta
                if apply_readjustments:
                    for certificate, diff in certificate_diffs:
                        if diff > 0:
                            certificates_to_create.append(
                                ElecCertificateReadjustment(
                                    cpo_id=cpo_id,
                                    provision_certificate_id=certificate.id,
                                    error_source=ElecCertificateReadjustment.METER_READINGS,
                                    # back to MWh to match the energy_amount field
                                    energy_amount=round(diff / 1000, 2),
                                    reason=(
                                        "Différence entre l'énergie générée par certificats "
                                        "et l'énergie déclarée dans les relevés"
                                    ),
                                )
                            )

        if apply_readjustments and certificates_to_create:
            ElecCertificateReadjustment.objects.bulk_create(certificates_to_create, batch_size=1000)

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

            if log_detail:
                detail_rows = []
                for cpo, data in report.items():
                    for row in data.get("detail_par_certificat", []):
                        detail_rows.append(
                            {
                                "Aménageur": cpo,
                                "ID certificat": row["provision_certificate_id"],
                                "Année": row["year"],
                                "Trimestre": row["quarter"],
                                "UO": row["operating_unit"],
                                "Énergie certificat (kWh)": row["certificate_energy_kwh"],
                                "Énergie relevés (kWh)": row["meter_reading_energy_kwh"],
                                "Déjà ajusté (kWh)": row["already_readjusted_energy_kwh"],
                                "Compensation erreur admin (kWh)": row["admin_error_energy_kwh"],
                                "Différence (kWh)": row["difference_kwh"],
                            }
                        )
                if detail_rows:
                    print(
                        "Détail par certificat : différence = énergie certificat "
                        "- énergie relevés - déjà ajusté + compensation erreur admin\n"
                    )
                    detail_df = pd.DataFrame(detail_rows)
                    detail_df = detail_df.sort_values(["Aménageur", "Année", "Trimestre", "UO", "ID certificat"])
                    print(detail_df.to_string(index=False))
                    print("")

            if unmatched_certificate_keys or unmatched_reading_keys:
                print("Clés non appariées ignorées (cpo_name, cpo_id, year, quarter, operating_unit)")
                if unmatched_certificate_keys:
                    print(" - Certificats sans relevés :")
                    for key in sorted(set(unmatched_certificate_keys)):
                        print(f"   {key}")
                if unmatched_reading_keys:
                    print(" - Relevés sans certificats :")
                    for key in sorted(set(unmatched_reading_keys)):
                        print(f"   {key}")
                print("")

        if csv:
            arr = []
            for cpo, data in report.items():
                arr.append([cpo, data["certificats"], data["real_energy_must_be_declared"], data["surplus"]])
            df = pd.DataFrame(
                arr,
                columns=["Aménageur", "Energie générée par certificats (kWh)", "Énergie déclarée (kWh)", "Surplus (kWh)"],
            )
            df.to_csv("/tmp/readings.csv", index=False)

            detail_arr = []
            for cpo, data in report.items():
                for row in data.get("detail_par_certificat", []):
                    detail_arr.append(
                        [
                            cpo,
                            row["provision_certificate_id"],
                            row["year"],
                            row["quarter"],
                            row["operating_unit"],
                            row["certificate_energy_kwh"],
                            row["meter_reading_energy_kwh"],
                            row["already_readjusted_energy_kwh"],
                            row["admin_error_energy_kwh"],
                            row["difference_kwh"],
                        ]
                    )
            if detail_arr:
                detail_df = pd.DataFrame(
                    detail_arr,
                    columns=[
                        "Aménageur",
                        "ID certificat",
                        "Année",
                        "Trimestre",
                        "UO",
                        "Énergie certificat (kWh)",
                        "Énergie relevés (kWh)",
                        "Déjà ajusté (kWh)",
                        "Compensation erreur admin (kWh)",
                        "Différence (kWh)",
                    ],
                )
                detail_df.to_csv("/tmp/readings_by_certificate.csv", index=False)

        return json.dumps({cpo: data["surplus"] for cpo, data in report.items()})
