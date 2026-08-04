import os
import tempfile
import uuid
from io import BufferedReader

import xlsxwriter
from django.utils.text import slugify

from biomethane.models import (
    BiomethaneContract,
    BiomethaneDigestate,
    BiomethaneEnergy,
    BiomethaneEnergyMonthlyReport,
    BiomethaneInjectionSite,
    BiomethaneProductionUnit,
    BiomethaneSupplyPlan,
)
from biomethane.models.biomethane_digestate_spreading import BiomethaneDigestateSpreading
from biomethane.models.biomethane_digestate_storage import BiomethaneDigestateStorage
from biomethane.models.biomethane_supply_input import BiomethaneSupplyInput
from core.models import Entity
from core.utils import format_month_label


def _verbose_name(model_class, field_name):
    """Get verbose_name for a model field, with fallback to a formatted field name."""
    try:
        return str(model_class._meta.get_field(field_name).verbose_name)
    except Exception:
        attr = getattr(model_class, field_name, None)
        if isinstance(attr, property) and getattr(attr, "verbose_name", None):
            return str(attr.verbose_name)
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
        display_method = getattr(instance, f"get_{field_name}_display", None)
        if callable(display_method):
            value = display_method()

        result.append((label, value))
    return result


def _get_display_value(instance, field_name):
    """Return the human-readable display value for a field if choices are defined."""
    display_method = getattr(instance, f"get_{field_name}_display", None)
    if callable(display_method):
        return display_method()
    return getattr(instance, field_name, None)


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
    "energy",  # owner FK for BiomethaneEnergyMonthlyReport
    "year",
}


def _auto_fields(model_class, virtual_field=False):
    """Return exportable field names for a model, skipping internal/structural ones."""
    fields = [f.name for f in model_class._meta.local_fields if f.name not in _SKIP_FIELDS]

    if not virtual_field:
        return fields

    virtual_fields = [
        name
        for name, attr in model_class.__dict__.items()
        if isinstance(attr, property) and getattr(attr, "is_virtual_field", False)
    ]
    return fields + virtual_fields


# BiomethaneProductionUnit inherits from Site via multi-table inheritance.
# Site fields do not appear in local_fields, so we list them explicitly with labels.
_PRODUCTION_UNIT_SITE_FIELDS = [
    ("Nom du site de production", "name"),
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
            value = _get_display_value(supply_input, field_name)
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
            value = _get_display_value(storage, field_name)
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
            value = _get_display_value(spreading, field_name)
            sheet.write(row_idx, col_idx, _format_value(value))


def _write_energy_monthly_reports_sheet(workbook, energy, header_format):
    """Write an Énergie mensuelle sheet with one row per monthly report."""
    sheet = workbook.add_worksheet("Énergie mensuelle")
    columns = [
        (fn, _verbose_name(BiomethaneEnergyMonthlyReport, fn))
        for fn in _auto_fields(BiomethaneEnergyMonthlyReport, virtual_field=True)
    ]
    sheet.set_column(0, len(columns) - 1, 35)
    for col_idx, (_, label) in enumerate(columns):
        sheet.write(0, col_idx, label, header_format)

    if energy is None:
        return

    monthly_reports = BiomethaneEnergyMonthlyReport.objects.filter(energy=energy).order_by("month")
    for row_idx, report in enumerate(monthly_reports, start=1):
        for col_idx, (field_name, _) in enumerate(columns):
            value = getattr(report, field_name, None)
            if field_name == "month":
                value = format_month_label(value, locale="fr")
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
    filename = f"biomethane_export_{year}_{slugify(producer.name)}_{uuid.uuid4().hex}.xlsx"
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

    # Déclaration production énergie mensuelle (table)
    _write_energy_monthly_reports_sheet(workbook, energy, header_format)

    # Approvisionnement (table)
    supply_plan = BiomethaneSupplyPlan.objects.filter(producer=producer, year=year).first()
    _write_supply_inputs_sheet(workbook, supply_plan, header_format)

    # Stockage digestat (table)
    _write_digestate_storage_sheet(workbook, producer, header_format)

    # Épandage digestat (table)
    _write_digestate_spreading_sheet(workbook, digestate, header_format)

    workbook.close()

    return open(file_path, "rb")
