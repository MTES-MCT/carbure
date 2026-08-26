from django.test import TestCase

from h2.handlers import H2ActionHandler
from traceability.factories import MaterialFactory
from transactions.models import Site


class H2ActionLookupsTest(TestCase):
    def test_looks_up_hydrogen_materials(self):
        hydrogen = MaterialFactory(code="H2-GASE", name="Hydrogène gazeux")
        MaterialFactory(code="BIO-WOOD", name="Bois")

        materials = list(H2ActionHandler().lookup("material"))

        self.assertEqual(materials, [hydrogen])

    def test_looks_up_refueling_stations(self):
        station = Site.objects.create(name="Station Paris", site_type=Site.H2_REFUELING_STATION)
        Site.objects.create(name="Dépôt Lyon", site_type=Site.EFS)

        sites = H2ActionHandler().lookup("site")

        self.assertEqual(list(sites.values_list("pk", flat=True)), [station.pk])
