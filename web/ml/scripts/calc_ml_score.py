import argparse
import datetime
import os

import django
from tqdm import tqdm

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()

from core.models import CarbureLot  # noqa: E402
from transactions.sanity_checks.helpers import get_prefetched_data  # noqa: E402

DEFAULT_ML_SCORE_CONFIG = {
    "eec_threshold": 0.8,
    "eec_exponent": 2,
    "ep_threshold": 0.8,
    "ep_exponent": 2,
    "lookback_days": 540,  # approx 18 months, based on transaction creation date
    "control_threshold": 0.0,
}


def calc_ml_score(year=None, period=None, *, config=None):
    config = {**DEFAULT_ML_SCORE_CONFIG, **(config or {})}
    data = get_prefetched_data()
    # {s.feedstock.code + s.origin.code_pays: s for s in EECStats.objects.select_related('feedstock', 'origin').all()}
    eec = data["eec"]
    # {s.feedstock.code + s.biofuel.code: s for s in EPStats.objects.select_related('feedstock', 'biofuel').all()}
    ep = data["ep"]

    date_begin = datetime.date.today() - datetime.timedelta(days=config["lookback_days"])
    lots = CarbureLot.objects.select_related("feedstock", "country_of_origin").filter(
        created_at__gt=date_begin,
        lot_status__in=[CarbureLot.ACCEPTED, CarbureLot.FROZEN],
    )
    if year:
        lots = lots.filter(year=year)
    if period:
        lots = lots.filter(period=period)

    for lot in tqdm(lots.iterator()):
        score = 0
        # eec penalisation
        if lot.feedstock and lot.country_of_origin:
            key = lot.feedstock.code + lot.country_of_origin.code_pays
            if key in eec:
                entry = eec[key]
                if lot.eec < config["eec_threshold"] * min(entry.default_value, entry.average):
                    score += (
                        (min(entry.default_value, entry.average) - lot.eec) / min(entry.default_value, entry.average)
                    ) ** config["eec_exponent"]
        # ep penalisation
        key = lot.feedstock.code + lot.biofuel.code
        if key in ep:
            entry = ep[key]
            if lot.ep < config["ep_threshold"] * entry.average:
                score += ((entry.average - lot.ep) / entry.average) ** config["ep_exponent"]

        lot.ml_scoring = score
        lot.ml_control_requested = score > config["control_threshold"]
        lot.save()


def main():
    parser = argparse.ArgumentParser(description="Calculate machine learning score")
    parser.add_argument("--year", dest="year", action="store", help="year")
    parser.add_argument("--period", dest="period", action="store", help="period")
    args = parser.parse_args()

    calc_ml_score(args.year, args.period)


if __name__ == "__main__":
    main()
