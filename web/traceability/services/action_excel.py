from io import BufferedReader

from core.import_export_template import create_import_template
from traceability.handlers.action import ActionIndustryHandler
from traceability.models import Action

COLUMNS = [
    {"key": "pos_id", "header": "N° de POS"},
    {"key": "material", "header": "Matière"},
    {"key": "quantity", "header": "Quantité"},
    {"key": "site", "header": "Site"},
    {"key": "shipping_date", "header": "Date d'expédition"},
    {"key": "shipping_distance", "header": "Distance de livraison"},
    {
        "key": "shipping_method",
        "header": "Mode de transport",
        "options": [label for _, label in Action.SHIPPING_METHODS],
    },
    {"key": "ei", "header": "EI"},
    {"key": "ep", "header": "EP"},
    {"key": "etd", "header": "ETD"},
    {"key": "eu", "header": "EU"},
    {"key": "eccs", "header": "ECCS"},
]


def build_action_import_template(handler: ActionIndustryHandler, entity=None) -> BufferedReader:
    columns = []
    for spec in COLUMNS:
        column = {"header": handler.excel_column_labels.get(spec["key"], spec["header"])}
        options = spec.get("options")
        if options is None:
            queryset = handler.lookup(spec["key"], entity)
            options = list(queryset.values_list("name", flat=True)) if queryset is not None else None
        if options:
            column["options"] = options
        columns.append(column)

    return create_import_template(
        title=f"Import actions {handler.industry}",
        columns=columns,
    )
