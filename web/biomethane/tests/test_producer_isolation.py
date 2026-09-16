from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from biomethane.factories import (
    BiomethaneContractFactory,
    BiomethaneDigestateFactory,
    BiomethaneDigestateSpreadingFactory,
    BiomethaneSupplyInputFactory,
    BiomethaneSupplyPlanFactory,
)
from biomethane.factories.contract import BiomethaneEntityConfigAmendmentFactory
from biomethane.models import (
    BiomethaneContractAmendment,
    BiomethaneDigestateSpreading,
    BiomethaneDigestateStorage,
    BiomethaneSupplyInput,
)
from biomethane.services.annual_declaration import BiomethaneAnnualDeclarationService
from core.models import Entity, MatierePremiere
from core.tests_utils import setup_current_user


class BiomethaneProducerObjectIsolationTests(TestCase):
    """Producer A, authenticated with its own entity_id, must not reach producer B's objects by pk."""

    fixtures = ["json/countries.json"]

    def setUp(self):
        self.producer_a = Entity.objects.create(name="Producer A", entity_type=Entity.BIOMETHANE_PRODUCER)
        self.producer_b = Entity.objects.create(name="Producer B", entity_type=Entity.BIOMETHANE_PRODUCER)
        self.buyer = Entity.objects.create(name="Buyer", entity_type=Entity.OPERATOR)

        setup_current_user(
            self,
            "producer-a@carbure.local",
            "Producer A",
            "gogogo",
            [(self.producer_a, "RW")],
        )

        self.params_a = {"entity_id": self.producer_a.id}
        year = BiomethaneAnnualDeclarationService.get_current_declaration_year()

        self.storage_b = BiomethaneDigestateStorage.objects.create(
            producer=self.producer_b,
            type="TANK",
            capacity=3000.0,
            has_cover=False,
            has_biogas_recovery=False,
        )
        self.storage_url = reverse("biomethane-digestate-storage-detail", kwargs={"pk": self.storage_b.pk})

        contract_b = BiomethaneContractFactory.create(
            producer=self.producer_b,
            buyer=self.buyer,
            tariff_reference="2021",
            pap_contracted=50.0,
        )
        self.amendment_b = BiomethaneEntityConfigAmendmentFactory.create(
            contract=contract_b,
            amendment_object=[BiomethaneContractAmendment.CMAX_PAP_UPDATE],
        )
        self.amendment_url = reverse("biomethane-contract-amendment-detail", kwargs={"pk": self.amendment_b.pk})

        digestate_b = BiomethaneDigestateFactory.create(producer=self.producer_b, year=year)
        self.spreading_b = BiomethaneDigestateSpreadingFactory.create(
            digestate=digestate_b,
            spreading_department="75",
            spread_quantity=100.0,
            spread_parcels_area=50.0,
        )
        self.spreading_url = reverse("biomethane-digestate-spreading-detail", kwargs={"pk": self.spreading_b.pk})

        plan_b = BiomethaneSupplyPlanFactory.create(producer=self.producer_b, year=year)
        feedstock = MatierePremiere.objects.create(
            name="Maïs isolation",
            name_en="Corn isolation",
            code="MAIS_ISOLATION",
            is_methanogenic=True,
        )
        self.input_b = BiomethaneSupplyInputFactory.create(
            supply_plan=plan_b,
            feedstock=feedstock,
            material_unit=BiomethaneSupplyInput.WET,
            volume=500.0,
        )
        self.input_url = reverse("biomethane-supply-input-detail", args=[self.input_b.pk])

    def assert_access_denied(self, response):
        self.assertIn(
            response.status_code,
            (status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND),
            f"Expected 403 or 404, got {response.status_code}: {getattr(response, 'data', None)}",
        )

    def test_cannot_read_update_or_delete_another_producer_storage(self):
        self.assert_access_denied(self.client.get(self.storage_url, self.params_a))

        response = self.client.put(
            self.storage_url,
            {"type": "LAGOON", "capacity": 9999.0, "has_cover": True, "has_biogas_recovery": True},
            content_type="application/json",
            query_params=self.params_a,
        )
        self.assert_access_denied(response)
        self.storage_b.refresh_from_db()
        self.assertEqual(self.storage_b.capacity, 3000.0)

        self.assert_access_denied(self.client.delete(self.storage_url, query_params=self.params_a))
        self.assertTrue(BiomethaneDigestateStorage.objects.filter(pk=self.storage_b.pk).exists())

    def test_cannot_read_another_producer_amendment(self):
        self.assert_access_denied(self.client.get(self.amendment_url, self.params_a))

    def test_cannot_delete_another_producer_spreading(self):
        self.assert_access_denied(self.client.delete(self.spreading_url, query_params=self.params_a))
        self.assertTrue(BiomethaneDigestateSpreading.objects.filter(pk=self.spreading_b.pk).exists())

    def test_cannot_read_update_or_delete_another_producer_supply_input(self):
        self.assert_access_denied(self.client.get(self.input_url, self.params_a))

        response = self.client.patch(
            self.input_url,
            {"volume": 1.0},
            content_type="application/json",
            query_params=self.params_a,
        )
        self.assert_access_denied(response)
        self.input_b.refresh_from_db()
        self.assertEqual(self.input_b.volume, 500.0)

        self.assert_access_denied(self.client.delete(self.input_url, query_params=self.params_a))
        self.assertTrue(BiomethaneSupplyInput.objects.filter(pk=self.input_b.pk).exists())
