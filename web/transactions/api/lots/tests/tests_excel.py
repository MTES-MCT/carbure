import os

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from core.models import CarbureLot, Entity, Pays
from core.tests_utils import setup_current_user
from transactions.models.entity_site import EntitySite
from transactions.models.site import Site


class LotsExcelImportTest(TestCase):
    fixtures = [
        "json/biofuels.json",
        "json/feedstock.json",
        "json/countries.json",
        "json/depots.json",
        "json/entities.json",
        "json/productionsites.json",
        "json/entities_sites.json",
    ]

    def setupProducer(self):
        self.producer = Entity.objects.create(
            is_enabled=True,
            name="Producer",
            entity_type=Entity.PRODUCER,
            default_certificate="PRODUCER_CERTIFICATE",
        )
        self.producer_production_site = Site.objects.create(
            site_type=Site.PRODUCTION_BIOLIQUID,
            is_enabled=True,
            name="Producer Production Site",
            country=self.FR,
            created_by=self.producer,
        )
        EntitySite.objects.create(entity=self.producer, site=self.producer_production_site)

    def setupProducerTrader(self):
        self.producer_trader = Entity.objects.create(
            is_enabled=True,
            name="Producer Trader",
            entity_type=Entity.PRODUCER,
            has_trading=True,
            default_certificate="PRODUCER_TRADER_CERTIFICATE",
        )
        self.producer_trader_production_site = Site.objects.create(
            site_type=Site.PRODUCTION_BIOLIQUID,
            is_enabled=True,
            name="Producer Trader Production Site",
            country=self.FR,
            created_by=self.producer_trader,
        )
        EntitySite.objects.create(entity=self.producer, site=self.producer_production_site)

    def setupTrader(self):
        self.trader = Entity.objects.create(
            is_enabled=True,
            name="Trader",
            entity_type=Entity.TRADER,
            has_trading=True,
            default_certificate="TRADER_CERTIFICATE",
        )
        self.trader_depot = Site.objects.create(
            site_type=Site.EFPE,
            is_enabled=True,
            name="Trader Depot",
            customs_id="AAA",
            country=self.FR,
        )
        EntitySite.objects.create(entity=self.trader, site=self.trader_depot)

    def setupOperator(self):
        self.operator = Entity.objects.create(
            is_enabled=True,
            name="Operator",
            entity_type=Entity.OPERATOR,
            has_trading=True,
            default_certificate="OPERATOR_CERTIFICATE",
        )
        self.operator_depot = Site.objects.create(
            site_type=Site.EFPE,
            is_enabled=True,
            name="Operator Depot",
            customs_id="BBB",
            country=self.FR,
        )
        EntitySite.objects.create(entity=self.operator, site=self.operator_depot)

    def setupOperatorTrader(self):
        self.operator_trader = Entity.objects.create(
            is_enabled=True,
            name="Operator Trader",
            entity_type=Entity.OPERATOR,
            has_trading=True,
            default_certificate="OPERATOR_TRADER_CERTIFICATE",
        )
        self.operator_trader_depot = Site.objects.create(
            site_type=Site.EFPE,
            is_enabled=True,
            name="Operator Trader Depot",
            customs_id="CCC",
            country=self.FR,
        )
        EntitySite.objects.create(entity=self.operator_trader, site=self.operator_trader_depot)

    def setUp(self):
        self.FR = Pays.objects.get(code_pays="FR")

        self.setupProducer()
        self.setupProducerTrader()
        self.setupTrader()
        self.setupOperator()
        self.setupOperatorTrader()

        self.user = setup_current_user(
            self,
            "tester@carbure.local",
            "Tester",
            "gogogo",
            [
                (self.producer, "ADMIN"),
                (self.producer_trader, "ADMIN"),
                (self.trader, "ADMIN"),
                (self.operator, "ADMIN"),
                (self.operator_trader, "ADMIN"),
            ],
        )

    def send_excel(self, entity: Entity, excel_fixture: str):
        CarbureLot.objects.filter(added_by=entity).delete()

        filepath = f"{os.environ['CARBURE_HOME']}/web/transactions/fixtures/{excel_fixture}"
        with open(filepath, "rb") as reader:
            file = SimpleUploadedFile(excel_fixture, reader.read())

        response = self.client.post(
            reverse("transactions-lots-add-excel"),
            {"entity_id": entity.id, "file": file},
        )
        if response.status_code != 200:
            print(response.json(), response.status_code)

        return CarbureLot.objects.filter(added_by=entity).all().prefetch_related("genericerror_set")

    def test_producer_excel(self):
        lots = self.send_excel(self.producer, "test_producer_template.xlsx")

        assert lots[0].carbure_producer == self.producer
        assert lots[0].carbure_production_site == self.producer_production_site
        assert lots[0].carbure_supplier == self.producer
        assert lots[0].supplier_certificate == self.producer.default_certificate
        assert lots[0].carbure_client == self.trader
        assert lots[0].genericerror_set.count() == 0

        assert lots[1].carbure_producer == self.producer
        assert lots[1].carbure_production_site == self.producer_production_site
        assert lots[1].carbure_supplier == self.producer
        assert lots[1].supplier_certificate == self.producer.default_certificate
        assert lots[1].carbure_client == self.operator
        assert lots[1].genericerror_set.count() == 0

        assert lots[2].carbure_producer == self.producer
        assert lots[2].carbure_production_site == self.producer_production_site
        assert lots[2].carbure_supplier == self.producer
        assert lots[2].supplier_certificate == self.producer.default_certificate
        assert lots[2].carbure_client == self.operator_trader
        assert lots[2].genericerror_set.count() == 0

        assert lots[3].carbure_producer is None
        assert lots[3].carbure_production_site is None
        assert lots[3].carbure_supplier is None
        assert lots[3].supplier_certificate == ""
        assert lots[3].carbure_client == self.trader
        assert lots[3].genericerror_set.count() == 2

        assert lots[4].carbure_producer == self.producer
        assert lots[4].carbure_production_site == self.producer_production_site
        assert lots[4].carbure_supplier == self.producer
        assert lots[4].supplier_certificate == self.producer.default_certificate
        assert lots[4].carbure_client == self.operator
        assert lots[4].genericerror_set.count() == 0

        assert lots[5].carbure_producer == self.producer
        assert lots[5].carbure_production_site == self.producer_production_site
        assert lots[5].carbure_supplier == self.producer
        assert lots[5].supplier_certificate == self.producer.default_certificate
        assert lots[5].carbure_client == self.operator_trader
        assert lots[5].genericerror_set.count() == 1

    def test_producer_trader_excel(self):
        lots = self.send_excel(self.producer_trader, "test_producer_trader_template.xlsx")

        assert lots[0].carbure_producer == self.producer_trader
        assert lots[0].carbure_production_site == self.producer_trader_production_site
        assert lots[0].carbure_supplier == self.producer_trader
        assert lots[0].supplier_certificate == self.producer_trader.default_certificate
        assert lots[0].carbure_client == self.trader
        assert lots[0].genericerror_set.count() == 0

        assert lots[1].carbure_producer is None
        assert lots[1].unknown_producer == ""
        assert lots[1].carbure_production_site is None
        assert lots[1].unknown_production_site == ""
        assert lots[1].carbure_supplier is None
        assert lots[1].supplier_certificate == ""
        assert lots[1].carbure_client == self.operator
        assert lots[1].genericerror_set.count() == 3

        assert lots[2].carbure_producer is None
        assert lots[2].unknown_producer == "Other Producer"
        assert lots[2].carbure_production_site is None
        assert lots[2].unknown_production_site == "Other Producer Production Site"
        assert lots[2].carbure_supplier is None
        assert lots[2].supplier_certificate == ""
        assert lots[2].carbure_client == self.operator_trader
        assert lots[2].genericerror_set.count() == 3

        assert lots[3].carbure_producer is None
        assert lots[3].unknown_producer == "Producer Trader"
        assert lots[3].carbure_production_site is None
        assert lots[3].unknown_production_site == "Wrong Production Site"
        assert lots[3].carbure_supplier is None
        assert lots[3].supplier_certificate == ""
        assert lots[3].carbure_client == self.trader
        assert lots[3].genericerror_set.count() == 2

        assert lots[4].carbure_producer == self.producer_trader
        assert lots[4].carbure_production_site == self.producer_trader_production_site
        assert lots[4].carbure_supplier == self.producer_trader
        assert lots[4].supplier_certificate == self.producer_trader.default_certificate
        assert lots[4].carbure_client == self.operator
        assert lots[4].genericerror_set.count() == 0

        assert lots[5].carbure_producer is None
        assert lots[5].unknown_producer == "Other Producer"
        assert lots[5].carbure_production_site is None
        assert lots[5].unknown_production_site == "Other Producer Production Site"
        assert lots[5].carbure_supplier is None
        assert lots[5].unknown_supplier == "Other Producer".upper()
        assert lots[5].carbure_client == self.producer_trader
        assert lots[5].genericerror_set.count() == 2
