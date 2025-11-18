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
    for row in reader:
        name = row[0]
        if name == "name":
            # header
            continue
        siren = row[1]
        entity_type = Entity.BIOMETHANE_PROVIDER
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
