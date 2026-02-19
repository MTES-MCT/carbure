from django.test import TestCase

from core.models import Entity, Pays
from core.serializers import UserEntitySerializer
from entity.factories.entity import EntityFactory
from entity.serializers.depot import DepotProductionSiteSerializer, EntityDepotSerializer, EntitySiteSerializer
from transactions.factories.depot import DepotFactory
from transactions.factories.production_site import ProductionSiteFactory
from transactions.models import Depot, EntitySite, Site


class EntitySiteSerializerTest(TestCase):
    fixtures = [
        "json/countries.json",
    ]

    @classmethod
    def setUpTestData(cls):
        cls.entity = EntityFactory.create(entity_type=Entity.OPERATOR)
        cls.blender_entity = EntityFactory.create(entity_type=Entity.OPERATOR)
        cls.country = Pays.objects.get(code_pays="FR")

    def test_serialize_entity_site_with_depot(self):
        """Test that the serializer returns the correct data for an EntitySite with a depot"""
        depot = DepotFactory.create(
            name="Dépôt de test",
            customs_id="FR123456",
            city="Paris",
            country=self.country,
            site_type=Depot.BIOFUELDEPOT,
        )
        entity_site = EntitySite.objects.create(
            entity=self.entity,
            site=depot,
            ownership_type=EntitySite.OWN,
            blending_is_outsourced=True,
            blender=self.blender_entity,
        )

        serializer = EntitySiteSerializer(entity_site)
        data = serializer.data

        self.assertEqual(
            data,
            {
                "ownership_type": EntitySite.OWN,
                "blending_is_outsourced": True,
                "blender": UserEntitySerializer(self.blender_entity).data,
                "depot": EntityDepotSerializer(depot).data,
                "site": None,
            },
        )

    def test_serialize_entity_site_with_production_site(self):
        """Test that the serializer returns the correct data for an EntitySite with a production site"""
        production_site = ProductionSiteFactory.create(
            name="Site de production de test",
            site_type=Site.PRODUCTION_BIOLIQUID,
            country=self.country,
            city="Lyon",
        )
        entity_site = EntitySite.objects.create(
            entity=self.entity,
            site=production_site,
            ownership_type=EntitySite.THIRD_PARTY,
            blending_is_outsourced=False,
            blender=None,
        )

        serializer = EntitySiteSerializer(entity_site)
        data = serializer.data

        self.assertEqual(
            data,
            {
                "ownership_type": EntitySite.THIRD_PARTY,
                "blending_is_outsourced": False,
                "blender": None,
                "site": DepotProductionSiteSerializer(production_site).data,
                "depot": None,
            },
        )

    def test_serialize_depot_directly(self):
        """Test that the serializer works when passing a Depot directly"""
        depot = DepotFactory.create(
            name="Dépôt direct",
            customs_id="FR789012",
            city="Marseille",
            country=self.country,
            site_type=Depot.BIOFUELDEPOT,
        )

        serializer = EntitySiteSerializer(depot)
        data = serializer.data

        self.assertEqual(
            data,
            {
                "ownership_type": None,
                "blending_is_outsourced": False,
                "blender": None,
                "depot": EntityDepotSerializer(depot).data,
                "site": None,
            },
        )
