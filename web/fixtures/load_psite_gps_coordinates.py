import sys, os
import django
import csv
import pandas as pd

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()

from producers.models import ProductionSite

filename = '%s/web/fixtures/csv/production_sites_gps.csv' % (os.environ['CARBURE_HOME'])

df = pd.read_csv(filename, delimiter=';').set_index('zip')['gps'].to_dict()
print(df)


psites = ProductionSite.objects.all()

for p in psites:
    if p.postal_code in df:
        print('FOUND gps for %s' % (p.name))
        print(df[p.postal_code])
        p.gps_coordinates = df[p.postal_code]
        p.save()
    else:
        print('could not find gps for %s, %s' % (p.name, p.postal_code))
