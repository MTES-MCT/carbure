import csv
import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()

from tiruert.models import FossilFuelCategory  # noqa: E402

filename = "%s/web/fixtures/csv/fossil_fuel_categories.csv" % (os.environ["CARBURE_HOME"])

with open(filename) as csvfile:
    reader = csv.reader(csvfile, quotechar='"')

    for row in reader:
        name = row[0]
        if name == "name":
            # header
            continue
        pci_litre = row[1]
        obj, created = FossilFuelCategory.objects.update_or_create(
            name=name,
            defaults={
                "pci_litre": pci_litre,
            },
        )
