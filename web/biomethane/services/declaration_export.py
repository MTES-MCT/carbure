import os
import tempfile
from datetime import datetime
from io import BufferedReader

import xlsxwriter
from django.utils.text import slugify

from biomethane.models import (
    BiomethaneContract,
    BiomethaneDigestate,
    BiomethaneEnergy,
    BiomethaneInjectionSite,
    BiomethaneProductionUnit,
    BiomethaneSupplyPlan,
)
from biomethane.models.biomethane_digestate_spreading import BiomethaneDigestateSpreading
from biomethane.models.biomethane_digestate_storage import BiomethaneDigestateStorage
from biomethane.models.biomethane_supply_input import BiomethaneSupplyInput
from core.models import Entity


def _verbose_name(model_class, field_name):
    """Get verbose_name for a model field, with fallback to a formatted field name."""
    try:
        return str(model_class._meta.get_field(field_name).verbose_name)
    except Exception:
        return field_name.replace("_", " ")


def _fields_from_model(instance, field_specs):
    """
    Return (label, value) pairs for an instance.

    Each entry in field_specs is either:
    - a string: label is derived from the model's verbose_name for that field
    - a (label, field_name) tuple: use the hardcoded label
    """
    model = type(instance)
    result = []
    for spec in field_specs:
        if isinstance(spec, str):
            field_name = spec
            label = _verbose_name(model, field_name)
        else:
            label, field_name = spec
        value = getattr(instance, field_name, None)
        result.append((label, value))
    return result


def _format_value(value):
    if value is None:
        return ""
    if isinstance(value, bool):
        return "OUI" if value else "NON"
    if isinstance(value, list):
        return ", ".join(str(v) for v in value)
    if isinstance(value, (str, int, float)):
        return value
    return str(value)


# Internal/structural fields that should never appear in exports.
_SKIP_FIELDS = {
    "id",
    "producer",  # owner FK (most models)
    "supply_plan",  # owner FK for BiomethaneSupplyInput
    "digestate",  # owner FK for BiomethaneDigestateSpreading
    "site_ptr",  # multi-table inheritance pointer (BiomethaneProductionUnit)
    "conditions_file",  # file field, not a data field
    "tracked_amendment_types",  # internal contract tracking
    # Site internal fields visible via BiomethaneProductionUnit._meta.fields
    "site_type",
    "private",
    "is_enabled",
    "created_by",
}


def _auto_fields(model_class):
    """Return exportable field names for a model, skipping internal/structural ones."""
    return [f.name for f in model_class._meta.local_fields if f.name not in _SKIP_FIELDS]


# BiomethaneProductionUnit inherits from Site via multi-table inheritance.
# Site fields do not appear in local_fields, so we list them explicitly with labels.
_PRODUCTION_UNIT_SITE_FIELDS = [
    ("Nom", "name"),
    ("SIRET", "site_siret"),
    ("Adresse", "address"),
    ("Code postal", "postal_code"),
    ("Ville", "city"),
    ("Pays", "country"),
    ("Coordonnées GPS", "gps_coordinates"),
]


def _write_supply_inputs_sheet(workbook, supply_plan, header_format):
    """Write an Approvisionnement sheet with one row per BiomethaneSupplyInput."""
    sheet = workbook.add_worksheet("Approvisionnement")
    columns = [(fn, _verbose_name(BiomethaneSupplyInput, fn)) for fn in _auto_fields(BiomethaneSupplyInput)]
    sheet.set_column(0, len(columns) - 1, 25)

    for col_idx, (_, label) in enumerate(columns):
        sheet.write(0, col_idx, label, header_format)

    if supply_plan is None:
        return

    inputs = BiomethaneSupplyInput.objects.filter(supply_plan=supply_plan).select_related("feedstock", "origin_country")
    for row_idx, supply_input in enumerate(inputs, start=1):
        for col_idx, (field_name, _) in enumerate(columns):
            value = getattr(supply_input, field_name, None)
            sheet.write(row_idx, col_idx, _format_value(value))


