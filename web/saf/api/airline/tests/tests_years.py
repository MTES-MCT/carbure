from django.test import TestCase
from django.urls import reverse


from core.tests_utils import setup_current_user
from core.models import Entity
from saf.factories import SafTicketFactory
from saf.models import SafTicket


class SafYearsTest(TestCase):
    fixtures = [
        "json/biofuels.json",
        "json/feedstock.json",
        "json/countries.json",
        "json/entities.json",
        "json/productionsites.json",
    ]

    def setUp(self):
        self.entity = Entity.objects.filter(entity_type=Entity.OPERATOR)[0]
        self.user = setup_current_user(
            self, "tester@carbure.local", "Tester", "gogogo", [(self.entity, "ADMIN")]
        )

        SafTicket.objects.all().delete()
        SafTicketFactory.create_batch(5, year=2021, client_id=self.entity.id)
        SafTicketFactory.create_batch(5, year=2022, client_id=self.entity.id)

    def test_saf_years(self):
        response = self.client.get(
            reverse("saf-airline-years"), {"entity_id": self.entity.id}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["data"], [2021, 2022])
