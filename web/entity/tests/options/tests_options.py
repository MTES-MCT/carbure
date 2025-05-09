from django.test import TestCase
from django.urls import reverse

from core.models import Entity, UserRights
from core.tests_utils import setup_current_user


class EntityProductionSiteTest(TestCase):
    fixtures = [
        "json/biofuels.json",
        "json/feedstock.json",
        "json/countries.json",
        "json/depots.json",
        "json/entities.json",
        "json/productionsites.json",
        "json/entities_sites.json",
    ]

    def setUp(self):
        self.admin = Entity.objects.filter(entity_type=Entity.ADMIN)[0]
        self.user = setup_current_user(self, "tester@carbure.local", "Tester", "gogogo", [(self.admin, "RW")], True)
        self.entity1, _ = Entity.objects.update_or_create(name="Le Super Producteur 1", entity_type="Producteur")
        UserRights.objects.update_or_create(user=self.user, entity=self.entity1, defaults={"role": UserRights.ADMIN})

        self.entity2, _ = Entity.objects.update_or_create(name="Le Super Operateur 1", entity_type="Opérateur")
        UserRights.objects.update_or_create(user=self.user, entity=self.entity2, defaults={"role": UserRights.ADMIN})

        self.entity3, _ = Entity.objects.update_or_create(name="Le Super Trader 1", entity_type="Trader")

    def test_mac_option(self):
        url = "entity-release-for-consumption"

        # wrongly formatted
        response = self.client.post(
            reverse(url) + "?entity_id=blablabla",
            {"entity_id": "blablabla", "has_mac": "true"},
        )
        assert response.status_code == 403
        # no entity_id
        response = self.client.post(reverse(url), {"has_mac": "true"})
        assert response.status_code == 403
        # entity I do not belong to
        response = self.client.post(
            reverse(url) + f"?entity_id={self.entity3.id}",
            {"entity_id": self.entity3.id, "has_mac": "true"},
        )
        assert response.status_code == 403
        # rights RW, mac option OK
        response = self.client.post(
            reverse(url) + f"?entity_id={self.entity2.id}",
            {"entity_id": self.entity2.id, "has_mac": "true"},
        )
        assert response.status_code == 200
        entity = Entity.objects.get(id=self.entity2.id)
        assert entity.has_mac is True
        # should pass
        response = self.client.post(
            reverse(url) + f"?entity_id={self.entity1.id}",
            {"entity_id": self.entity1.id, "has_mac": "true"},
        )
        assert response.status_code == 200
        entity = Entity.objects.get(id=self.entity1.id)
        assert entity.has_mac is True

        # disable:
        # wrongly formatted
        response = self.client.post(
            reverse(url) + "?entity_id=blablabla",
            {"entity_id": "blablabla", "has_mac": "false"},
        )
        assert response.status_code == 403
        # no entity_id
        response = self.client.post(reverse(url), {"has_mac": "false"})
        assert response.status_code == 403
        # entity I do not belong to
        response = self.client.post(
            reverse(url) + f"?entity_id={self.entity3.id}",
            {"entity_id": self.entity3.id, "has_mac": "false"},
        )
        assert response.status_code == 403
        # should pass
        response = self.client.post(
            reverse(url) + f"?entity_id={self.entity1.id}",
            {"entity_id": self.entity1.id, "has_mac": "false"},
        )
        assert response.status_code == 200
        entity = Entity.objects.get(id=self.entity1.id)
        assert entity.has_mac is False

        # revert
        response = self.client.post(
            reverse(url) + f"?entity_id={self.entity1.id}",
            {"entity_id": self.entity1.id, "has_mac": "true"},
        )
        assert response.status_code == 200
        entity = Entity.objects.get(id=self.entity1.id)
        assert entity.has_mac is True

    def test_trading_option(self):
        url = "entity-trading"

        # wrongly formatted
        response = self.client.post(
            reverse(url) + "?entity_id=blablabla",
            {"entity_id": "blablabla", "has_trading": "true"},
        )
        assert response.status_code == 403
        # no entity_id
        response = self.client.post(reverse(url), {"has_trading": "true"})
        assert response.status_code == 403
        # entity I do not belong to
        response = self.client.post(
            reverse(url) + f"?entity_id={self.entity3.id}",
            {"entity_id": self.entity3.id, "has_trading": "true"},
        )
        assert response.status_code == 403
        # should pass
        response = self.client.post(
            reverse(url) + f"?entity_id={self.entity1.id}",
            {"entity_id": self.entity1.id, "has_trading": "true"},
        )
        assert response.status_code == 200
        entity = Entity.objects.get(id=self.entity1.id)
        assert entity.has_trading is True

        # entity I do not belong to
        response = self.client.post(reverse(url), {"entity_id": self.entity3.id, "has_trading": "false"})
        assert response.status_code == 403
        # should pass
        response = self.client.post(
            reverse(url) + f"?entity_id={self.entity1.id}",
            {"entity_id": self.entity1.id, "has_trading": "false"},
        )
        assert response.status_code == 200
        entity = Entity.objects.get(id=self.entity1.id)
        assert entity.has_trading is False

        # revert
        response = self.client.post(
            reverse(url) + f"?entity_id={self.entity1.id}",
            {"entity_id": self.entity1.id, "has_trading": "true"},
        )
        assert response.status_code == 200
        entity = Entity.objects.get(id=self.entity1.id)
        assert entity.has_trading is True

        # should not work on Operator
        # because operators cannot trade # deprecated as of 2022
        # response = self.client.post(reverse(url_enable), {'entity_id': self.entity2.id})
        # self.assertEqual(response.status_code, 400)

    def test_elec_option(self):
        url = "entity-elec"

        # wrongly formatted
        response = self.client.post(reverse(url), {"entity_id": "blablabla", "has_elec": "true"})
        assert response.status_code == 403

        # no entity_id
        response = self.client.post(reverse(url), {"has_elec": "true"})
        assert response.status_code == 403

        # entity I do not belong to
        response = self.client.post(reverse(url), {"entity_id": self.entity3.id, "has_elec": "true"})
        assert response.status_code == 403

        # toggle to true
        response = self.client.post(
            reverse(url) + f"?entity_id={self.entity2.id}",
            {"entity_id": self.entity2.id, "has_elec": "true"},
        )
        assert response.status_code == 200
        entity = Entity.objects.get(id=self.entity2.id)
        assert entity.has_elec is True

        # revert to false
        response = self.client.post(
            reverse(url) + f"?entity_id={self.entity2.id}",
            {"entity_id": self.entity2.id, "has_elec": "false"},
        )
        assert response.status_code == 200
        entity = Entity.objects.get(id=self.entity2.id)
        assert entity.has_elec is False

        # should only work on Operator
        response = self.client.post(
            reverse(url) + f"?entity_id={self.entity1.id}", {"entity_id": self.entity1.id, "has_elec": "true"}
        )
        assert response.status_code == 400
        assert response.json()["message"] == "NOT_OPERATOR"
