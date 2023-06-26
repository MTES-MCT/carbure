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
    "Tournesol": "TOURNESOL",
    "Triticale": "TRITICALE",
    "Distillat d'acide gras de palme": None,
}


dc_biofuel_to_carbure_biofuel: dict[str, str | None] = {
    "Bio Iso-Butène": None,
    "Bio Iso-Octane": None,
    "Bio-essence de synthèse": None,
    "Bio-ETBE": "ETBE",
    "Biogazole de synthèse": "BG",
    "EEHA": "EEHA",
    "EEHU": "EEHU",
    "EEHV": "EEHV",
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
    "HC-C": "HCC",
    "HC-E": "HCE",
    "HC-G": "HCG",
    "Méthanol": "MT",
    "MTBE": "MTBE",
    "TAEE": "TAEE",
    "TAME": "TAME",
}


def get_feedstock_from_dc_feedstock(feedstock_name: str) -> str | None:
    if not feedstock_name:
        return None
    feedstock_name = feedstock_name.replace("’", "'").strip()
    return dc_feedstock_to_carbure_feedstock.get(feedstock_name, None)


def get_biofuel_from_dc_biofuel(biofuel_name: str) -> str | None:
    if not biofuel_name:
        return None
    biofuel_name = biofuel_name.replace("’", "'").strip()
    return dc_biofuel_to_carbure_biofuel.get(biofuel_name, None)
