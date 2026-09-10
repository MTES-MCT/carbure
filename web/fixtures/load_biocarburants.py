import csv
import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()

from core.models import Biocarburant  # noqa: E402

filename = "%s/web/fixtures/csv/biocarburants.csv" % (os.environ["CARBURE_HOME"])

with open(filename, newline="", encoding="utf-8-sig") as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        code = row["code"]
        name = row["name"]
        name_en = row["name_en"]
        is_displayed = row["is_displayed"]
        is_alcool = row["is_alcool"]
        is_graisse = row["is_graisse"]
        pci_kg = row["pci_kg"]
        pci_litre = row["pci_litre"]
        masse_volumique = row["masse_volumique"]
        renewable_energy_share = row["renewable_energy_share"]
        compatible_essence = row["compatible_essence"]
        compatible_diesel = row["compatible_diesel"]
        compatible_gpl = row["compatible_gpl"]
        description = row["description"]

        obj, created = Biocarburant.objects.update_or_create(
            code=code,
            defaults={
                "name": name,
                "name_en": name_en,
                "is_displayed": is_displayed,
                "is_alcool": is_alcool,
                "is_graisse": is_graisse,
                "pci_kg": pci_kg,
                "pci_litre": pci_litre,
                "masse_volumique": masse_volumique,
                "renewable_energy_share": renewable_energy_share,
                "compatible_essence": compatible_essence,
                "compatible_diesel": compatible_diesel,
                "compatible_gpl": compatible_gpl,
                "description": description,
            },
        )
