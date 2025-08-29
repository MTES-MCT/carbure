from django.test import TestCase
from django.urls import reverse

from biomethane.models.biomethane_digestate import BiomethaneDigestate
from biomethane.utils import get_declaration_period
from core.models import Entity
from core.tests_utils import assert_object_contains_data, setup_current_user


class BiomethaneDigestateTests(TestCase):
    def setUp(self):
        self.entity = Entity.objects.create(
            name="Test Entity",
            entity_type=Entity.BIOMETHANE_PRODUCER,
        )

        self.user = setup_current_user(
            self,
            "tester@carbure.local",
            "Tester",
            "gogogo",
            [(self.entity, "RW")],
        )

        self.digestate = BiomethaneDigestate.objects.create(
            producer=self.entity,
            year=get_declaration_period(),
        )

        self.digestate_url = reverse("biomethane-digestate")

    def test_retrieve_digestate_for_current_year(self):
        """Test that digestate data can be retrieved for the current year"""
        response = self.client.get(self.digestate_url, {"entity_id": self.entity.id})

        self.assertEqual(self.digestate.id, response.data["id"])
        self.assertEqual(self.digestate.year, response.data["year"])

    def test_create_digestate(self):
        """Test that a new digestate record can be created with valid data"""
        data = {
            "raw_digestate_tonnage_produced": 42,
            "raw_digestate_dry_matter_rate": 0.1,
            "solid_digestate_tonnage": 42,
        }

        self.client.put(
            self.digestate_url,
            data,
            content_type="application/json",
            query_params={"entity_id": self.entity.id},
        )

        digestate = BiomethaneDigestate.objects.get(producer=self.entity, year=2025)

        assert_object_contains_data(self, digestate, data)

    def test_update_digestate(self):
        """Test that an existing digestate record can be updated with new data"""
        data = {
            "raw_digestate_tonnage_produced": 42,
            "raw_digestate_dry_matter_rate": 0.1,
            "solid_digestate_tonnage": 42,
        }

        self.client.put(
            self.digestate_url,
            data,
            content_type="application/json",
            query_params={"entity_id": self.entity.id, "year": self.digestate.year},
        )

        digestate = BiomethaneDigestate.objects.get(producer=self.entity, year=self.digestate.year)

        assert_object_contains_data(self, digestate, data)
