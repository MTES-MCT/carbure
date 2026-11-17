import json
from decimal import Decimal

from django.db import connection
from django.test import TestCase
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from rest_framework import status

from core.models import Entity
from core.tests_utils import setup_current_user
from traceability.factories import ActionFactory
from traceability.models import Action, ActionStatus


class TransferCreateTest(TestCase):
    fixtures = ["json/countries.json"]

    def setUp(self):
        self.hrs = Entity.objects.create(name="Station", entity_type=Entity.HRS)
        self.recipient = Entity.objects.create(name="Opérateur", entity_type=Entity.OPERATOR, is_tiruert_liable=True)
        setup_current_user(self, "tester@carbure.local", "Tester", "password", [(self.hrs, "RW")])
        self.certificate = ActionFactory(
            holder=self.hrs,
            industry=Action.H2,
            type=Action.VALORIZE,
            status=ActionStatus.CREATED,
            quantity=Decimal("30.000"),
            material=None,
        )
        self.url = reverse("traceability-action-list")
        self.params = {"entity_id": self.hrs.id, "industry": Action.H2}

    def post(self, payload):
        return self.client.post(
            self.url, data=json.dumps(payload), content_type="application/json", query_params=self.params
        )

    def payload(self, **overrides):
        data = {
            "type": Action.TRANSFER,
            "status": ActionStatus.PENDING,
            "holder": self.recipient.id,
            "parent": self.certificate.id,
            "quantity": "10.000",
        }
        data.update(overrides)
        return data

    def test_creates_a_pending_transfer_for_part_of_the_certificate(self):
        response = self.post(self.payload())

        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        transfer = Action.objects.get(pk=response.data["id"])
        self.assertEqual(transfer.type, Action.TRANSFER)
        self.assertEqual(transfer.status, ActionStatus.PENDING)
        self.assertEqual(transfer.holder, self.recipient)
        self.assertEqual(transfer.parent, self.certificate)
        self.assertEqual(transfer.quantity, Decimal("10.000"))
        self.assertEqual(transfer.working_date, self.certificate.working_date)
        self.assertEqual(transfer.industry, Action.H2)
        self.assertTrue(transfer.pos_id)

    def test_refuses_a_recipient_that_is_not_tiruert_liable(self):
        other = Entity.objects.create(name="Autre", entity_type=Entity.OPERATOR, is_tiruert_liable=False)

        response = self.post(self.payload(holder=other.id))

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(Action.objects.filter(type=Action.TRANSFER).exists())

    def test_refuses_a_quantity_that_is_not_strictly_positive(self):
        response = self.post(self.payload(quantity="0"))

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("quantity", response.data)
        self.assertFalse(Action.objects.filter(type=Action.TRANSFER).exists())

    def test_refuses_a_quantity_above_the_certificate_remainder(self):
        response = self.post(self.payload(quantity="30.001"))

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("quantity", response.data)
        self.assertFalse(Action.objects.filter(type=Action.TRANSFER).exists())

    def test_refuses_a_transfer_to_the_holding_station(self):
        self.hrs.is_tiruert_liable = True
        self.hrs.save(update_fields=["is_tiruert_liable"])

        response = self.post(self.payload(holder=self.hrs.id))

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(Action.objects.filter(type=Action.TRANSFER).exists())

    def test_a_second_transfer_cannot_exceed_what_remains(self):
        first = self.post(self.payload(quantity="20.000"))
        self.assertEqual(first.status_code, status.HTTP_201_CREATED, first.data)

        second = self.post(self.payload(quantity="15.000"))
        self.assertEqual(second.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("quantity", second.data)

        exact = self.post(self.payload(quantity="10.000"))
        self.assertEqual(exact.status_code, status.HTTP_201_CREATED, exact.data)

    def test_locks_the_parent_certificate_before_creating(self):
        with CaptureQueriesContext(connection) as captured:
            response = self.post(self.payload())

        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        locking = [query["sql"] for query in captured.captured_queries if "FOR UPDATE" in query["sql"]]
        self.assertEqual(len(locking), 1)
        self.assertIn(str(self.certificate.id), locking[0])
