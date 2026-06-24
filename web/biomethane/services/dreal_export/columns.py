from collections.abc import Callable
from dataclasses import dataclass

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
    _get_display_value,
    _verbose_name,
)

from .context import ExportRowContext

# Pastel background colors per export section (header + data cells).
SECTION_COLORS = {
    "producer": "#EEEEEE",
    "production_unit": "#E8F4FC",
    "contract": "#FFF0E0",
    "injection_site": "#E8FCE8",
    "digestate": "#FCE8F0",
    "energy": "#F0E8FC",
    "supply_plan": "#E8FCF0",
}


@dataclass(frozen=True)
class ColumnDef:
    label: str
    section: str
    resolve: Callable[[ExportRowContext], object]


def section_formats(workbook):
    """Return header and cell formats keyed by section name."""
    formats = {}
    for section, color in SECTION_COLORS.items():
        formats[section] = {
            "header": workbook.add_format({"bold": True, "bg_color": color}),
            "cell": workbook.add_format({"bg_color": color}),
        }
    return formats


def _model_field_column(label: str, section: str, attr: str, field_name: str) -> ColumnDef:
    def resolve(ctx: ExportRowContext, _attr=attr, _field_name=field_name):
        obj = getattr(ctx, _attr, None)
        if obj is None:
            return ""
        return _get_display_value(obj, _field_name)

    return ColumnDef(label=label, section=section, resolve=resolve)


def _model_columns(model_class, section: str, attr: str, extra_fields=()) -> list[ColumnDef]:
    columns = [_model_field_column(label, section, attr, field_name) for label, field_name in extra_fields]
    for field_name in _auto_fields(model_class):
        columns.append(
            _model_field_column(_verbose_name(model_class, field_name), section, attr, field_name),
        )
    return columns


def _energy_columns() -> list[ColumnDef]:
    columns = _model_columns(BiomethaneEnergy, "energy", "energy")
    columns.extend(
        [
            ColumnDef(
                "Quantité de biométhane injecté (Nm3/an)",
                "energy",
                lambda ctx: ctx.energy_metrics.injected_biomethane_nm3_per_year if ctx.energy_metrics else None,
            ),
            ColumnDef(
                "Nombre d'heures de fonctionnement (h)",
                "energy",
                lambda ctx: ctx.energy_metrics.operating_hours if ctx.energy_metrics else None,
            ),
        ]
    )
    return columns


def build_column_defs() -> list[ColumnDef]:
    """Return ordered column definitions for the DREAL flat export."""
    return [
        ColumnDef("Nom du biométhaniseur", "producer", lambda ctx: ctx.producer.name),
        *_model_columns(BiomethaneProductionUnit, "production_unit", "production_unit", _PRODUCTION_UNIT_SITE_FIELDS),
        *_model_columns(BiomethaneContract, "contract", "contract"),
        *_model_columns(BiomethaneInjectionSite, "injection_site", "injection_site"),
        *_model_columns(BiomethaneDigestate, "digestate", "digestate"),
        *_energy_columns(),
        ColumnDef(
            "Tonnage total brut d'intrants (tMB)",
            "supply_plan",
            lambda ctx: ctx.supply_metrics.total_gross_volume_tmb if ctx.supply_metrics else None,
        ),
        ColumnDef(
            "Part cultures principales (%)",
            "supply_plan",
            lambda ctx: ctx.supply_metrics.primary_crop_percentage if ctx.supply_metrics else None,
        ),
        ColumnDef(
            "Part cultures intermédiaires (%)",
            "supply_plan",
            lambda ctx: ctx.supply_metrics.intermediate_crop_percentage if ctx.supply_metrics else None,
        ),
    ]
