import json
from datetime import date
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from core.models import Entity
from core.tests_utils import setup_current_user
from traceability.factories import ActionFactory
from traceability.models import Action, ActionStatus, Industry


class LiableVolumeTest(TestCase):
    fixtures = ["json/countries.json"]

    def setUp(self):
        self.liable = Entity.objects.create(name="Redevable", entity_type=Entity.OPERATOR, is_tiruert_liable=True)
        self.recipient = Entity.objects.create(name="Autre redevable", entity_type=Entity.OPERATOR, is_tiruert_liable=True)
        setup_current_user(self, "liable@carbure.local", "Liable", "password", [(self.liable, "RW")])
        self.volume = ActionFactory(
            holder=self.liable,
            industry=Industry.H2,
            type=Action.TRANSFER,
            status=ActionStatus.ACCEPTED,
            quantity=Decimal("30.000"),
            material=None,
            pos_id=None,
        )
        self.url = reverse("traceability-action-list")
        self.params = {"entity_id": self.liable.id, "industry": Industry.H2}

    def post(self, payload):
        return self.client.post(
            self.url, data=json.dumps(payload), content_type="application/json", query_params=self.params
        )

    def test_cedes_part_of_an_accepted_volume(self):
        response = self.post(
            {
                "type": Action.TRANSFER,
                "status": ActionStatus.PENDING,
                "holder": self.recipient.id,
                "parent": self.volume.id,
                "quantity": "10.000",
            }
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        transfer = Action.objects.get(pk=response.data["id"])
        self.assertEqual(transfer.type, Action.TRANSFER)
        self.assertEqual(transfer.status, ActionStatus.PENDING)
        self.assertEqual(transfer.holder, self.recipient)
        self.assertEqual(transfer.parent, self.volume)
        self.assertEqual(transfer.quantity, Decimal("10.000"))
        self.assertEqual(Action.objects.get(pk=self.volume.id).quantity_available, Decimal("20.000"))

    def test_consumes_the_remainder_of_an_accepted_volume(self):
        response = self.post(
            {
                "type": Action.CONSUME,
                "status": ActionStatus.CREATED,
                "holder": self.liable.id,
                "parent": self.volume.id,
                "quantity": "30.000",
                "working_date": date.today().isoformat(),
            }
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        consumption = Action.objects.get(pk=response.data["id"])
        self.assertEqual(consumption.type, Action.CONSUME)
        self.assertEqual(consumption.status, ActionStatus.CREATED)
        self.assertEqual(consumption.holder, self.liable)
        self.assertEqual(consumption.parent, self.volume)
        self.assertEqual(Action.objects.get(pk=self.volume.id).quantity_available, Decimal("0.000"))

        follow_up = self.post(
            {
                "type": Action.TRANSFER,
                "status": ActionStatus.PENDING,
                "holder": self.recipient.id,
                "parent": self.volume.id,
                "quantity": "1.000",
            }
        )
        self.assertEqual(follow_up.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("quantity", follow_up.data)

    def test_refuses_a_lot_created_by_the_liable_party(self):
        response = self.post(
            {
                "type": Action.CONSUME,
                "status": ActionStatus.PENDING,
                "holder": self.liable.id,
                "quantity": "10.000",
                "working_date": date.today().isoformat(),
            }
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(Action.objects.filter(type=Action.CONSUME, holder=self.liable).exists())
