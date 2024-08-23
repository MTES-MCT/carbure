import argparse
import datetime
import os

import django
from tqdm import tqdm

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()

from core.models import CarbureLot
from transactions.sanity_checks.helpers import get_prefetched_data

DATE_BEGIN = datetime.date.today() - datetime.timedelta(days=540)  # approx 18 months


def calc_ml_score(year=None, period=None):
    data = get_prefetched_data()
    # {s.feedstock: s.default_value for s in ETDStats.objects.select_related('feedstock').all()}
    data["etd"]
    # {s.feedstock.code + s.origin.code_pays: s for s in EECStats.objects.select_related('feedstock', 'origin').all()}
    eec = data["eec"]
    # {s.feedstock.code + s.biofuel.code: s for s in EPStats.objects.select_related('feedstock', 'biofuel').all()}
    ep = data["ep"]

    lots = CarbureLot.objects.select_related("feedstock", "country_of_origin").filter(
        created_at__gt=DATE_BEGIN,
        lot_status__in=[CarbureLot.ACCEPTED, CarbureLot.FROZEN],
    )
    if year:
        lots = lots.filter(year=year)
    if period:
        lots = lots.filter(period=period)

    for l in tqdm(lots.iterator()):
        score = 0
        # eec penalisation
        if l.feedstock and l.country_of_origin:
            key = l.feedstock.code + l.country_of_origin.code_pays
            if key in eec:
                entry = eec[key]
                if l.eec < 0.8 * min(entry.default_value, entry.average):
                    score += (
                        (min(entry.default_value, entry.average) - l.eec) / min(entry.default_value, entry.average)
                    ) ** 2
                if l.eec > 1.2 * max(entry.default_value, entry.average):
                    score += (
                        (l.eec - max(entry.default_value, entry.average)) / max(entry.default_value, entry.average)
                    ) ** 2
        # ep penalisation
        key = l.feedstock.code + l.biofuel.code
        if key in ep:
            entry = ep[key]
            if l.ep < 0.8 * entry.average:
                score += ((entry.average - l.ep) / entry.average) ** 2
            if entry.default_value_max_ep > 0 and l.ep > 1.2 * entry.default_value_max_ep:
                score += ((l.ep - entry.default_value_max_ep) / entry.default_value_max_ep) ** 2

        # etd penalisation ###### NOT INCLUDED FOR NOW - fausse les resultats - trop de faux positifs, trop different du premier check
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
        if score > 0:
            l.ml_control_requested = True
        l.save()


def main():
    parser = argparse.ArgumentParser(description="Calculate machine learning score")
    parser.add_argument("--year", dest="year", action="store", help="year")
    parser.add_argument("--period", dest="period", action="store", help="period")
    args = parser.parse_args()

    calc_ml_score(args.year, args.period)


if __name__ == "__main__":
    main()
