import os

import pandas as pd
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
    ]

    # create the entity that will import the excel file
    def setupOwnerEntity(self):
        self.owner = Entity.objects.create(
            is_enabled=True,
            name="Owner",
            default_certificate="OWNER_CERTIFICATE",
        )
        self.owner_production_site = Site.objects.create(
            site_type=Site.PRODUCTION_BIOLIQUID,
            is_enabled=True,
            name="Owner Production Site",
            country=self.FR,
            created_by=self.owner,
        )
        self.owner_depot = Site.objects.create(
            site_type=Site.EFPE,
            is_enabled=True,
            name="Owner Depot",
            customs_id="AAA",
            country=self.FR,
        )

    # create another entity that will be involved in transactions
    def setupOtherEntity(self):
        self.other = Entity.objects.create(
            is_enabled=True,
            name="Other",
            entity_type=Entity.OPERATOR,
            default_certificate="OTHER_CERTIFICATE",
            has_trading=True,
        )
        self.other_depot = Site.objects.create(
            site_type=Site.EFPE,
            is_enabled=True,
            name="Other Depot",
            customs_id="BBB",
            country=self.FR,
        )
        EntitySite.objects.create(entity=self.other, site=self.other_depot)

    def setUp(self):
        self.FR = Pays.objects.get(code_pays="FR")

        self.setupOwnerEntity()
        self.setupOtherEntity()

        self.user = setup_current_user(
            self,
            "tester@carbure.local",
            "Tester",
            "gogogo",
            [(self.owner, "ADMIN")],
        )

    def debug_lots(self, title, lots):
        values = lots.values(
            "free_field",
            "carbure_producer",
            "unknown_producer",
            "carbure_production_site",
            "unknown_production_site",
            "carbure_supplier",
            "unknown_supplier",
            "carbure_vendor",
            "carbure_client",
            "unknown_client",
        )

        print(title)
        print(pd.DataFrame(values).fillna(""))

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
        self.owner.entity_type = Entity.PRODUCER
        self.owner.has_trading = False
        self.owner.has_stocks = False
        self.owner.save()

        # add production site, remove depot
        EntitySite.objects.update_or_create(entity=self.owner, site=self.owner_production_site)
        EntitySite.objects.filter(entity=self.owner, site=self.owner_depot).delete()

        lots = self.send_excel(self.owner, "test_lot_template.xlsx")

        assert lots.filter(carbure_producer=self.owner).count() == 4
        assert lots.filter(carbure_producer=None, unknown_producer="").count() == 1
        assert lots.filter(carbure_producer=None, unknown_producer="Unknown").count() == 3

        assert lots.filter(carbure_production_site=self.owner_production_site).count() == 4
        assert lots.filter(carbure_production_site=None, unknown_production_site="Unknown Production Site").count() == 3

        assert lots.filter(carbure_supplier=self.owner).count() == 6
        assert lots.filter(carbure_supplier=None, unknown_supplier="UNKNOWN").count() == 2
        assert lots.filter(supplier_certificate=self.owner.default_certificate).count() == 6

        assert lots.filter(carbure_vendor=self.owner).count() == 0
        assert lots.filter(vendor_certificate=self.owner.default_certificate).count() == 0

        assert lots.filter(carbure_client=self.owner).count() == 1
        assert lots.filter(carbure_client=self.other).count() == 5

        assert lots.filter(carbure_delivery_site=self.owner_depot).count() == 1
        assert lots.filter(carbure_delivery_site=self.other_depot).count() == 5

    def test_producer_trader_excel(self):
        self.owner.entity_type = Entity.PRODUCER
        self.owner.has_trading = True
        self.owner.has_stocks = True
        self.owner.save()

        # add production site, remove depot
        EntitySite.objects.update_or_create(entity=self.owner, site=self.owner_production_site)
        EntitySite.objects.filter(entity=self.owner, site=self.owner_depot).delete()

        lots = self.send_excel(self.owner, "test_lot_template.xlsx")

        assert lots.filter(carbure_producer=self.owner).count() == 4
        assert lots.filter(carbure_producer=None, unknown_producer="").count() == 1
        assert lots.filter(unknown_producer="Unknown").count() == 3

        assert lots.filter(carbure_production_site=self.owner_production_site).count() == 4
        assert lots.filter(unknown_production_site="Unknown Production Site").count() == 3

        assert lots.filter(carbure_supplier=self.owner).count() == 6
        assert lots.filter(carbure_supplier=None, unknown_supplier="Unknown").count() == 2
        assert lots.filter(supplier_certificate=self.owner.default_certificate).count() == 6

        assert lots.filter(carbure_vendor=self.owner).count() == 1
        assert lots.filter(vendor_certificate=self.owner.default_certificate).count() == 1

        assert lots.filter(carbure_client=self.owner).count() == 1
        assert lots.filter(carbure_client=self.other).count() == 5

        assert lots.filter(carbure_delivery_site=self.owner_depot).count() == 1
        assert lots.filter(carbure_delivery_site=self.other_depot).count() == 5

    def test_operator_excel(self):
        self.owner.entity_type = Entity.OPERATOR
        self.owner.has_trading = False
        self.owner.has_stocks = False
        self.owner.save()

        # remove production site, add depot
        EntitySite.objects.filter(entity=self.owner, site=self.owner_production_site).delete()
        EntitySite.objects.update_or_create(entity=self.owner, site=self.owner_depot)

        lots = self.send_excel(self.owner, "test_lot_template.xlsx")

        assert lots.filter(carbure_producer=None).count() == 8
        assert lots.filter(unknown_producer="Owner").count() == 3

        assert lots.filter(carbure_production_site=None).count() == 8
        assert lots.filter(unknown_production_site="Owner Production Site").count() == 4

        assert lots.filter(carbure_supplier=self.owner).count() == 6
        assert lots.filter(carbure_supplier=None, unknown_supplier="Unknown").count() == 2
        assert lots.filter(supplier_certificate=self.owner.default_certificate).count() == 6

        assert lots.filter(carbure_vendor=self.owner).count() == 1
        assert lots.filter(vendor_certificate=self.owner.default_certificate).count() == 1

        assert lots.filter(carbure_client=self.owner).count() == 2
        assert lots.filter(carbure_client=self.other).count() == 5

        assert lots.filter(carbure_delivery_site=self.owner_depot).count() == 1
        assert lots.filter(carbure_delivery_site=self.other_depot).count() == 5

    def test_trader_excel(self):
        self.owner.entity_type = Entity.TRADER
        self.owner.has_trading = True
        self.owner.has_stocks = True
        self.owner.save()

        # remove production site, add depot
        EntitySite.objects.filter(entity=self.owner, site=self.owner_production_site).delete()
        EntitySite.objects.update_or_create(entity=self.owner, site=self.owner_depot)

        lots = self.send_excel(self.owner, "test_lot_template.xlsx")

        assert lots.filter(carbure_producer=None).count() == 8
        assert lots.filter(unknown_producer="Owner").count() == 3

        assert lots.filter(carbure_production_site=None).count() == 8
        assert lots.filter(unknown_production_site="Owner Production Site").count() == 4

        assert lots.filter(carbure_supplier=self.owner).count() == 6
        assert lots.filter(carbure_supplier=None, unknown_supplier="Unknown").count() == 2
        assert lots.filter(supplier_certificate=self.owner.default_certificate).count() == 6

        assert lots.filter(carbure_vendor=self.owner).count() == 1
        assert lots.filter(vendor_certificate=self.owner.default_certificate).count() == 1

        assert lots.filter(carbure_client=self.owner).count() == 1
        assert lots.filter(carbure_client=self.other).count() == 5

        assert lots.filter(carbure_delivery_site=self.owner_depot).count() == 1
        assert lots.filter(carbure_delivery_site=self.other_depot).count() == 5
