import csv
import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()

from core.models import MatierePremiere

filename = '%s/web/fixtures/csv/matierespremieres.csv' % (os.environ['CARBURE_HOME'])

with open(filename) as csvfile:
    reader = csv.reader(csvfile, quotechar='"')
    for row in reader:
        code = row[0]
        if code == 'code':
            # header
            continue

        name = row[1]
        compat_alcool = row[2]
        compat_graisse = row[3]
        is_double_compte = row[4]
        is_huile_vegetale = row[5]
        is_displayed = row[6]
        category = row[7]
        obj, created = MatierePremiere.objects.update_or_create(code=code, defaults={'name':name, 'description':'', 'compatible_alcool': compat_alcool, 'compatible_graisse': compat_graisse, 'is_double_compte': is_double_compte, 'is_huile_vegetale': is_huile_vegetale, 'is_displayed': is_displayed, 'category': category})

