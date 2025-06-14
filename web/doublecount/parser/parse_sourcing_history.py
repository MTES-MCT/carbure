from typing import List

from openpyxl import Workbook

from core.models import GenericCertificate
from doublecount.parser.excel_to_carbure_convertor import get_feedstock_from_dc_feedstock
from doublecount.parser.helpers import extract_country_code, extract_year, intOrZero
from doublecount.parser.types import SourcingHistoryRow


def parse_sourcing_history(excel_file: Workbook, start_year: int) -> List[SourcingHistoryRow]:
    sourcing_sheet = excel_file["Historique d'approvisionnement"]
    sourcing_rows: List[SourcingHistoryRow] = []

    current_year = 2100

    # Collect all certificate IDs from the sheet
    certificate_ids = [row[7].value for row in sourcing_sheet.iter_rows() if row[7].value]

    # Preload all certificates in one query
    certificates = GenericCertificate.objects.filter(certificate_id__in=certificate_ids)
    certificates_dict = {cert.certificate_id: cert for cert in certificates}

    for line, row in enumerate(sourcing_sheet.iter_rows()):
        current_year = extract_year(row[1].value, current_year)
        if current_year > start_year:
            continue

        feedstock_name = row[2].value
        origin_country_cell = row[3].value
        supply_country_cell = row[4].value
        transit_country_cell = row[5].value
        raw_material_supplier = row[6].value
        supplier_certificate_id = row[7].value

        if not feedstock_name or feedstock_name == origin_country_cell:
            continue

        feedstock = get_feedstock_from_dc_feedstock(feedstock_name)
        if not feedstock:
            continue

        origin_country = extract_country_code(origin_country_cell)
        supply_country = extract_country_code(supply_country_cell)
        transit_country = extract_country_code(transit_country_cell)

        # Get the supplier certificate from the preloaded dictionary
        supplier_certificate = certificates_dict.get(supplier_certificate_id)

        sourcing: SourcingHistoryRow = {
            "line": line + 1,
            "year": current_year,
            "feedstock": feedstock,
            "origin_country": origin_country,
            "supply_country": supply_country,
            "transit_country": transit_country,
            "metric_tonnes": intOrZero(row[8].value),
            "raw_material_supplier": raw_material_supplier,
            "supplier_certificate_name": supplier_certificate_id,
            "supplier_certificate": supplier_certificate,
        }

        sourcing_rows.append(sourcing)

    return sourcing_rows
