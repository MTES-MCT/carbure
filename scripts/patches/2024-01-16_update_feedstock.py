import argparse
import code
import os
import django


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()

from tqdm import tqdm
from django.db import transaction
from django.core.paginator import Paginator
from core.models import CarbureLot, MatierePremiere
from certificates.models import DoubleCountingRegistration
from transactions.sanity_checks import bulk_sanity_checks, get_prefetched_data


@transaction.atomic
def rename_alcool_pur_marc_raisin():
    try:
        feedstock = MatierePremiere.objects.get(id=77)
    except:
        print(f"Feedstock {id} not found")
        return
    feedstock.name = "Ethanol pur de marc de raisin"
    feedstock.code = "ETHANOL_PUR_MARC_RAISIN"
    feedstock.save()


if __name__ == "__main__":
    rename_alcool_pur_marc_raisin()
