import sys, os
import django
import csv

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()

from core.models import MatierePremiere

filename = '%s/web/fixtures/csv/matierespremieres.csv' % (os.environ['CARBURE_HOME'])

with open(filename) as csvfile:
    reader = csv.reader(csvfile, delimiter=';', quotechar='"')
    for row in reader:
        code = row[0]
        name = row[1]
        obj, created = MatierePremiere.objects.update_or_create(code=code, defaults={'name':name, 'description':''})
