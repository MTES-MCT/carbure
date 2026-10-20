from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from biomethane.factories import BiomethaneContractFactory, BiomethaneProductionUnitFactory
from biomethane.models import BiomethaneAnnualDeclaration
from core.models import Entity
from core.tests_utils import setup_current_user_with_jwt
from entity.factories import EntityFactory


class BiomethaneProviderDeclarationViewSetTest(TestCase):
    fixtures = ["json/countries.json"]

    def setUp(self):
        self.client = APIClient()
        self.url = reverse("biomethane-provider-declarations-list")
        self.year = 2024

        self.provider = EntityFactory.create(name="Provider A", entity_type=Entity.BIOMETHANE_PROVIDER)
        self.other_provider = EntityFactory.create(name="Provider B", entity_type=Entity.BIOMETHANE_PROVIDER)
        self.user = setup_current_user_with_jwt(
            self, "provider@carbure.local", "Provider", "gogogo", [(self.provider, "RO")]
        )

    def _create_producer(self, name, buyer, status_=BiomethaneAnnualDeclaration.DECLARED, year=None):
        producer = EntityFactory.create(name=name, entity_type=Entity.BIOMETHANE_PRODUCER)
        BiomethaneContractFactory.create(producer=producer, buyer=buyer)
        BiomethaneAnnualDeclaration.objects.create(producer=producer, year=year or self.year, status=status_)
        return producer

    def _get(self, **params):
        return self.client.get(self.url, {"entity_id": self.provider.id, **params})

    def test_returns_only_validated_declarations_of_own_contracts(self):
        """Only validated declarations of producers under contract with the provider are returned."""
        own = self._create_producer("Own", self.provider)
        self._create_producer("In progress", self.provider, status_=BiomethaneAnnualDeclaration.IN_PROGRESS)
        self._create_producer("Other", self.other_provider)

        response = self._get()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual([item["producer"]["id"] for item in response.data["results"]], [own.id])

    def test_year_filter(self):
        """The year filter restricts results to the requested year."""
        self._create_producer("Y2024", self.provider, year=2024)
        producer_2023 = self._create_producer("Y2023", self.provider, year=2023)

        response = self._get(year=2023)

        self.assertEqual([item["producer"]["id"] for item in response.data["results"]], [producer_2023.id])

    def test_response_exposes_producer_and_production_unit(self):
        """Each item exposes the producer and the location of its production unit."""
        producer = self._create_producer("Producer", self.provider)
        BiomethaneProductionUnitFactory.create(
            producer=producer, insee_code="75056", address="1 rue de Paris", postal_code="75001", city="Paris"
        )

        item = self._get().data["results"][0]

        self.assertEqual(set(item.keys()), {"producer", "production_unit"})
        self.assertEqual(item["producer"]["id"], producer.id)
        self.assertEqual(
            item["production_unit"],
            {"insee_code": "75056", "address": "1 rue de Paris", "postal_code": "75001", "city": "Paris"},
        )

    def test_production_unit_is_null_without_production_unit(self):
        """Without a production unit, production_unit is null."""
        self._create_producer("No unit", self.provider)

        item = self._get().data["results"][0]

        self.assertIsNone(item["production_unit"])

    def test_forbidden_for_another_provider_entity(self):
        """A provider cannot read through another provider entity it has no rights on."""
        response = self.client.get(self.url, {"entity_id": self.other_provider.id})

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_forbidden_for_non_provider_entity(self):
        """An entity that is not a biomethane provider cannot access the API."""
        producer = self._create_producer("Producer", self.provider)
        setup_current_user_with_jwt(self, "producer@carbure.local", "Producer", "gogogo", [(producer, "ADMIN")])

        response = self.client.get(self.url, {"entity_id": producer.id})

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_forbidden_without_entity_id(self):
        """Without entity_id, access is denied."""
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_forbidden_without_api_key(self):
        """Without an API key, access is denied."""
        self.client.credentials()
        self.client.force_authenticate(user=self.user)

        response = self._get()

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
