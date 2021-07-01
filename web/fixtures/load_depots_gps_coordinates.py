import sys, os
import django
import csv
import pandas as pd

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()

from core.models import Depot

filename = '%s/web/fixtures/csv/depots_gps_coordinates.csv' % (os.environ['CARBURE_HOME'])

df = pd.read_csv(filename, delimiter=';').set_index('zip')['gps'].to_dict()
print(df)


depots = Depot.objects.all()

for d in depots:
    if d.postal_code in df:
        print('FOUND gps for %s' % (d.name))
        print(df[d.postal_code])
        d.gps_coordinates = df[d.postal_code]
        d.save()
    else:
        print('could not find gps for %s, %s' % (d.name, d.postal_code))
