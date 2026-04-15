import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()

from load_biomethane_utils import load_external_admin_entities  # noqa: E402

from core.models import ExternalAdminRights  # noqa: E402

filename = "%s/web/fixtures/csv/biomethane_DREAL.csv" % (os.environ["CARBURE_HOME"])
load_external_admin_entities(filename, ExternalAdminRights.DREAL, "DREAL")
