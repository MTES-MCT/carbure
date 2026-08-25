from collections.abc import Sequence
from dataclasses import dataclass, replace
from io import BufferedReader

from core.import_export_template import TemplateColumns, create_import_template
from traceability.handlers.action import ActionIndustryHandler
from traceability.models import Action


@dataclass(frozen=True)
class ActionExcelColumn:
    key: str
    label: str
    options: Sequence[str] | None = None


DEFAULT_ACTION_EXCEL_COLUMNS = [
    ActionExcelColumn(key="pos_id", label="N° de POS"),
    ActionExcelColumn(key="quantity", label="Quantité"),
    ActionExcelColumn(key="shipping_date", label="Date d'expédition"),
    ActionExcelColumn(key="shipping_distance", label="Distance de livraison"),
    ActionExcelColumn(
        key="shipping_method",
        label="Mode de transport",
        options=[label for _, label in Action.SHIPPING_METHODS],
    ),
    ActionExcelColumn(key="ei", label="EI"),
    ActionExcelColumn(key="ep", label="EP"),
    ActionExcelColumn(key="etd", label="ETD"),
    ActionExcelColumn(key="eu", label="EU"),
    ActionExcelColumn(key="eccs", label="ECCS"),
]


def build_action_import_template(handler: ActionIndustryHandler) -> BufferedReader:
    columns = resolve_action_excel_columns(handler)
    return create_import_template(
        title=f"Import actions {handler.industry}",
        columns=_to_template_columns(columns),
    )


def resolve_action_excel_columns(handler: ActionIndustryHandler) -> list[ActionExcelColumn]:
    labels = handler.excel_column_labels
    unknown = set(labels) - {column.key for column in DEFAULT_ACTION_EXCEL_COLUMNS}
    if unknown:
        raise ValueError(f"Handler {handler.industry} relabels unknown columns: {sorted(unknown)}")

    return [replace(column, label=labels.get(column.key, column.label)) for column in DEFAULT_ACTION_EXCEL_COLUMNS]


def _to_template_columns(columns: Sequence[ActionExcelColumn]) -> list[TemplateColumns]:
    template_columns: list[TemplateColumns] = []
    for column in columns:
        spec: TemplateColumns = {"header": column.label}
        if column.options:
            spec["options"] = list(column.options)
        template_columns.append(spec)
    return template_columns
