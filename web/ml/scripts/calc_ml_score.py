import argparse
import os
import django
from tqdm import tqdm
import datetime

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()

from api.v4.helpers import get_prefetched_data
from core.models import CarbureLot
from ml.models import EECStats, EPStats, ETDStats

DATE_BEGIN = datetime.date.today() - datetime.timedelta(days=540) # approx 18 months

def calc_ml_score(args):
    data = get_prefetched_data()
    # {s.feedstock: s.default_value for s in ETDStats.objects.select_related('feedstock').all()}
    etd = data['etd']
    #{s.feedstock.code + s.origin.code_pays: s for s in EECStats.objects.select_related('feedstock', 'origin').all()}
    eec = data['eec']
    # {s.feedstock.code + s.biofuel.code: s for s in EPStats.objects.select_related('feedstock', 'biofuel').all()}
    ep = data['ep']

    lots = CarbureLot.objects.select_related('feedstock', 'country_of_origin').filter(created_at__gt=DATE_BEGIN, lot_status__in=[CarbureLot.ACCEPTED, CarbureLot.FROZEN])
    if args.year:
        lots = lots.filter(year=args.year)
    
    for l in tqdm(lots.iterator()):
        score = 0
        # eec penalisation
        if l.feedstock and l.country_of_origin:
            key = l.feedstock.code + l.country_of_origin.code_pays
            if key in eec:
                entry = eec[key]
                if l.eec < 0.8 * min(entry.default_value, entry.average):
                    score += ((min(entry.default_value, entry.average) - l.eec) / min(entry.default_value, entry.average))**2
                if l.eec > 1.2 * max(entry.default_value, entry.average):
                    score += ((l.eec - max(entry.default_value, entry.average)) / max(entry.default_value, entry.average))**2
        # ep penalisation
        key = l.feedstock.code + l.biofuel.code
        if key in ep:
            entry = ep[key]
            if l.ep < 0.8 * entry.average:
                score += ((entry.average - l.ep) / entry.average)**2
            if entry.default_value_max_ep > 0 and l.ep > 1.2 * entry.default_value_max_ep:
                score += ((l.ep - entry.default_value_max_ep) / entry.default_value_max_ep)**2
                
        # etd penalisation
        # if l.feedstock in etd:
        #    default_value = etd[l.feedstock]
        #    if l.etd > 2 * default_value and l.etd > 5:
        #        score += 1 # louche - ETD trop gros
        #    if l.country_of_origin:
        #        if not l.country_of_origin.is_in_europe and l.etd <= default_value:
        #            score += 1 # valeur ETD par defaut sur un lot qui vient de loin
        #        if l.country_of_origin.is_in_europe and l.etd == default_value:
        #            score += 0.5 # lot ne vient pas de loin, pas d'effort de calcul
        l.ml_scoring = score
        l.save()

def main():
    parser = argparse.ArgumentParser(description='Calculate machine learning score')
    parser.add_argument('--year', dest='year', action='store', help='year')    
    args = parser.parse_args()

    calc_ml_score(args)

if __name__ == '__main__':
    main()
