from django.test import TestCase
from django.urls import reverse


from api.v4.tests_utils import setup_current_user
from core.models import Entity
from saf.factories import SafTicketSourceFactory, SafTicketFactory
from saf.models import SafTicketSource, SafTicket


class SafYearsTest(TestCase):
    fixtures = [
        "json/biofuels.json",
        "json/feedstock.json",
        "json/countries.json",
        "json/entities.json",
        "json/productionsites.json",
    ]

    def setUp(self):
        self.ticket_sources = [SafTicketSourceFactory.create() for _ in range(0, 100)]
        SafTicketSource.objects.all().delete()
        SafTicketSource.objects.bulk_create(self.ticket_sources)

        self.tickets = [SafTicketFactory.create() for _ in range(0, 100)]
        SafTicket.objects.all().delete()
        SafTicket.objects.bulk_create(self.tickets)

        # let's create a user with some rights
        self.entity = SafTicketSource.objects.first().added_by
        self.user = setup_current_user(self, "tester@carbure.local", "Tester", "gogogo", [(self.entity, "ADMIN")])

    def test_saf_years(self):
        ticket_source_years = (SafTicketSource.objects.filter(added_by_id=self.entity.id).values_list("year", flat=True).distinct())  # fmt:skip
        ticket_years = SafTicket.objects.filter(added_by_id=self.entity.id).values_list("year", flat=True).distinct()
        years = sorted(set(list(ticket_source_years) + list(ticket_years)))

        response = self.client.get(reverse("api-v5-saf-years"), {"entity_id": self.entity.id})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["data"], years)
