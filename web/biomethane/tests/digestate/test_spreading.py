from django.test import TestCase
from django.urls import reverse

from biomethane.models.biomethane_digestate import BiomethaneDigestate
from biomethane.models.biomethane_digestate_spreading import BiomethaneDigestateSpreading
from core.models import Entity
from core.tests_utils import assert_object_contains_data, setup_current_user


class BiomethaneDigestateSpreadingTests(TestCase):
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
            year=2024,
        )

        self.digestate_spreading_url = reverse("biomethane-digestate-spreading-list")

    def test_create_digestate_spreading(self):
        data = {
            "spreading_department": "75",
            "spread_quantity": 100,
            "spread_parcels_area": 100,
        }

        response = self.client.post(
            self.digestate_spreading_url,
            data,
            content_type="application/json",
            query_params={"entity_id": self.entity.id, "year": self.digestate.year},
        )

        self.assertEqual(response.status_code, 201)

        spreading = BiomethaneDigestateSpreading.objects.filter(digestate=self.digestate).first()

        assert_object_contains_data(self, spreading, data)

    def test_create_digestate_without_rw_rights(self):
        setup_current_user(
            self,
            "tester2@carbure.local",
            "Tester2",
            "gogogo",
        )

        response = self.client.post(
            self.digestate_spreading_url,
            {},
            content_type="application/json",
            query_params={"entity_id": self.entity.id, "year": self.digestate.year},
        )

        self.assertEqual(response.status_code, 403)
