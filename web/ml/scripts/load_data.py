import os

import django
from django.db.models import Avg, Count, Max, Min
from django.db.models.aggregates import StdDev

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()

from core.models import CarbureLot, MatierePremiere
from ml.models import EECStats, EPStats, ETDStats


def load_eec_data():
    default_values = {
        "BETTERAVE": 9.6,
        "MAIS": 25.5,
        "BLE": 27,
        "ORGE": 27,
        "CANNE_A_SUCRE": 17.1,
        "SOJA": 22.1,
        "COLZA": 33.4,
        "TOURNESOL": 26.9,
    }

    data = (
        CarbureLot.objects.filter(
            year__gte=2021,
            feedstock__category=MatierePremiere.CONV,
            lot_status__in=[CarbureLot.ACCEPTED, CarbureLot.FROZEN],
            country_of_origin__isnull=False,
        )
        .exclude(eec=0)
        .values("feedstock", "feedstock__code", "country_of_origin")
        .annotate(nb_lots=Count("eec"), average=Avg("eec"), stddev=StdDev("eec"), min=Min("eec"), max=Max("eec"))
        .exclude(nb_lots__lt=10)
    )
    for entry in data:
        d = {
            "nb_lots": entry["nb_lots"],
            "stddev": round(entry["stddev"], 2),
            "average": round(entry["average"], 2),
        }
        if entry["feedstock__code"] in default_values:
            d["default_value"] = default_values[entry["feedstock__code"]]
        EECStats.objects.update_or_create(feedstock_id=entry["feedstock"], origin_id=entry["country_of_origin"], defaults=d)


def load_ep_data():
    referential = {
        "ETHBETTERAVE": (10.6, 38.3),
        "ETHMAIS": (2.6, 40.1),
        "ETHCANNE_A_SUCRE": (1.8, 1.8),
        "ETHBLE": (2.2, 42.5),
        "ETHORGE": (2.2, 42.5),
        "ETBEBETTERAVE": (10.6, 38.3),
        "ETBEMAIS": (2.6, 40.1),
        "ETBECANNE_A_SUCRE": (1.8, 1.8),
        "ETBEBLE": (2.2, 42.5),
        "ETBEORGE": (2.2, 42.5),
        "ED95BETTERAVE": (10.6, 38.3),
        "ED95MAIS": (2.6, 40.1),
        "ED95CANNE_A_SUCRE": (1.8, 1.8),
        "ED95BLE": (2.2, 42.5),
        "ED95ORGE": (2.2, 42.5),
        "EMHVCOLZA": (16.3, 16.3),
        "EMHVSOJA": (16.9, 16.9),
        "EMHVTOURNESOL": (16.5, 16.5),
        "EMHUHUILE_ALIMENTAIRE_USAGEE": (13, 13),
        "EMHAHUILES_OU_GRAISSES_ANIMALES_CAT3": (19.1, 19.1),
        "EMHAHUILES_OU_GRAISSES_ANIMALES_CAT1_CAT2": (19.1, 19.1),
        "HVOECOLZA": (15, 15),
        "HVOGCOLZA": (15, 15),
        "HVOESOJA": (15.2, 15.2),
        "HVOGSOJA": (15.2, 15.2),
        "HVOETOURNESOL": (14.7, 14.7),
        "HVOGTOURNESOL": (14.7, 14.7),
        "HOEHUILE_ALIMENTAIRE_USAGEE": (14.3, 14.3),
        "HOEHUILES_OU_GRAISSES_ANIMALES_CAT3": (20.3, 20.3),
        "HOGHUILES_OU_GRAISSES_ANIMALES_CAT3": (20.3, 20.3),
        "HOGHUILE_ALIMENTAIRE_USAGEE": (14.3, 14.3),
        "HOEHUILES_OU_GRAISSES_ANIMALES_CAT1_CAT2": (20.3, 20.3),
        "HOGHUILES_OU_GRAISSES_ANIMALES_CAT1_CAT2": (20.3, 20.3),
        "HVPCOLZA": (5.2, 5.2),
        "HVPSOJA": (5.9, 5.9),
        "HVPTOURNESOL": (5.4, 5.4),
        "HCUHUILE_ALIMENTAIRE_USAGEE": (0.8, 0.8),
    }

    data = (
        CarbureLot.objects.filter(
            year__gte=2021, lot_status__in=[CarbureLot.ACCEPTED, CarbureLot.FROZEN], country_of_origin__isnull=False
        )
        .exclude(ep=0)
        .values("biofuel", "feedstock", "biofuel__code", "feedstock__code")
        .annotate(nb_lots=Count("ep"), average=Avg("ep"), stddev=StdDev("ep"), min=Min("ep"), max=Max("ep"))
        .exclude(nb_lots__lt=10)
    )
    for entry in data:
        d = {
            "nb_lots": entry["nb_lots"],
            "stddev": round(entry["stddev"], 2),
            "average": round(entry["average"], 2),
        }
        key = entry["biofuel__code"] + entry["feedstock__code"]
        if key in referential:
            value = referential[key]
            d["default_value_min_ep"] = value[0]
            d["default_value_max_ep"] = value[1]
        EPStats.objects.update_or_create(biofuel_id=entry["biofuel"], feedstock_id=entry["feedstock"], defaults=d)


def load_etd_data():
    data = {
        "BETTERAVE": 2.3,
        "BLE": 2.2,
        "MAIS": 2.2,
        "CANNE_A_SUCRE": 9.7,
        "SOJA": 8.9,
        "TOURNESOL": 2.1,
        "COLZA": 1.8,
        "HUILE_ALIMENTAIRE_USAGEE": 1.7,
        "HUILES_OU_GRAISSES_ANIMALES_CAT1_CAT2": 1.5,
        "HUILES_OU_GRAISSES_ANIMALES_CAT3": 1.5,
    }
    for k, v in data.items():
        feedstock = MatierePremiere.objects.get(code=k)
        ETDStats.objects.update_or_create(feedstock=feedstock, default_value=v)


def load_ml_data():
    load_eec_data()
    load_ep_data()
    load_etd_data()


if __name__ == "__main__":
    load_ml_data()
