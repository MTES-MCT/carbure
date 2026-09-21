from django.utils.encoding import force_str

from traceability.models import Action

# Shared section colors so each industry reuses the same palette.
EXCEL_PRODUCTION_COLOR = "#D9EAF7"
EXCEL_TRANSPORT_COLOR = "#FCE4D6"
EXCEL_CONSUMPTION_COLOR = "#E2F0D9"

ACTION_EXCEL_COLUMNS = {
    "pos_id": {
        "header": "N° de POS",
        "comment": "N° de la preuve de durabilité (max 64 caractères)",
        "color": EXCEL_PRODUCTION_COLOR,
    },
    "certificate": {
        "header": "N° de certificat",
        "comment": "Liste de choix",
        "options": lambda entity, handler: list(
            handler.lookups.certificate(entity).values_list("certificate_id", flat=True)
        ),
        "color": EXCEL_PRODUCTION_COLOR,
    },
    "material": {
        "header": "Matière",
        "comment": "Liste de choix",
        "options": lambda entity, handler: list(handler.lookups.material(entity).values_list("name", flat=True)),
        "color": EXCEL_PRODUCTION_COLOR,
    },
    "quantity": {
        "header": "Quantité",
        "comment": "Chiffre strictement supérieur à 0",
        "color": EXCEL_CONSUMPTION_COLOR,
    },
    "site": {
        "header": "Site",
        "comment": "Liste de choix",
        "options": lambda entity, handler: list(handler.lookups.site(entity).values_list("name", flat=True)),
        "color": EXCEL_CONSUMPTION_COLOR,
    },
    "shipping_date": {
        "header": "Date d'expédition",
        "comment": "Format : JJ/MM/AAAA",
        "color": EXCEL_TRANSPORT_COLOR,
    },
    "shipping_distance": {
        "header": "Distance de livraison (km)",
        "comment": "Chiffre supérieur ou égal à 0",
        "color": EXCEL_TRANSPORT_COLOR,
    },
    "shipping_method": {
        "header": "Mode de transport",
        "comment": "Liste de choix",
        "options": [force_str(label) for _, label in Action.SHIPPING_METHODS],
        "color": EXCEL_TRANSPORT_COLOR,
    },
    "eec": {
        "header": "EEC",
        "comment": "Émissions résultant de l'extraction ou de la culture des matières premières - Chiffre supérieur ou égal à 0",  # noqa: E501
        "color": EXCEL_PRODUCTION_COLOR,
    },
    "el": {
        "header": "EL",
        "comment": "Émissions annualisées résultant de modifications des stocks de carbone dues à des changements dans l'affectation des sols - Chiffre supérieur ou égal à 0",  # noqa: E501
        "color": EXCEL_PRODUCTION_COLOR,
    },
    "ei": {
        "header": "EI",
        "comment": "Emissions liées aux intrants (gCO2eq/MJ de carburant) - Chiffre supérieur ou égal à 0",
        "color": EXCEL_PRODUCTION_COLOR,
    },
    "ep": {
        "header": "EP",
        "comment": "Emissions liées à la production (gCO2eq/MJ de carburant) - Chiffre supérieur ou égal à 0",
        "color": EXCEL_PRODUCTION_COLOR,
    },
    "etd": {
        "header": "ETD",
        "comment": "Emissions liées au transport et à la distribution (gCO2eq/MJ de carburant) - Chiffre supérieur ou égal à 0",  # noqa: E501
        "color": EXCEL_TRANSPORT_COLOR,
    },
    "eu": {
        "header": "EU",
        "comment": "Émissions résultant du carburant à l'usage (gCO2eq/MJ de carburant) - Chiffre supérieur ou égal à 0",
        "color": EXCEL_CONSUMPTION_COLOR,
    },
    "eccs": {
        "header": "ECCS",
        "comment": "Réductions d'émissions dues au captage et au stockage géologique du carbone (gCO₂éq/MJ de carburant) - Chiffre supérieur ou égal à 0",  # noqa: E501
        "color": EXCEL_CONSUMPTION_COLOR,
    },
    "esca": {
        "header": "ESCA",
        "comment": "Réductions d'émissions dues à l'accumulation du carbone dans les sols grâce à une meilleure gestion agricole - Chiffre supérieur ou égal à 0",  # noqa: E501
        "color": EXCEL_PRODUCTION_COLOR,
    },
    "eccr": {
        "header": "ECCR",
        "comment": "Réductions d'émissions dues au piégeage et à la substitution du CO2 - Chiffre supérieur ou égal à 0",
        "color": EXCEL_CONSUMPTION_COLOR,
    },
    "working_date": {
        "header": "Date de consommation",
        "comment": "Format : MM/AAAA",
        "color": EXCEL_CONSUMPTION_COLOR,
    },
}


def excel_column(key: str, **overrides) -> dict:
    return {"key": key, **ACTION_EXCEL_COLUMNS[key], **overrides}
