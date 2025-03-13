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
        label = row[0]
        if label == "label":
            # header
            continue
        fuel_category = FossilFuelCategory.objects.get(pk=row[1])
        pci_litre = row[2]
        masse_volumique = row[3]
        nomenclatures = [int(x) for x in row[4].split(",")]
        obj, created = FossilFuel.objects.update_or_create(
            label=label,
            defaults={
                "fuel_category": fuel_category,
                "pci_litre": pci_litre,
                "masse_volumique": masse_volumique,
                "nomenclatures": nomenclatures,
            },
        )
