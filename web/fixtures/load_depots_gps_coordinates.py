import os

import django
import pandas as pd

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()

from core.models import Depot

filename = '%s/web/fixtures/csv/depots_gps_coordinates.csv' % (os.environ['CARBURE_HOME'])

df = pd.read_csv(filename, delimiter=';').set_index('zip')['gps'].to_dict()
print(df)


depots = Depot.objects.all()

for d in depots:
    try:
        code = int(d.postal_code)
    except:
        print('missing zip code for %s' % d.name)
        continue
    if code in df:
        print('FOUND gps for %s' % (d.name))
        print(df[code])
        d.gps_coordinates = df[code]
        d.save()
    else:
        print('could not find gps for %s, %s' % (d.name, d.postal_code))
