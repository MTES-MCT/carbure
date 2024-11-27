from django.urls import reverse

from saf.factories import SafTicketFactory, SafTicketSourceFactory
from saf.models import SafTicket, SafTicketSource
from saf.tests import TestCase


class SafYearsTest(TestCase):
    def setUp(self):
        super().setUp()

        SafTicketSource.objects.all().delete()
        SafTicketSourceFactory.create_batch(10, year=2021, added_by_id=self.entity.id)
        SafTicketSourceFactory.create_batch(10, year=2022, added_by_id=self.entity.id)

        SafTicket.objects.all().delete()
        SafTicketFactory.create_batch(10, year=2022, supplier_id=self.entity.id)

    def test_saf_years(self):
        response = self.client.get(reverse("saf-years"), {"entity_id": self.entity.id})
        assert response.status_code == 200
        assert response.json() == [2021, 2022]
