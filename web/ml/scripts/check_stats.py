import argparse
import os
import django
from tqdm import tqdm
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()

from core.models import CarbureLot
from ml.models import EECStats, EPStats, ETDStats


def check_ml_score():
    lots = (
        CarbureLot.objects.select_related("feedstock", "country_of_origin", "carbure_supplier")
        .filter(
            year__gt=2021,
            lot_status__in=[CarbureLot.ACCEPTED, CarbureLot.FROZEN],
            ml_scoring__gt=0.1,
        )
        .values("carbure_supplier__name", "ml_scoring")
    )
    df = pd.DataFrame(lots)
    # print(df)
    df["ml_scoring"].hist().plot()
    print(df[["ml_scoring"]].quantile([0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]))

    plt.show()


def main():
    check_ml_score()


if __name__ == "__main__":
    main()
