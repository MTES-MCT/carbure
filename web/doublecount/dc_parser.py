from calendar import c
import re
import traceback
from typing import List, TypedDict, Tuple
from openpyxl import Workbook, load_workbook
from core.common import CarbureException

from doublecount.dc_sanity_checks import DoubleCountingError


class SourcingRow(TypedDict):
    line: int
    year: int
    feedstock: str | None
    origin_country: str | None
    supply_country: str | None
    transit_country: str | None
    metric_tonnes: int


class ProductionRow(TypedDict):
    line: int
    year: int
    feedstock: str | None
    feedstock_check: str | None
    biofuel: str | None
    max_production_capacity: int
    estimated_production: int
    requested_quota: int


def parse_dc_excel(
    filename: str,
) -> Tuple[List[SourcingRow], List[ProductionRow]]:
    excel_file = load_workbook(filename, data_only=True)

    info = parse_info(excel_file)
    sourcing_history = parse_sourcing(excel_file, "Historique d'approvisionnement")
    sourcing_forecast = parse_sourcing(excel_file, "Approvisionnement prévisionnel")
    production_forecast = parse_production(excel_file)

    return info, sourcing_history, sourcing_forecast, production_forecast


def parse_info(excel_file: Workbook):
    try:
        presentation = excel_file["Présentation"]
        application = excel_file["Reconnaissance double comptage"]

        production_site = presentation[5][2].value

        try:
            # loop through reconaissance sheet to find the base year defined in it
            year_row_index = 0
            for i, row in enumerate(application.iter_rows()):
                year_row_index = i
                if row[6].value == "Première année de reconnaissance":
                    break
            year = int(application[year_row_index + 2][6].value)
        except:
            year = 0

        return {
            "production_site": production_site,
            "year": year,
        }
    except:
        traceback.print_exc()
        return {"production_site": None, "year": 0}


def parse_sourcing(excel_file: Workbook, sheet_name: str) -> List[SourcingRow]:
    if sheet_name not in excel_file:
        raise CarbureException(
            DoubleCountingError.BAD_WORKSHEET_NAME, {"sheet_name": sheet_name}
        )

    sourcing_sheet = excel_file[sheet_name]
    sourcing_rows: List[SourcingRow] = []

    current_year = -1

    for line, row in enumerate(sourcing_sheet.iter_rows()):
        current_year = extract_year(row[1].value, current_year)

        feedstock_name = row[2].value
        origin_country_cell = row[3].value
        supply_country_cell = row[4].value
        transit_country_cell = row[5].value

        # skip row if no year or feedstock is defined
        if (
            not feedstock_name
            or not origin_country_cell
            or feedstock_name == origin_country_cell
        ):
            continue

        feedstock = get_feedstock_from_dc_feedstock(feedstock_name)

        # this allow to accept row without year but only when feedstock recognized
        if current_year == -1 and feedstock is None:
            continue

        origin_country = extract_country_code(origin_country_cell)
        supply_country = extract_country_code(supply_country_cell)
        transit_country = extract_country_code(transit_country_cell)

        sourcing: SourcingRow = {
            "line": line + 1,
            "year": current_year,
            "feedstock": feedstock,
            "origin_country": origin_country,
            "supply_country": supply_country,
            "transit_country": transit_country,
            "metric_tonnes": 0,
        }

        if sheet_name == "Approvisionnement prévisionnel":
            sourcing["metric_tonnes"] = row[6].value
        elif sheet_name == "Historique d'approvisionnement":
            sourcing["metric_tonnes"] = row[8].value
            # sourcing["supplier_name"] = row[6].value
            # sourcing["supplier_certificate"] = row[7].value

        sourcing_rows.append(sourcing)

    return sourcing_rows


def intOrZero(value):
    try:
        return int(value)
    except:
        return 0


def parse_production(excel_file: Workbook) -> List[ProductionRow]:
    production_rows: List[ProductionRow] = []

    current_year = -1
    production_sheet = excel_file["Production"]

    for line, row in enumerate(production_sheet.iter_rows()):
        current_year = extract_year(row[1].value, current_year)

        biofuel_name = row[2].value
        feedstock_name = row[3].value
        feedstock_name_check = row[8].value
        max_production_capacity = intOrZero(row[4].value)
        estimated_production = intOrZero(row[9].value)

        if current_year == -1 or not feedstock_name or not biofuel_name:
            continue

        feedstock = get_feedstock_from_dc_feedstock(feedstock_name)
        feedstock_check = feedstock if feedstock_name == feedstock_name_check else ""
        biofuel = dc_biofuel_to_carbure_biofuel.get(biofuel_name.strip(), None)
        production: ProductionRow = {
            "line": line + 1,
            "year": current_year,
            "feedstock": feedstock,
            "feedstock_check": feedstock_check,
            "biofuel": biofuel,
            "max_production_capacity": max_production_capacity,
            "estimated_production": estimated_production,
            "requested_quota": 0,
        }

        production_rows.append(production)

    current_year = -1
    quota_sheet = excel_file["Reconnaissance double comptage"]

    for row in quota_sheet.iter_rows():
        current_year = extract_year(row[1].value, current_year)

        biofuel_name = row[2].value
        feedstock_name = row[3].value
        requested_quota = row[4].value

        if current_year == -1 or not feedstock_name or not biofuel_name:
            continue

        biofuel = dc_biofuel_to_carbure_biofuel.get(biofuel_name.strip(), None)
        feedstock = get_feedstock_from_dc_feedstock(feedstock_name)

        for production in production_rows:
            if (
                biofuel
                and feedstock
                and current_year == production["year"]
                and biofuel == production["biofuel"]
                and feedstock == production["feedstock"]
            ):
                production["requested_quota"] = requested_quota

    return production_rows


