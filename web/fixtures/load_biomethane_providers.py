import csv
import os
from unicodedata import name

import django
from django.db import IntegrityError

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()

from core.models import Entity  # noqa: E402

filename = "%s/web/fixtures/csv/biomethane_providers.csv" % (os.environ["CARBURE_HOME"])

with open(filename) as csvfile:
    reader = csv.reader(csvfile, quotechar='"')
    entity_type = Entity.BIOMETHANE_PROVIDER

    for row in reader:
        name = row[0]
        if name == "name":
            # header
            continue
        siren = row[1]
        try:
            Entity.objects.get_or_create(
                registration_id=siren,
                entity_type=entity_type,
                name=name,
            )
        except IntegrityError:
            try:
                Entity.objects.create(
                    registration_id=siren,
                    entity_type=entity_type,
                    name=f"{name} (fournisseur gaz)",
                )
            except Exception:
                pass

    # Wrong sirens correction
    siren_corrections = {
        "947688099": "813273554",
        "814450151": "891588154",
        "915720015": "984306357",
        "491911400": "38 76 56 04 (CVR)",
        "824763536": "422716878",
        "530609668": "833755598",
        "314119504": "844431387",
        "428766976": "622037083",
        "493467591": "521913798",
        "442395448": "434582540",
    }

    for old_siren, new_siren in siren_corrections.items():
        Entity.objects.filter(registration_id=old_siren, entity_type=entity_type).update(registration_id=new_siren)
