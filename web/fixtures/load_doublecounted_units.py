import sys, os
import django
import csv

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()

from certificates.models import *

filename = '%s/web/fixtures/csv/unites_double_compte.csv' % (os.environ['CARBURE_HOME'])

with open(filename) as csvfile:
    reader = csv.reader(csvfile, quotechar='"')
    for row in reader:
        name = row[0]
        if name == 'name':
            continue
        address = row[1]
        cert_id = row[2]
        vfrom = row[3]
        vuntil = row[4]
        scope = row[5]


        d = {}
        d['certificate_holder'] = name
        d['registered_address'] = address
        d['valid_from'] = vfrom
        d['valid_until'] = vuntil
        DoubleCountingRegistration.objects.update_or_create(certificate_id=cert_id, defaults=d)
