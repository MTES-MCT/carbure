from django.test import TestCase

from entity.factories.entity import EntityFactory
from h2.factories.h2_station import H2StationFactory
from h2.handlers import lookups
from traceability.factories import MaterialFactory
from transactions.models import Site


class H2ActionLookupsTest(TestCase):
    def test_materials_are_limited_to_hydrogen(self):
        hydrogen = MaterialFactory(code="H2-GASE", name="Hydrogène gazeux")
        MaterialFactory(code="BIO-WOOD", name="Bois")

        self.assertEqual(list(lookups.material(None)), [hydrogen])

    def test_sites_are_limited_to_entity_refueling_stations(self):
        entity = EntityFactory.create()
        station = H2StationFactory.create(created_by=entity)
        Site.objects.create(name="Dépôt Lyon", site_type=Site.EFS)

        self.assertEqual(list(lookups.site(entity).values_list("pk", flat=True)), [station.pk])
