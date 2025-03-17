import csv
import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()

from tiruert.models import FossilFuel, FossilFuelCategory  # noqa: E402

filename = "%s/web/fixtures/csv/fossil_fuels.csv" % (os.environ["CARBURE_HOME"])

with open(filename) as csvfile:
    reader = csv.reader(csvfile, quotechar='"')
    for row in reader:
        nomenclature = row[0]
        if nomenclature == "nomenclature":
            # header
            continue
        fuel_category = FossilFuelCategory.objects.get(pk=row[1])
        label = row[2]
        pci_litre = row[3]
        masse_volumique = row[4]
        obj, created = FossilFuel.objects.update_or_create(
            nomenclature=nomenclature,
            defaults={
                "fuel_category": fuel_category,
                "pci_litre": pci_litre,
                "masse_volumique": masse_volumique,
                "label": label,
            },
        )
