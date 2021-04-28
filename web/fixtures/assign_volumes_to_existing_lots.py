import sys, os
import django
import csv
import calendar
import datetime
import re
import argparse
import openpyxl
import pandas as pd
from typing import TYPE_CHECKING, Dict, List, Optional
from pandas._typing import FilePathOrBuffer, Scalar

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()

from core.models import LotV2, LotTransaction, Entity

def try_assign_volumes():
    entities = Entity.objects.filter(entity_type__in=['Producteur', 'Trader'])
    stock = LotTransaction.objects.filter(carbure_client__in=entities, lot__status='Validated', delivery_status__in=['N', 'AC', 'AA'])

    for s in stock:
        # do we have children?
        children = LotTransaction.objects.filter(lot__parent_lot=s.lot)
        if children.count() == 0:
            print('Setting remaining_volume back on %d' % (s.id))
            s.lot.remaining_volune = s.lot.volume
            s.lot.save()
        else:
            print('Found tx with children %d' % (s.id))
       
def main():
    try_assign_volumes()

if __name__ == '__main__':
    main()
