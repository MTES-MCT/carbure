import re
import unicodedata

dc_feedstock_to_carbure_feedstock = {
    "alcool pur de marc de raisin": "ETHANOL_PUR_MARC_RAISIN",
    "alcool pur de lies de vin": "ETHANOL_PUR_LIES_VIN",
    "balles (enveloppes)": "BALLES",
    "boues de stations d'épuration": "BOUES_EPURATION",
    "brai de tallol": "BRAI_TALLOL",
    "déchets de bois": "DECHETS_BOIS",
    "déchets municipaux en mélange (hors déchets ménagers triés)": "DECHETS_MUNICIPAUX_MELANGE",
    "distillat d'acide gras de palme": "DISTILLAT_ACIDE_GRAS_PALME",
    "effluents d'huileries de palme et rafles": "EFFLUENTS_HUILERIES_PALME_RAFLE",
    "effluents d'huileries de palme et rafles (pome)": "EFFLUENTS_HUILERIES_PALME_RAFLE",
    "egouts pauvres de 2e extractions": "EP2",
    "ethanol de lies de vin": "ETHANOL_PUR_LIES_VIN",
    "ethanol pur de lies de vin": "ETHANOL_PUR_LIES_VIN",
    "ethanol pur de marc de raisin": "ETHANOL_PUR_MARC_RAISIN",
    "graisses de flotation": "GRAISSES_FLOTTATION",
    "huile de palme": "HUILE_PALME",
    "huiles ou graisses animales (c i)": "HUILES_OU_GRAISSES_ANIMALES_CAT1_CAT2",
    "huiles ou graisses animales (c ii)": "HUILES_OU_GRAISSES_ANIMALES_CAT1_CAT2",
    "huiles ou graisses animales (c iii)": "HUILES_OU_GRAISSES_ANIMALES_CAT3",
    "marcs de raisin": "MARC_DE_RAISIN",
    "mat. cellulosiques d'origine non alimentaire": "MAT_CELLULOSIQUE_NON_ALIMENTAIRE",
    "mat. ligno-cellulosiques (hors grumes de sciage & de placage)": "MAT_LIGNO_CELLULOSIQUE",
    "amidons résiduels déchets": "AMIDON_RESIDUEL_DECHETS",
    "méthanol brut issu de la pâte kraft obtenue à partir de la pulpe de bois": "RAW_METHANOL_KRAFT_PULPING",
    "culture intermédiaire": "CIVE",
    "alcools mauvais goûts": "MAUVAIS_GOUTS",
    "huiles acides de pâtes de neutralisation": "PATES_DE_NEUTRALISATION",
    "ethanol de rinçage de lignes de production de l'industrie cosmétique": "ETHANOL_DE_RINÇAGE",
    "alcool résiduel de synthèse pharmaceutique": "ALCOOL_DE_SYNTHESE_PHARMACEUTIQUE",
    "huiles acides ayant une haute teneur en soufre": "HUILES_ACIDES_NEUTRALISEES_AYANT_UNE_HAUTE_TENEUR_EN_SOUFRE",
    "déchets industriels autres": "DECHETS_INDUSTRIELS",
}


dc_biofuel_to_carbure_biofuel = {
    "bio isobutène": None,
    "bio isooctane": None,
    "bes": "Bio-essence de synthèse",
    "bioessence de synthèse": "BES",
    "bioetbe": "ETBE",
    "biogazole de synthèse": "BG",
    "emag de pome": "EMAG",
    "ethanol d'ep2": "ETH",
    "ethanol pour ed95": "ED95",
    "ethanol": "ETH",
    "hccc": "HCC",
    "hcce": "HCE",
    "hccg": "HCG",
    "méthanol": "MT",
    "ester ethylique d'huiles animales": "EEHA",
    "ester ethylique d'huiles usagées": "EEHU",
    "ester ethylique d'huiles végétales": "EEHV",
    "ester méthylique d'acide gras": "EMAG",
    "ester méthylique d'acide gras d'effluents d'huilerie de palme": "EMAG",
    "ester méthylique d'huiles animales": "EMHA",
    "ester méthylique d'huiles usagées": "EMHU",
    "ester méthylique d'huiles végétales": "EMHV",
    "ethyl tert-butyl ether": "ETBE",
    "huiles hydrotraitées carburéacteur": "HVOC",
    "huiles hydrotraitées essences": "HVOE",
    "huiles hydrotraitées gazoles": "HVOG",
    "methyl tert-butyl ether": "MTBE",
    "tert-amyl ethyl ether": "TAEE",
    "tert-amyl methyl ether": "TAME",
}


def to_upper_snake_case(value: str) -> str:
    value = value.strip()
    value = value.translate(str.maketrans({"œ": "oe", "Œ": "OE", "æ": "ae", "Æ": "AE"}))
    value = unicodedata.normalize("NFKD", value)
    value = "".join(character for character in value if not unicodedata.combining(character))
    value = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", value)
    value = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", value)
    value = re.sub(r"[^A-Za-z0-9]+", "_", value)
    return value.strip("_").upper()


def get_feedstock_from_dc_feedstock(feedstock_name: str) -> str | None:
    if not feedstock_name:
        return None
    feedstock_name = feedstock_name.replace("’", "'").strip().lower()
    return dc_feedstock_to_carbure_feedstock.get(feedstock_name, to_upper_snake_case(feedstock_name))


def get_biofuel_from_dc_biofuel(biofuel_name: str) -> str | None:
    if not biofuel_name:
        return None
    biofuel_name = biofuel_name.replace("’", "'").replace("-", "").strip().lower()
    return dc_biofuel_to_carbure_biofuel.get(biofuel_name, to_upper_snake_case(biofuel_name))
