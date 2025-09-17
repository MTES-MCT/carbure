from django.test import TestCase

from certificates.models import ProductionSiteCertificate
from core.models import Biocarburant, MatierePremiere, Pays
from entity.factories.entity import EntityFactory
from entity.serializers.production_sites import EntityProductionSiteSerializer, EntityProductionSiteWriteSerializer
from producers.models import ProductionSiteInput, ProductionSiteOutput
from transactions.factories.certificate import EntityCertificateFactory, GenericCertificateFactory
from transactions.factories.site import SiteFactory

PRODUCTION_SITE_DATA = {
    "country_code": "FR",
    "name": "Test Production Site",
    "date_mise_en_service": "2020-12-01",
    "ges_option": "Actual",
    "eligible_dc": "true",
    "dc_reference": "DC-FR-12-493",
    "site_siret": "FR0001",
    "address": "1 rue de la Paix",
    "city": "Seynod",
    "postal_code": "74600",
    "manager_name": "Bob",
    "manager_phone": "0123456789",
    "manager_email": "bob@test.com",
    "inputs": ["BLE"],
    "outputs": ["ETH"],
    "certificates": ["FR_123"],
}


class ProductionSiteSerializerTest(TestCase):
    fixtures = [
        "json/biofuels.json",
        "json/feedstock.json",
        "json/countries.json",
    ]

    @classmethod
    def setUpTestData(cls):
        cls.country = Pays.objects.get(code_pays="FR")
        cls.feedstock = MatierePremiere.objects.get(code="BLE")
        cls.biofuel = Biocarburant.objects.get(code="ETH")

        cls.producer = EntityFactory.create(name="Producer")
        cls.cert = GenericCertificateFactory.create(certificate_id="FR_123")
        cls.entity_cert = EntityCertificateFactory.create(entity=cls.producer, certificate=cls.cert)

    def test_serialize_production_site(self):
        production_site = SiteFactory.create(name="Test Production Site", created_by=self.producer)
        ProductionSiteInput.objects.create(production_site=production_site, matiere_premiere=self.feedstock)
        ProductionSiteOutput.objects.create(production_site=production_site, biocarburant=self.biofuel)
        ProductionSiteCertificate.objects.create(
            production_site=production_site, certificate=self.entity_cert, entity=self.producer
        )

        serializer = EntityProductionSiteSerializer(production_site)

        self.assertEqual(serializer.data["name"], "Test Production Site")
        self.assertEqual(len(serializer.data["inputs"]), 1)
        self.assertEqual(serializer.data["inputs"][0]["code"], "BLE")
        self.assertEqual(len(serializer.data["outputs"]), 1)
        self.assertEqual(serializer.data["outputs"][0]["code"], "ETH")
        self.assertEqual(len(serializer.data["certificates"]), 1)
        self.assertEqual(serializer.data["certificates"][0]["certificate_id"], "FR_123")

    def test_production_site_write_serializer_with_missing_fields(self):
        serializer = EntityProductionSiteWriteSerializer(data={})

        self.assertEqual(serializer.is_valid(), False)

        self.assertEqual(serializer.errors["name"][0].code, "required")
        self.assertEqual(serializer.errors["inputs"][0].code, "required")
        self.assertEqual(serializer.errors["outputs"][0].code, "required")
        self.assertEqual(serializer.errors["certificates"][0].code, "required")

    def test_create_new_production_site_from_serializer(self):
        serializer = EntityProductionSiteWriteSerializer(data=PRODUCTION_SITE_DATA, context={"entity_id": self.producer.pk})

        self.assertEqual(serializer.is_valid(), True)

        self.assertEqual(serializer.validated_data["country"], self.country)
        self.assertEqual(serializer.validated_data["inputs"], [self.feedstock])
        self.assertEqual(serializer.validated_data["outputs"], [self.biofuel])
        self.assertEqual(serializer.validated_data["certificates"], [self.cert])

        production_site = serializer.save()

        inputs = production_site.productionsiteinput_set
        outputs = production_site.productionsiteoutput_set
        certificates = production_site.productionsitecertificate_set

        self.assertEqual(production_site.name, "Test Production Site")
        self.assertEqual(inputs.count(), 1)
        self.assertEqual(inputs.first().matiere_premiere.code, "BLE")
        self.assertEqual(outputs.count(), 1)
        self.assertEqual(outputs.first().biocarburant.code, "ETH")
        self.assertEqual(certificates.count(), 1)
        self.assertEqual(certificates.first().certificate.certificate.certificate_id, "FR_123")

    def test_update_existing_production_site_from_serializer(self):
        production_site = SiteFactory.create(name="Old Production Site", created_by=self.producer)

        serializer = EntityProductionSiteWriteSerializer(
            production_site,
            data=PRODUCTION_SITE_DATA,
            context={"entity_id": self.producer.pk},
        )

        self.assertEqual(serializer.is_valid(), True)

        production_site = serializer.save()

        inputs = production_site.productionsiteinput_set
        outputs = production_site.productionsiteoutput_set
        certificates = production_site.productionsitecertificate_set

        self.assertEqual(production_site.name, "Test Production Site")
        self.assertEqual(inputs.count(), 1)
        self.assertEqual(inputs.first().matiere_premiere.code, "BLE")
        self.assertEqual(outputs.count(), 1)
        self.assertEqual(outputs.first().biocarburant.code, "ETH")
        self.assertEqual(certificates.count(), 1)
        self.assertEqual(certificates.first().certificate.certificate.certificate_id, "FR_123")
