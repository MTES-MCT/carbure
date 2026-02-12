from pathlib import Path

from openpyxl import Workbook


def prepare_excel_data(meter_reading, cpo_totals, delta_in_kwh, delta_in_mwh):
    meter_reading_for_csv = {
        "cpo__name": meter_reading["cpo__name"],
        "operating_unit": meter_reading["operating_unit"],
        "application__quarter": meter_reading["application__quarter"],
        "application__year": meter_reading["application__year"],
        "total_energy_used": meter_reading["total_energy_used"],
        "recalculated_energy_amount": meter_reading["recalculated_energy_amount"],
        "delta_in_kwh": delta_in_kwh,
        "delta_in_mwh": delta_in_mwh,
    }

    cpo_totals = (
        {
            "cpo__name": meter_reading["cpo__name"],
            "total_energy_used": 0,
            "recalculated_energy_amount": 0,
            "delta_in_kwh": 0,
            "delta_in_mwh": 0,
        }
        if cpo_totals is None
        else cpo_totals
    )

    cpo_totals_for_csv = {
        "total_energy_used": cpo_totals["total_energy_used"] + float(meter_reading["total_energy_used"]),
        "recalculated_energy_amount": cpo_totals["recalculated_energy_amount"]
        + float(meter_reading["recalculated_energy_amount"]),
        "delta_in_kwh": cpo_totals["delta_in_kwh"] + delta_in_kwh,
        "delta_in_mwh": cpo_totals["delta_in_mwh"] + delta_in_mwh,
    }
    return meter_reading_for_csv, cpo_totals_for_csv


def create_excel_file(meter_readings_for_csv, cpo_totals, last_year, log):
    filepath = Path(f"compensate_elec_provision_{last_year}.xlsx")
    wb = Workbook()

    recap_headers = [
        "Aménageur",
        "Somme des relevés (kWh)",
        "Somme recalculée des relevés (kWh)",
        "Montant à compenser (kWh)",
        "Montant à compenser (MWh)",
    ]
    detail_headers = [
        "Aménageur",
        "Operating unit",
        "Trimestre",
        "Année",
        "Somme des relevés (kWh)",
        "Somme recalculée des relevés (kWh)",
        "Montant à compenser (kWh)",
        "Montant à compenser (MWh)",
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
                round(totals["delta_in_kwh"], 3),
                round(totals["delta_in_mwh"], 3),
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
                round(row["delta_in_kwh"], 3),
                round(row["delta_in_mwh"], 3),
            ]
        )

    wb.save(filepath)
    if log:
        print(f"Fichier Excel enregistré : {filepath.absolute()}")
