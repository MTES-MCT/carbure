import os
import django
import argparse
from django.db.models import Sum, Count, Min, Q
import calendar
import datetime

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()

from core.models import *
from django.core import serializers
    
def snapshot_feyzin_data():
    trans = ETBETransformation.objects.all()
    serialized_obj = serializers.serialize('json', trans)
    f = open('transformations.json', 'w')
    f.write(serialized_obj)
    f.close()
    
if __name__ == '__main__':
    snapshot_feyzin_data()
