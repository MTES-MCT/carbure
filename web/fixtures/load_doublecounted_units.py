import csv
import os

import dateutil
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()

from certificates.models import DoubleCountingRegistration

filename = "%s/web/fixtures/csv/unites_double_compte.csv" % (os.environ["CARBURE_HOME"])

with open(filename) as csvfile:
    reader = csv.reader(csvfile, quotechar='"')
    for row in reader:
        name = row[0]
        if name == "Name":
            continue
        address = row[1]
        cert_id = row[2]
        vfrom = dateutil.parser.parse(row[3], dayfirst=True)
        vuntil = dateutil.parser.parse(row[4], dayfirst=True)
        scope = row[5]
        print(vuntil, vfrom)

        d = {}
        d["certificate_holder"] = name
        d["registered_address"] = address
        d["valid_from"] = vfrom
        d["valid_until"] = vuntil
        DoubleCountingRegistration.objects.update_or_create(certificate_id=cert_id, defaults=d)
