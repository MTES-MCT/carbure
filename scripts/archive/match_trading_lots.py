import sys
import os
import django
import argparse
from django.db.models import Sum

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()


from core.models import *

def reassign():
    odd_lots = CarbureLot.objects.filter(carbure_client__entity_type=Entity.TRADER, delivery_type=CarbureLot.UNKNOWN, lot_status=CarbureLot.ACCEPTED)
    for lot in odd_lots:
        # find child
        try:
            child = CarbureLot.objects.get(parent_lot=lot)
            print('Found child')
            lot.delivery_type = CarbureLot.TRADING
            lot.save()
        except:
            print('Could not find child')       
            
if __name__ == '__main__':
    reassign()
    
