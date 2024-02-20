from email.policy import default


DC_FEEDSTOCK_UNRECOGNIZED = "__unrecognized__"

dc_feedstock_to_carbure_feedstock = {
    "alcool pur de marc de raisin": "ETHANOL_PUR_MARC_RAISIN",
    "alcool pur de lies de vin": "ETHANOL_PUR_LIES_VIN",
    "algues": "ALGUES",
    "bagasse": "BAGASSE",
    "balles (enveloppes)": "BALLES",
    "betterave": "BETTERAVE",
    "blé": "BLE",
    "boues de stations d'épuration": "BOUES_EPURATION",
    "brai de tallol": "BRAI_TALLOL",
    "canne à sucre": "CANNE_A_SUCRE",
    "colza": "COLZA",
    "coques": "COQUES",
    "déchets de bois": "DECHETS_BOIS",
    "déchets industriels": "DECHETS_INDUSTRIELS",
    "déchets municipaux en mélange (hors déchets ménagers triés)": "DECHETS_MUNICIPAUX_MELANGE",
    "déchets organiques ménagers": "DECHETS_ORGANIQUES_MENAGERS",
    "distillat d'acide gras de palme": "DISTILLAT_ACIDE_GRAS_PALME",
    "effluents d'huileries de palme et rafles": "EFFLUENTS_HUILERIES_PALME_RAFLE",
    "effluents d'huileries de palme et rafles (pome)": "EFFLUENTS_HUILERIES_PALME_RAFLE",
    "egouts pauvres de 2e extractions": "EP2",
    "ethanol de lies de vin": "ETHANOL_PUR_LIES_VIN",
    "ethanol pur de lies de vin": "ETHANOL_PUR_LIES_VIN",
    "ethanol pur de marc de raisin": "ETHANOL_PUR_MARC_RAISIN",
    "fumier humide": "FUMIER_HUMIDE",
    "fumier sec": "FUMIER_SEC",
    "glycérine brute": "GLYCERINE_BRUTE",
    "graisses de flotation": "GRAISSES_FLOTTATION",
    "huile alimentaire usagée": "HUILE_ALIMENTAIRE_USAGEE",
    "huile de palme": "HUILE_PALME",
    "huiles ou graisses animales (c i)": "HUILES_OU_GRAISSES_ANIMALES_CAT1_CAT2",
    "huiles ou graisses animales (c ii)": "HUILES_OU_GRAISSES_ANIMALES_CAT1_CAT2",
    "huiles ou graisses animales (c iii)": "HUILES_OU_GRAISSES_ANIMALES_CAT3",
    "lies de vin": "LIES_DE_VIN",
    "maïs": "MAIS",
    "marcs de raisin": "MARC_DE_RAISIN",
    "mat. cellulosiques d'origine non alimentaire": "MAT_CELLULOSIQUE_NON_ALIMENTAIRE",
    "mat. ligno-cellulosiques (hors grumes de sciage & de placage)": "MAT_LIGNO_CELLULOSIQUE",
    "orge": "ORGE",
    "paille": "PAILLE",
    "râpes": "RAPES",
    "seigle": "SEIGLE",
    "soja": "SOJA",
    "tallol": "TALLOL",
    "tournesol": "TOURNESOL",
    "triticale": "TRITICALE",
}


dc_biofuel_to_carbure_biofuel = {
    "bio isobutène": None,
    "bio isooctane": None,
    "bes": "Bio-essence de synthèse",
    "bioessence de synthèse": "BES",
    "bioetbe": "ETBE",
    "biogazole de synthèse": "BG",
    "eeha": "EEHA",
    "eehu": "EEHU",
    "eehv": "EEHV",
    "emag de pome": "EMAG",
    "emag": "EMAG",
    "emha": "EMHA",
    "emhu": "EMHU",
    "emhv": "EMHV",
    "etbe": "ETBE",
    "ethanol d'ep2": "ETH",
    "ethanol pour ed95": "ED95",
    "ethanol": "ETH",
    "hvoc": "HVOC",
    "hvoe": "HVOE",
    "hvog": "HVOG",
    "hcc": "HCC",
    "hce": "HCE",
    "hcg": "HCG",
    "méthanol": "MT",
    "mtbe": "MTBE",
    "taee": "TAEE",
    "tame": "TAME",
}


def get_feedstock_from_dc_feedstock(feedstock_name: str) -> str | None:
    if not feedstock_name:
        return None
    feedstock_name = feedstock_name.replace("’", "'").strip().lower()
    return dc_feedstock_to_carbure_feedstock.get(feedstock_name, None)


def get_biofuel_from_dc_biofuel(biofuel_name: str) -> str | None:
    if not biofuel_name:
        return None
    biofuel_name = biofuel_name.replace("’", "'").replace("-", "").strip().lower()
    return dc_biofuel_to_carbure_biofuel.get(biofuel_name, None)
