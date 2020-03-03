import sys, os
import django
import csv

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()

from core.models import MatierePremiere

filename = '%s/web/fixtures/matierespremieres.csv' % (os.environ['CARBURE_HOME'])

with open(filename) as csvfile:
    reader = csv.reader(csvfile, delimiter=',', quotechar='"')
    for row in reader:
        name = row[0]
        obj, created = MatierePremiere.objects.update_or_create(name=name, defaults={'description':''})

