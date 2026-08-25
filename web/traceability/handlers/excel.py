from traceability.models import Action

ACTION_EXCEL_COLUMNS = {
    "pos_id": {"header": "N° de POS"},
    "material": {"header": "Matière"},
    "quantity": {"header": "Quantité"},
    "site": {"header": "Site"},
    "shipping_date": {"header": "Date d'expédition"},
    "shipping_distance": {"header": "Distance de livraison"},
    "shipping_method": {
        "header": "Mode de transport",
        "options": [value for value, _ in Action.SHIPPING_METHODS],
    },
    "ei": {"header": "EI"},
    "ep": {"header": "EP"},
    "etd": {"header": "ETD"},
    "eu": {"header": "EU"},
    "eccs": {"header": "ECCS"},
}


def excel_column(key: str, **overrides) -> dict:
    return {"key": key, **ACTION_EXCEL_COLUMNS[key], **overrides}