def _write_digestate_storage_sheet(workbook, producer, header_format):
    """Write a Stockage digestat sheet with one row per storage."""
    sheet = workbook.add_worksheet("Stockage digestat")
    columns = [(fn, _verbose_name(BiomethaneDigestateStorage, fn)) for fn in _auto_fields(BiomethaneDigestateStorage)]
    sheet.set_column(0, len(columns) - 1, 30)

    for col_idx, (_, label) in enumerate(columns):
        sheet.write(0, col_idx, label, header_format)

    for row_idx, storage in enumerate(BiomethaneDigestateStorage.objects.filter(producer=producer), start=1):
        for col_idx, (field_name, _) in enumerate(columns):
            value = getattr(storage, field_name, None)
            sheet.write(row_idx, col_idx, _format_value(value))


def _write_digestate_spreading_sheet(workbook, digestate, header_format):
    """Write an Épandage digestat sheet with one row per spreading."""
    sheet = workbook.add_worksheet("Épandage digestat")
    columns = [(fn, _verbose_name(BiomethaneDigestateSpreading, fn)) for fn in _auto_fields(BiomethaneDigestateSpreading)]
    sheet.set_column(0, len(columns) - 1, 35)

    for col_idx, (_, label) in enumerate(columns):
        sheet.write(0, col_idx, label, header_format)

    if digestate is None:
        return

    for row_idx, spreading in enumerate(BiomethaneDigestateSpreading.objects.filter(digestate=digestate), start=1):
        for col_idx, (field_name, _) in enumerate(columns):
            value = getattr(spreading, field_name, None)
            sheet.write(row_idx, col_idx, _format_value(value))


def _write_sheet(workbook, sheet_name, fields, header_format):
    """Write a sheet with 2 columns: Nom du champ / Valeur du champ."""
    sheet = workbook.add_worksheet(sheet_name)
    sheet.set_column(0, 0, 50)
    sheet.set_column(1, 1, 50)

    sheet.write(0, 0, "Nom du champ", header_format)
    sheet.write(0, 1, "Valeur du champ", header_format)

    for row_idx, (label, value) in enumerate(fields, start=1):
        sheet.write(row_idx, 0, label)
        sheet.write(row_idx, 1, _format_value(value))


def generate_annual_export(producer: Entity, year: int) -> BufferedReader:
    """Generate an Excel file with all biomethane data for a producer and a given year."""
    filename = f"biomethane_export_{year}_{slugify(producer.name)}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    file_path = os.path.join(tempfile.gettempdir(), filename)

    workbook = xlsxwriter.Workbook(file_path)
    header_format = workbook.add_format({"bold": True})

    # Contrat
    contract = BiomethaneContract.objects.filter(producer=producer).first()
    _write_sheet(
        workbook,
        "Contrat",
        _fields_from_model(contract, _auto_fields(BiomethaneContract)) if contract else [],
        header_format,
    )

    # Unité de production
    production_unit = BiomethaneProductionUnit.objects.filter(producer=producer).first()
    production_unit_fields = _PRODUCTION_UNIT_SITE_FIELDS + _auto_fields(BiomethaneProductionUnit)
    _write_sheet(
        workbook,
        "Unité de production",
        _fields_from_model(production_unit, production_unit_fields) if production_unit else [],
        header_format,
    )

    # Site d'injection
    injection_site = BiomethaneInjectionSite.objects.filter(producer=producer).first()
    _write_sheet(
        workbook,
        "Site d'injection",
        _fields_from_model(injection_site, _auto_fields(BiomethaneInjectionSite)) if injection_site else [],
        header_format,
    )

    # Digestat
    digestate = BiomethaneDigestate.objects.filter(producer=producer, year=year).first()
    _write_sheet(
        workbook,
        "Digestat",
        _fields_from_model(digestate, _auto_fields(BiomethaneDigestate)) if digestate else [],
        header_format,
    )

    # Énergie
    energy = BiomethaneEnergy.objects.filter(producer=producer, year=year).first()
    _write_sheet(
        workbook,
        "Énergie",
        _fields_from_model(energy, _auto_fields(BiomethaneEnergy)) if energy else [],
        header_format,
    )

    # Approvisionnement (table)
    supply_plan = BiomethaneSupplyPlan.objects.filter(producer=producer, year=year).first()
    _write_supply_inputs_sheet(workbook, supply_plan, header_format)

    # Stockage digestat (table)
    _write_digestate_storage_sheet(workbook, producer, header_format)

    # Épandage digestat (table)
    _write_digestate_spreading_sheet(workbook, digestate, header_format)

    workbook.close()

    return open(file_path, "rb")
