import csv
import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()

from core.models import Biocarburant

filename = "%s/web/fixtures/csv/biocarburants.csv" % (os.environ["CARBURE_HOME"])

with open(filename) as csvfile:
    reader = csv.reader(csvfile, quotechar='"')
    for row in reader:
        code = row[0]
        if code == "code":
            # header
            continue
        name = row[1]
        pcikg = row[2]
        pcil = row[3]
        mv = row[4]
        is_alcool = row[5]
        is_graisse = row[6]
        is_displayed = row[7]
        compat_essence = row[8]
        compat_diesel = row[9]
        obj, created = Biocarburant.objects.update_or_create(
            code=code,
            defaults={
                "name": name,
                "description": "",
                "pci_kg": pcikg,
                "pci_litre": pcil,
                "masse_volumique": mv,
                "is_alcool": is_alcool,
                "is_graisse": is_graisse,
                "is_displayed": is_displayed,
                "compatible_essence": compat_essence,
                "compatible_diesel": compat_diesel,
            },
        )
