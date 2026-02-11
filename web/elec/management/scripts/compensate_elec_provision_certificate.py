from collections import defaultdict
from datetime import date
from pathlib import Path

from django.db.models import CharField, Sum
from django.db.models.expressions import F, Value
from django.db.models.functions import Cast, Concat, Round
from openpyxl import Workbook

from elec.models import ElecProvisionCertificate, ElecMeterReadingVirtual
from transactions.models import YearConfig


def prepare_csv_data(meter_reading, cpo_totals, delta):
    meter_reading_for_csv = {
        "cpo__name": meter_reading["cpo__name"],
        "operating_unit": meter_reading["operating_unit"],
        "application__quarter": meter_reading["application__quarter"],
        "application__year": meter_reading["application__year"],
        "total_energy_used": meter_reading["total_energy_used"],
        "recalculated_energy_amount": meter_reading["recalculated_energy_amount"],
        "delta": delta,
    }

    cpo_totals = (
        {
            "cpo__name": meter_reading["cpo__name"],
            "total_energy_used": 0,
            "recalculated_energy_amount": 0,
            "delta": 0,
        }
        if cpo_totals is None
        else cpo_totals
    )

    cpo_totals_for_csv = {
        "total_energy_used": cpo_totals["total_energy_used"]
        + float(meter_reading["total_energy_used"]),
        "recalculated_energy_amount": cpo_totals["recalculated_energy_amount"]
        + float(meter_reading["recalculated_energy_amount"]),
        "delta": cpo_totals["delta"] + delta,
    }
    return meter_reading_for_csv, cpo_totals_for_csv


def create_excel_file(meter_readings_for_csv, cpo_totals, last_year, log):
    filepath = Path(f"compensate_elec_provision_{last_year}.xlsx")
    wb = Workbook()

    recap_headers = [
        "Aménageur",
        "Somme des relevés",
        "Somme recalculée des relevés",
        "Montant à compenser",
    ]
    detail_headers = [
        "Aménageur",
        "Operating unit",
        "Trimestre",
        "Année",
        "Somme des relevés",
        "Somme recalculée des relevés",
        "Montant à compenser",
    ]

    ws_recap = wb.active
    ws_recap.title = "Recap CPO"
    ws_recap.append(recap_headers)
    for cpo_name in sorted(cpo_totals.keys()):
        totals = cpo_totals[cpo_name]
        ws_recap.append(
            [
                cpo_name,
                round(totals["total_energy_used"], 3),
                round(totals["recalculated_energy_amount"], 3),
                round(totals["delta"], 3),
            ]
        )

    ws_detail = wb.create_sheet("Détail")
    ws_detail.append(detail_headers)
    for row in meter_readings_for_csv:
        ws_detail.append(
            [
                row["cpo__name"],
                row["operating_unit"],
                row["application__quarter"],
                row["application__year"],
                row["total_energy_used"],
                row["recalculated_energy_amount"],
                row["delta"],
            ]
        )

    wb.save(filepath)
    if log:
        print(f"Fichier Excel enregistré : {filepath.absolute()}")


def compensate_elec_provision_certificate(
    new_enr_ratio, apply=False, store_file=False, log=False
):
    today = date.today()
    last_year = today.year - 1
    new_enr_ratio = new_enr_ratio / 100  # 25 -> 0.25

    meter_readings = (
        ElecMeterReadingVirtual.objects.prefetch_related("application", "cpo")
        .filter(application__year=last_year)
        .values(
            "cpo__id",
            "cpo__name",
            "operating_unit",
            "application__year",
            "application__quarter",
        )
        .annotate(
            total_energy_used=Round(
                Sum((F("current_index") - F("prev_index")) * F("enr_ratio")), 3
            ),
            recalculated_energy_amount=Round(
                Sum((F("current_index") - F("prev_index")) * new_enr_ratio), 3
            ),
        )
        .order_by("cpo__name", "operating_unit", "application_id")
    )

    certificates_already_created = (
        ElecProvisionCertificate.objects.filter(
            year=last_year,
            source=ElecProvisionCertificate.ENR_RATIO_COMPENSATION,
        )
        .values("cpo_id", "quarter", "year", "operating_unit")
        .annotate(
            key=Concat(
                Cast(F("cpo_id"), output_field=CharField()),
                Value("-"),
                Cast(F("quarter"), output_field=CharField()),
                Value("-"),
                Cast(F("year"), output_field=CharField()),
                Value("-"),
                F("operating_unit"),
            )
        )
        .values_list("key", flat=True)
    )

    elec_provision_certificates = []
    meter_readings_for_csv = []
    cpo_totals = {}

    for meter_reading in meter_readings:
        delta = float(
            meter_reading["recalculated_energy_amount"]
            - meter_reading["total_energy_used"]
        )
        key = (
            f"{meter_reading['cpo__id']}-{meter_reading['application__quarter']}"
            f"-{meter_reading['application__year']}-{meter_reading['operating_unit']}"
        )

        if delta > 0 and key not in certificates_already_created:
            meter_reading_for_csv, cpo_totals_for_csv = prepare_csv_data(
                meter_reading,
                cpo_totals.get(meter_reading["cpo__name"]),
                delta,
            )
            meter_readings_for_csv.append(meter_reading_for_csv)
            cpo_totals[meter_reading["cpo__name"]] = cpo_totals_for_csv
            elec_provision_certificates.append(
                ElecProvisionCertificate(
                    cpo_id=meter_reading["cpo__id"],
                    quarter=meter_reading["application__quarter"],
                    year=last_year,
                    operating_unit=meter_reading["operating_unit"],
                    energy_amount=delta,
                    remaining_energy_amount=delta,
                    source=ElecProvisionCertificate.ENR_RATIO_COMPENSATION,
                )
            )

    if apply:
        if elec_provision_certificates:
            ElecProvisionCertificate.objects.bulk_create(
                elec_provision_certificates, batch_size=10
            )
            if log:
                print(f"Created {len(elec_provision_certificates)} new certificates")
        elif log:
            print("No new certificates to create")

        YearConfig.objects.filter(year=today.year).update(
            renewable_share=new_enr_ratio
        )

    if store_file and meter_readings_for_csv:
        create_excel_file(meter_readings_for_csv, cpo_totals, last_year, log)

    return elec_provision_certificates
