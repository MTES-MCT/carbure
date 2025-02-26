import argparse
import os

import django
import pandas as pd
from django.db import transaction
from pyparsing import col

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()

from doublecount.models import DoubleCountingApplication, DoubleCountingProduction, DoubleCountingSourcing  # noqa: E402


@transaction.atomic
def restore_deleted_dc_applications(apply, path):
    print("> Loading csv files")
    applications = pd.read_csv(f"{path}/applications.csv").to_dict("records")
    production = pd.read_csv(f"{path}/production.csv").to_dict("records")
    sourcing = pd.read_csv(f"{path}/sourcing.csv").to_dict("records")

    db_applications = [DoubleCountingApplication(**a) for a in applications]
    db_production = [DoubleCountingProduction(**p) for p in production]
    db_sourcing = [DoubleCountingSourcing(**s) for s in sourcing]


    if apply:
      print("> Insert rows in database")
      DoubleCountingApplication.objects.bulk_create(db_applications, batch_size=1000)
      DoubleCountingProduction.objects.bulk_create(db_production, batch_size=1000)
      DoubleCountingSourcing.objects.bulk_create(db_sourcing, batch_size=1000)

    print("> Done")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Reinsert previously deleted DC data")
    parser.add_argument("--apply", dest="apply", action="store_true", default=False, help="Save the changes to the db")
    parser.add_argument("--path", dest="path", action="store", default=1000, help="Path to csv files folder")
    args = parser.parse_args()
    restore_deleted_dc_applications(apply=args.apply, path=args.path)
