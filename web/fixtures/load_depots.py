import sys, os
import django
import csv

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()

from core.models import Depot

filename = '%s/web/fixtures/csv/depots.csv' % (os.environ['CARBURE_HOME'])

with open(filename) as csvfile:
    reader = csv.reader(csvfile, delimiter=';', quotechar='"')
    for row in reader:
        name = row[0]
        depot_id = row[1]
        city = row[2]
        if city == "Ville":
            continue
        obj, created = Depot.objects.update_or_create(depot_id=depot_id, defaults={'name': name, 'city':city})
