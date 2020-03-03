import sys, os
import django
import csv

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()

from core.models import TypeBiocarburant 

filename = '%s/web/fixtures/biocarburants.csv' % (os.environ['CARBURE_HOME'])

with open(filename) as csvfile:
    reader = csv.reader(csvfile, delimiter=',', quotechar='"')
    for row in reader:
        name = row[1]
        obj, created = TypeBiocarburant.objects.update_or_create(name=name, defaults={'description':''})

