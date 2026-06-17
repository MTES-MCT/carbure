import os
import tempfile
from datetime import datetime
from io import BufferedReader

import xlsxwriter
from django.core.exceptions import ObjectDoesNotExist

from biomethane.models import (
    BiomethaneAnnualDeclaration,
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


def _safe_related(obj, attr):
    """Return a reverse one-to-one related object, or None when it does not exist."""
    try:
        return getattr(obj, attr)
    except ObjectDoesNotExist:
        return None


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


def generate_dreal_export(producer_ids, year: int) -> BufferedReader:
    """Generate a flat Excel file (one row per producer) of validated declarations for DREAL.

    Only producers within `producer_ids` that have a validated (DECLARED) declaration for `year`
    are exported.
    """
    filename = f"biomethane_dreal_export_{year}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    file_path = os.path.join(tempfile.gettempdir(), filename)

    workbook = xlsxwriter.Workbook(file_path)
    header_format = workbook.add_format({"bold": True})
    sheet = workbook.add_worksheet("Déclarations")

    col_defs = _build_column_defs()

    sheet.set_column(0, len(col_defs) - 1, 30)
    for col_idx, (label, _section, _field) in enumerate(col_defs):
        sheet.write(0, col_idx, label, header_format)

    # Anchor on validated declarations and join year-independent one-to-one relations in a single query
    declarations = list(
        BiomethaneAnnualDeclaration.objects.filter(
            producer_id__in=producer_ids,
            year=year,
            status=BiomethaneAnnualDeclaration.DECLARED,
        )
        .select_related(
            "producer",
            "producer__biomethane_contract",
            "producer__biomethane_production_unit__department",
            "producer__biomethane_injection_site",
        )
        .order_by("producer__name")
    )
    exported_producer_ids = [decl.producer_id for decl in declarations]

    # Year-scoped relations cannot be select_related, preload them to avoid N+1 queries
    digestates = {
        d.producer_id: d for d in BiomethaneDigestate.objects.filter(producer_id__in=exported_producer_ids, year=year)
    }
    energies = {e.producer_id: e for e in BiomethaneEnergy.objects.filter(producer_id__in=exported_producer_ids, year=year)}

    for row_idx, declaration in enumerate(declarations, start=1):
        producer = declaration.producer
        pid = producer.id
        row_objects = {
            "contract": _safe_related(producer, "biomethane_contract"),
            "production_unit": _safe_related(producer, "biomethane_production_unit"),
            "injection_site": _safe_related(producer, "biomethane_injection_site"),
            "digestate": digestates.get(pid),
            "energy": energies.get(pid),
        }
        for col_idx, (_label, section, field_name) in enumerate(col_defs):
            if section == "producer":
                sheet.write(row_idx, col_idx, producer.name)
            else:
                obj = row_objects.get(section)
                if obj is None or field_name is None:
                    sheet.write(row_idx, col_idx, "")
                else:
                    value = _get_display_value(obj, field_name)
                    sheet.write(row_idx, col_idx, _format_value(value))

    workbook.close()
    return open(file_path, "rb")