def extract_year(year_str: str, current_year: int):
    try:
        match = re.search("([0-9]{4})", str(year_str))
        year = match.group(0)
        return int(year)
    except:
        return current_year


def extract_country_code(country_str: str) -> str | None:
    if country_str:
        return (country_str or "").split("-")[0].strip()
    else:
        return None


def get_feedstock_from_dc_feedstock(feedstock_name: str) -> str | None:
    feedstock_name = feedstock_name.replace("’", "'")
    return dc_feedstock_to_carbure_feedstock.get(feedstock_name.strip(), None)


dc_feedstock_to_carbure_feedstock: dict[str, str | None] = {
    "Algues": "ALGUES",
    "Bagasse": "BAGASSE",
    "Balles (enveloppes)": "BALLES",
    "Betterave": "BETTERAVE",
    "Blé": "BLE",
    "Boues de stations d'épuration": "BOUES_EPURATION",
    "Brai de tallol": "BRAI_TALLOL",
    "Canne à sucre": "CANNE_A_SUCRE",
    "Captage de carbone": None,
    "Colza": "COLZA",
    "Coques": "COQUES",
    "Déchets de bois": "DECHETS_BOIS",
    "Déchets industriels": "DECHETS_INDUSTRIELS",
    "Déchets municipaux en mélange (Hors déchets ménagers triés)": "DECHETS_MUNICIPAUX_MELANGE",
    "Déchets organiques ménagers": "DECHETS_ORGANIQUES_MENAGERS",
    "Distillat d'acide gras de palme": None,
    "Effluents d'huileries de palme et rafles": "EFFLUENTS_HUILERIES_PALME_RAFLE",
    "Effluents d'huileries de palme et rafles (POME)": "EFFLUENTS_HUILERIES_PALME_RAFLE",
    "Egouts Pauvres de 2e Extractions": "EP2",
    "Fumier humide": "FUMIER_HUMIDE",
    "Fumier sec": "FUMIER_SEC",
    "Glycérine brute": "FUMIER_HUMIDE",
    "Graisses de flotation": "GRAISSES_FLOTTATION",
    "Huile alimentaire usagée": "HUILE_ALIMENTAIRE_USAGEE",
    "Huile de palme": "HUILE_PALME",
    "Huiles ou graisses animales (C I)": "HUILES_OU_GRAISSES_ANIMALES_CAT1_CAT2",
    "Huiles ou graisses animales (C II)": "HUILES_OU_GRAISSES_ANIMALES_CAT1_CAT2",
    "Huiles ou graisses animales (C III)": "HUILES_OU_GRAISSES_ANIMALES_CAT3",
    "Lies de vin": "LIES_DE_VIN",
    "Maïs": "MAIS",
    "Marcs de raisin": "MARC_DE_RAISIN",
    "Mat. cellulosiques d'origine non alimentaire": "MAT_CELLULOSIQUE_NON_ALIMENTAIRE",
    "Mat. ligno-cellulosiques (Hors grumes de sciage & de placage)": "MAT_LIGNO_CELLULOSIQUE",
    "Orge": "ORGE",
    "Paille": "PAILLE",
    "Râpes": "RAPES",
    "Seigle": "SEIGLE",
    "Soja": "SOJA",
    "Tallol": "TALLOL",
    "Tournesol ": "TOURNESOL",
    "Triticale": "TRITICALE",
}

dc_biofuel_to_carbure_biofuel: dict[str, str | None] = {
    "Bio Iso-Butène": None,
    "Bio Iso-Octane": None,
    "Bio-essence de synthèse": None,
    "Bio-ETBE": "ETBE",
    "Biogazole de synthèse": "BG",
    "EEHA": None,
    "EEHU": None,
    "EEHV": None,
    "EMAG de POME": "EMAG",
    "EMAG": "EMAG",
    "EMHA": "EMHA",
    "EMHU": "EMHU",
    "EMHV": "EMHV",
    "ETBE": "ETBE",
    "Ethanol d'EP2": "ETH",
    "Ethanol pour ED95": "ED95",
    "Ethanol": "ETH",
    "HVO-C": "HVOC",
    "HVO-E": "HVOE",
    "HVO-G": "HVOG",
    "Méthanol": "MT",
    "MTBE": "MTBE",
    "TAEE": "TAEE",
    "TAME": None,
}
