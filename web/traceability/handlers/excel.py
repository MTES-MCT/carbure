from traceability.models import Action

ACTION_EXCEL_COLUMNS = {
    "pos_id": {
        "header": "N° de POS",
        "comment": "N° de la preuve de durabilité (max 64 caractères)",
    },
    "material": {
        "header": "Matière",
        "comment": "Liste de choix",
        "options": lambda entity, handler: list(handler.lookups.material(entity).values_list("name", flat=True)),
    },
    "quantity": {
        "header": "Quantité",
        "comment": "Chiffre strictement supérieur à 0",
    },
    "site": {
        "header": "Site",
        "comment": "Liste de choix",
        "options": lambda entity, handler: list(handler.lookups.site(entity).values_list("name", flat=True)),
    },
    "shipping_date": {
        "header": "Date d'expédition",
        "comment": "Format : JJ/MM/AAAA",
    },
    "shipping_distance": {
        "header": "Distance de livraison",
        "comment": "Chiffre supérieur ou égal à 0",
    },
    "shipping_method": {
        "header": "Mode de transport",
        "comment": "Liste de choix",
        "options": [value for value, _ in Action.SHIPPING_METHODS],
    },
    "ei": {
        "header": "EI",
        "comment": "Emissions liées aux intrants (gCO2eq/MJ de carburant) - Chiffre supérieur ou égal à 0",
    },
    "ep": {
        "header": "EP",
        "comment": "Emissions liées à la production (gCO2eq/MJ de carburant) - Chiffre supérieur ou égal à 0",
    },
    "etd": {
        "header": "ETD",
        "comment": "Emissions liées au transport et à la distribution (gCO2eq/MJ de carburant) - Chiffre supérieur ou égal à 0",  # noqa: E501
    },
    "eu": {
        "header": "EU",
        "comment": "Émissions résultant du carburant à l'usage (gCO2eq/MJ de carburant) - Chiffre supérieur ou égal à 0",
    },
    "eccs": {
        "header": "ECCS",
        "comment": "Réductions d'émissions dues au captage et au stockage géologique du carbone (gCO₂éq/MJ de carburant) - Chiffre supérieur ou égal à 0",  # noqa: E501
    },
}


def excel_column(key: str, **overrides) -> dict:
    return {"key": key, **ACTION_EXCEL_COLUMNS[key], **overrides}
