from django.test import TestCase
from django.urls import reverse

from certificates.models import ProductionSiteCertificate
from core.models import (
    Entity,
)
from core.tests_utils import setup_current_user
from entity.factories.entity import EntityFactory
from producers.models import ProductionSiteInput, ProductionSiteOutput
from transactions.factories.certificate import EntityCertificateFactory
from transactions.factories.production_site import (
    ProductionSiteCertificateFactory,
    ProductionSiteInputFactory,
    ProductionSiteOutputFactory,
)
from transactions.factories.site import SiteFactory
from transactions.models import ProductionSite
from transactions.models.site import Site


class EntityProductionSiteTest(TestCase):
    fixtures = [
        "json/biofuels.json",
        "json/feedstock.json",
        "json/countries.json",
    ]

    @classmethod
    def setUpTestData(cls):
        cls.admin: Entity = EntityFactory.create(entity_type=Entity.ADMIN)
        cls.producer: Entity = EntityFactory.create(entity_type=Entity.PRODUCER)

        cls.production_site: ProductionSite = SiteFactory.create(
            site_type=Site.PRODUCTION_BIOLIQUID, created_by=cls.producer
        )

        cls.production_site_input = ProductionSiteInputFactory.create(production_site=cls.production_site)
        cls.production_site_output = ProductionSiteOutputFactory.create(production_site=cls.production_site)

        cls.production_site_certificate = ProductionSiteCertificateFactory.create(
            entity=cls.producer, production_site=cls.production_site
        )

    def setUp(self):
        self.user = setup_current_user(
            self,
            email="tester@carbure.local",
            name="Tester",
            password="gogogo",
            is_staff=True,
            entity_rights=[(self.producer, "RW"), (self.admin, "RO")],
        )

    # API CALLS SHORTHANDS

    def list_production_sites(self, entity_id, **kwargs):
        query_params = {"entity_id": entity_id, **kwargs}
        url = reverse("api-entity-production-sites-list")
        response = self.client.get(url, query_params=query_params)
        return response.json()

    def create_production_site(self, entity_id, data):
        query_params = {"entity_id": entity_id}
        url = reverse("api-entity-production-sites-list")
        response = self.client.post(url, data, query_params=query_params)
        return response.json()

    def update_production_site(self, entity_id, production_site_id, data):
        kwargs = {"id": production_site_id}
        query_params = {"entity_id": entity_id}
        url = reverse("api-entity-production-sites-update-item", kwargs=kwargs)
        response = self.client.post(url, data, query_params=query_params)
        return response.json()

    def delete_production_site(self, entity_id, production_site_id):
        kwargs = {"id": production_site_id}
        query_params = {"entity_id": entity_id}
        url = reverse("api-entity-production-sites-delete", kwargs=kwargs)
        response = self.client.post(url, query_params=query_params)
        return response.json()

    def set_production_site_feedstocks(self, entity_id, production_site_id, data):
        kwargs = {"id": production_site_id}
        query_params = {"entity_id": entity_id}
        url = reverse("api-entity-production-sites-set-feedstocks", kwargs=kwargs)
        response = self.client.post(url, data, query_params=query_params)
        return response.json()

    def set_production_site_biofuels(self, entity_id, production_site_id, data):
        kwargs = {"id": production_site_id}
        query_params = {"entity_id": entity_id}
        url = reverse("api-entity-production-sites-set-biofuels", kwargs=kwargs)
        response = self.client.post(url, data, query_params=query_params)
        return response.json()

    def set_production_site_certificates(self, entity_id, production_site_id, data):
        kwargs = {"id": production_site_id}
        url = reverse("api-entity-production-sites-set-certificates", kwargs=kwargs)
        query_params = {"entity_id": entity_id}
        response = self.client.post(url, data, query_params=query_params)
        return response.json()

    # PRODUCER TESTS

    def test_list_production_sites(self):
        data = self.list_production_sites(entity_id=self.producer.pk)

        psite = self.production_site
        psite_input = self.production_site_input.matiere_premiere
        psite_output = self.production_site_output.biocarburant

        self.assertEqual(len(data), 1)

        self.assertEqual(data[0]["id"], psite.pk)
        self.assertEqual(data[0]["name"], psite.name)

        self.assertEqual(len(data[0]["inputs"]), 1)
        self.assertEqual(data[0]["inputs"][0]["code"], psite_input.code)

        self.assertEqual(len(data[0]["outputs"]), 1)
        self.assertEqual(data[0]["outputs"][0]["code"], psite_output.code)

        self.assertEqual(len(data[0]["certificates"]), 1)
        self.assertEqual(
            data[0]["certificates"][0]["certificate_id"],
            self.production_site_certificate.certificate.certificate.certificate_id,
        )

    def test_create_production_site(self):
        form_data = {
            "entity_id": self.producer.pk,
            "country_code": "FR",
            "name": "Site prod 1",
            "date_mise_en_service": "2020-12-01",
            "ges_option": "Actual",
            "eligible_dc": "true",
            "dc_reference": "DC-FR-12-493",
            "site_siret": "FR0001",
            "address": "1 rue de la Paix",
            "city": "Seynod",
            "postal_code": "74600",
            "manager_name": "",
            "manager_phone": "",
            "manager_email": "",
        }

        data = self.create_production_site(
            entity_id=self.producer.pk,
            data=form_data,
        )

        psite = ProductionSite.objects.select_related("country").get(pk=data["id"])

        self.assertEqual(psite.created_by_id, self.producer.pk)
        self.assertEqual(psite.name, form_data["name"])
        self.assertEqual(psite.country.code_pays, form_data["country_code"])
        self.assertEqual(psite.address, form_data["address"])

    def test_create_production_site_with_missing_data(self):
        data = self.create_production_site(entity_id=self.producer.pk, data={})

        self.assertEqual(data["name"], ["Ce champ est obligatoire."])
        self.assertEqual(data["country_code"], ["Ce champ est obligatoire."])
        self.assertEqual(data["site_siret"], ["Ce champ est obligatoire."])

    def test_update_production_site(self):
        psite: Site = self.production_site
        initial_name = psite.name
        initial_country = psite.country.code_pays

        self.update_production_site(
            entity_id=self.producer.pk,
            production_site_id=psite.id,
            data={"name": "A new name", "country_code": "ES"},
        )

        psite.refresh_from_db()

        self.assertNotEqual(initial_name, "A new name")
        self.assertEqual(psite.name, "A new name")
        self.assertNotEqual(psite.country.code_pays, initial_country)
        self.assertEqual(psite.country.code_pays, "ES")

    def test_delete_production_site(self):
        psite = self.production_site

        self.delete_production_site(
            entity_id=self.producer.pk,
            production_site_id=psite.pk,
        )

        self.assertEqual(ProductionSite.objects.filter(pk=psite.pk).count(), 0)
        self.assertEqual(ProductionSiteInput.objects.filter(production_site=psite).count(), 0)
        self.assertEqual(ProductionSiteOutput.objects.filter(production_site=psite).count(), 0)
        self.assertEqual(ProductionSiteCertificate.objects.filter(production_site=psite).count(), 0)

    def test_set_production_site_feedstocks(self):
        self.set_production_site_feedstocks(
            entity_id=self.producer.pk,
            production_site_id=self.production_site.pk,
            data={"matiere_premiere_codes": ["COLZA", "BLE"]},
        )

        psite_inputs = ProductionSiteInput.objects.filter(production_site=self.production_site)
        feedstocks = psite_inputs.values_list("matiere_premiere__code", flat=True)

        self.assertEqual(feedstocks.count(), 2)
        self.assertIn("COLZA", feedstocks)
        self.assertIn("BLE", feedstocks)

    def test_set_production_site_biofuels(self):
        self.set_production_site_biofuels(
            entity_id=self.producer.pk,
            production_site_id=self.production_site.pk,
            data={"biocarburant_codes": ["ETH", "ETBE"]},
        )

        psite_outputs = ProductionSiteOutput.objects.filter(production_site=self.production_site)
        biofuels = psite_outputs.values_list("biocarburant__code", flat=True)

        self.assertEqual(biofuels.count(), 2)
        self.assertIn("ETH", biofuels)
        self.assertIn("ETBE", biofuels)

    def test_set_production_site_certificates(self):
        entity_cert = EntityCertificateFactory.create(entity=self.producer)

        self.set_production_site_certificates(
            entity_id=self.producer.pk,
            production_site_id=self.production_site.pk,
            data={"certificate_ids": [entity_cert.certificate.certificate_id]},
        )

        psite_certs = ProductionSiteCertificate.objects.filter(production_site=self.production_site)
        certificates = psite_certs.values_list("certificate__certificate__certificate_id", flat=True)

        self.assertEqual(certificates.count(), 1)
        self.assertIn(entity_cert.certificate.certificate_id, certificates)

    # ADMIN TESTS

    def test_list_production_sites_as_admin(self):
        data = self.list_production_sites(entity_id=self.admin.pk, company_id=self.producer.pk)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["name"], self.production_site.name)
