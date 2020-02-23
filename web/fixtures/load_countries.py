import sys, os
import django
import csv

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()

from core.models import Pays

filename = '%s/web/fixtures/countries.csv' % (os.environ['CARBURE_HOME'])

with open(filename) as csvfile:
    reader = csv.reader(csvfile, delimiter=',', quotechar='"')
    for row in reader:
        code_pays = row[0]
        full_name = row[1]

        print(code_pays)
        print(full_name)
        obj, created = Pays.objects.update_or_create(code_pays=code_pays, defaults={'name':full_name})
        
        
