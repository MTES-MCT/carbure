from api.v4.tests_utils import setup_current_user
from core.models import Entity, Pays, ProductionSite, MatierePremiere, Biocarburant, UserRights
from producers.models import ProductionSite, ProductionSiteInput, ProductionSiteOutput
from django.test import TestCase
from django.urls import reverse


class EntityProductionSiteTest(TestCase):
    fixtures = [
        "json/biofuels.json",
        "json/feedstock.json",
        "json/countries.json",
        "json/depots.json",
        "json/entities.json",
        "json/productionsites.json",
    ]

    def setUp(self):
        self.admin = Entity.objects.filter(entity_type=Entity.ADMIN)[0]
        self.user = setup_current_user(self, "tester@carbure.local", "Tester", "gogogo", [(self.admin, "RW")], True)
        self.entity1, _ = Entity.objects.update_or_create(name="Le Super Producteur 1", entity_type="Producteur")
        UserRights.objects.update_or_create(user=self.user, entity=self.entity1, defaults={"role": UserRights.ADMIN})

        self.entity2, _ = Entity.objects.update_or_create(name="Le Super Operateur 1", entity_type="Opérateur")
        UserRights.objects.update_or_create(user=self.user, entity=self.entity2, defaults={"role": UserRights.ADMIN})

        self.entity3, _ = Entity.objects.update_or_create(name="Le Super Trader 1", entity_type="Trader")
        UserRights.objects.update_or_create(user=self.user, entity=self.entity2, defaults={"role": UserRights.ADMIN})

    def test_mac_option(self):
        url = "entity-options-rfc"

        # wrongly formatted
        response = self.client.post(reverse(url), {"entity_id": "blablabla", "has_mac": "true"})
        self.assertEqual(response.status_code, 403)
        # no entity_id
        response = self.client.post(reverse(url), {"has_mac": "true"})
        self.assertEqual(response.status_code, 400)
        # entity I do not belong to
        response = self.client.post(reverse(url), {"entity_id": self.entity3.id, "has_mac": "true"})
        self.assertEqual(response.status_code, 403)
        # rights RW, mac option OK
        response = self.client.post(reverse(url), {"entity_id": self.entity2.id, "has_mac": "true"})
        self.assertEqual(response.status_code, 200)
        entity = Entity.objects.get(id=self.entity2.id)
        self.assertEqual(entity.has_mac, True)
        # should pass
        response = self.client.post(reverse(url), {"entity_id": self.entity1.id, "has_mac": "true"})
        self.assertEqual(response.status_code, 200)
        entity = Entity.objects.get(id=self.entity1.id)
        self.assertEqual(entity.has_mac, True)

        # disable:
        # wrongly formatted
        response = self.client.post(reverse(url), {"entity_id": "blablabla", "has_mac": "false"})
        self.assertEqual(response.status_code, 403)
        # no entity_id
        response = self.client.post(reverse(url), {"has_mac": "false"})
        self.assertEqual(response.status_code, 400)
        # entity I do not belong to
        response = self.client.post(reverse(url), {"entity_id": self.entity3.id, "has_mac": "false"})
        self.assertEqual(response.status_code, 403)
        # should pass
        response = self.client.post(reverse(url), {"entity_id": self.entity1.id, "has_mac": "false"})
        self.assertEqual(response.status_code, 200)
        entity = Entity.objects.get(id=self.entity1.id)
        self.assertEqual(entity.has_mac, False)

        # revert
        response = self.client.post(reverse(url), {"entity_id": self.entity1.id, "has_mac": "true"})
        self.assertEqual(response.status_code, 200)
        entity = Entity.objects.get(id=self.entity1.id)
        self.assertEqual(entity.has_mac, True)

    def test_trading_option(self):
        url = "entity-options-trading"

        # wrongly formatted
        response = self.client.post(reverse(url), {"entity_id": "blablabla", "has_trading": "true"})
        self.assertEqual(response.status_code, 403)
        # no entity_id
        response = self.client.post(reverse(url), {"has_trading": "true"})
        self.assertEqual(response.status_code, 400)
        # entity I do not belong to
        response = self.client.post(reverse(url), {"entity_id": self.entity3.id, "has_trading": "true"})
        self.assertEqual(response.status_code, 403)
        # should pass
        response = self.client.post(reverse(url), {"entity_id": self.entity1.id, "has_trading": "true"})
        self.assertEqual(response.status_code, 200)
        entity = Entity.objects.get(id=self.entity1.id)
        self.assertEqual(entity.has_trading, True)

        # disable:
        # wrongly formatted
        response = self.client.post(reverse(url), {"entity_id": "blablabla", "has_trading": "false"})
        self.assertEqual(response.status_code, 403)
        # no entity_id
        response = self.client.post(reverse(url), {"has_trading": "false"})
        self.assertEqual(response.status_code, 400)
        # entity I do not belong to
        response = self.client.post(reverse(url), {"entity_id": self.entity3.id, "has_trading": "false"})
        self.assertEqual(response.status_code, 403)
        # should pass
        response = self.client.post(reverse(url), {"entity_id": self.entity1.id, "has_trading": "false"})
        self.assertEqual(response.status_code, 200)
        entity = Entity.objects.get(id=self.entity1.id)
        self.assertEqual(entity.has_trading, False)

        # revert
        response = self.client.post(reverse(url), {"entity_id": self.entity1.id, "has_trading": "true"})
        self.assertEqual(response.status_code, 200)
        entity = Entity.objects.get(id=self.entity1.id)
        self.assertEqual(entity.has_trading, True)

        # should not work on Operator
        # because operators cannot trade # deprecated as of 2022
        # response = self.client.post(reverse(url_enable), {'entity_id': self.entity2.id})
        # self.assertEqual(response.status_code, 400)
