import os
import tempfile
from datetime import datetime
from io import BufferedReader

import xlsxwriter

from biomethane.models import (
    BiomethaneContract,
    BiomethaneDigestate,
    BiomethaneEnergy,
    BiomethaneInjectionSite,
    BiomethaneProductionUnit,
)
from biomethane.services.declaration_export import (
    _PRODUCTION_UNIT_SITE_FIELDS,
    _auto_fields,
    _format_value,
    _get_display_value,
    _verbose_name,
)


def _build_column_defs():
    """Build column definitions as list of (header_label, section, field_name) tuples."""
    cols = [("Nom du biométhaniseur", "producer", None)]

    for fn in _auto_fields(BiomethaneContract):
        cols.append((_verbose_name(BiomethaneContract, fn), "contract", fn))

    for label, fn in _PRODUCTION_UNIT_SITE_FIELDS:
        cols.append((label, "production_unit", fn))
    for fn in _auto_fields(BiomethaneProductionUnit):
        cols.append((_verbose_name(BiomethaneProductionUnit, fn), "production_unit", fn))

    for fn in _auto_fields(BiomethaneInjectionSite):
        cols.append((_verbose_name(BiomethaneInjectionSite, fn), "injection_site", fn))

    for fn in _auto_fields(BiomethaneDigestate):
        cols.append((_verbose_name(BiomethaneDigestate, fn), "digestate", fn))

    for fn in _auto_fields(BiomethaneEnergy):
        cols.append((_verbose_name(BiomethaneEnergy, fn), "energy", fn))

    return cols


def generate_dreal_export(production_units, year: int) -> BufferedReader:
    """Generate a simple Excel file with one declaration per row for DREAL."""
    filename = f"biomethane_dreal_export_{year}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    file_path = os.path.join(tempfile.gettempdir(), filename)

    workbook = xlsxwriter.Workbook(file_path)
    header_format = workbook.add_format({"bold": True})
    sheet = workbook.add_worksheet("Déclarations")

    col_defs = _build_column_defs()

    sheet.set_column(0, len(col_defs) - 1, 30)
    for col_idx, (label, _section, _field) in enumerate(col_defs):
        sheet.write(0, col_idx, label, header_format)

    # Preload related data to avoid N+1 queries
    production_units = list(production_units.select_related("producer", "department"))
    producer_ids = [pu.producer_id for pu in production_units]

    contracts = {c.producer_id: c for c in BiomethaneContract.objects.filter(producer_id__in=producer_ids)}
    injection_sites = {i.producer_id: i for i in BiomethaneInjectionSite.objects.filter(producer_id__in=producer_ids)}
    digestates = {d.producer_id: d for d in BiomethaneDigestate.objects.filter(producer_id__in=producer_ids, year=year)}
    energies = {e.producer_id: e for e in BiomethaneEnergy.objects.filter(producer_id__in=producer_ids, year=year)}

    for row_idx, pu in enumerate(production_units, start=1):
        pid = pu.producer_id
        row_objects = {
            "contract": contracts.get(pid),
            "production_unit": pu,
            "injection_site": injection_sites.get(pid),
            "digestate": digestates.get(pid),
            "energy": energies.get(pid),
        }
        for col_idx, (_label, section, field_name) in enumerate(col_defs):
            if section == "producer":
                sheet.write(row_idx, col_idx, pu.producer.name if pu.producer else "")
            else:
                obj = row_objects.get(section)
                if obj is None or field_name is None:
                    sheet.write(row_idx, col_idx, "")
                else:
                    value = _get_display_value(obj, field_name)
                    sheet.write(row_idx, col_idx, _format_value(value))

    workbook.close()
    return open(file_path, "rb")
