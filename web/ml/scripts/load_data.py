import os
import django
from django.db.models.aggregates import StdDev
from django.db.models import Avg, Count, Min, Max


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()

from ml.models import EECStats, EPStats, ETDStats
from core.models import Entity, MatierePremiere, Biocarburant, CarbureLot

def load_eec_data():
    data = CarbureLot.objects.filter(year__gte=2021, feedstock__category=MatierePremiere.CONV, lot_status__in=[CarbureLot.ACCEPTED, CarbureLot.FROZEN], country_of_origin__isnull=False)\
    .exclude(eec=0)\
    .values('feedstock', 'country_of_origin')\
    .annotate(nb_lots=Count('eec'), average=Avg('eec'), stddev=StdDev('eec'), min=Min('eec'), max=Max('eec'))\
    .exclude(nb_lots__lt=10)
    for entry in data:
        d = {
            'nb_lots': entry['nb_lots'],
            'stddev': round(entry['stddev'], 2),
            'average': round(entry['average'], 2),
        }
        EECStats.objects.update_or_create(feedstock_id=entry['feedstock'], origin_id=entry['country_of_origin'], defaults=d)

def load_ep_data():
    data = CarbureLot.objects.filter(year__gte=2021, lot_status__in=[CarbureLot.ACCEPTED, CarbureLot.FROZEN], country_of_origin__isnull=False)\
    .exclude(ep=0)\
    .values('biofuel', 'feedstock',)\
    .annotate(nb_lots=Count('ep'), average=Avg('ep'), stddev=StdDev('ep'), min=Min('ep'), max=Max('ep'))\
    .exclude(nb_lots__lt=10)
    for entry in data:
        d = {
            'nb_lots': entry['nb_lots'],
            'stddev': round(entry['stddev'], 2),
            'average': round(entry['average'], 2),
        }
        EPStats.objects.update_or_create(biofuel_id=entry['biofuel'], feedstock_id=entry['feedstock'], defaults=d)

def load_etd_data():
    data = {
        'BETTERAVE': 2,
        'BLE': 2,
        'MAIS': 2,
        'CANNE_A_SUCRE': 9,
        'SOJA': 13,
        'TOURNESOL': 1,
        'COLZA': 1,
        'HUILE_ALIMENTAIRE_USAGEE': 1,
    }
    for k, v in data.items():
        feedstock = MatierePremiere.objects.get(code=k)
        ETDStats.objects.update_or_create(feedstock=feedstock, default_value=v)

if __name__ == '__main__':
    load_eec_data()
    load_ep_data()
    load_etd_data()
