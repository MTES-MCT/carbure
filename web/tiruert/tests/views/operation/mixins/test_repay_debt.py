from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from core.models import MatierePremiere, UserRights
from core.tests_utils import setup_current_user
from tiruert.models import Operation
from tiruert.tests.debt_utils import DebtTestMixin


class DebtViewTestCase(DebtTestMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.user = setup_current_user(self, "tester@carbure.local", "Tester", "gogogo", [(self.entity, UserRights.ADMIN)])

    def post_repay(self, lots, entity=None, **extra):
        body = {
            "type": Operation.DEBT_REPAYMENT,
            "biofuel": self.biofuel.id,
            "customs_category": MatierePremiere.CONV,
            "debited_entity": self.entity.id,
            "lots": lots,
            **extra,
        }
        url = f"{reverse('operations-list')}?entity_id={(entity or self.entity).id}"
        return self.client.post(url, body, content_type="application/json")

    def get_debts(self):
        return self.client.get(reverse("operations-debts"), {"entity_id": self.entity.id})


class RepayDebtViewTest(DebtViewTestCase):
    def test_create_endpoint_repay_debt(self):
        lot = self.create_lot(1000)
        self.create_debt(lot, 100)
        url = f"{reverse('operations-list')}?entity_id={self.entity.id}"
        body = {
            "type": Operation.DEBT_REPAYMENT,
            "biofuel": self.biofuel.id,
            "customs_category": MatierePremiere.CONV,
            "debited_entity": self.entity.id,
            "lots": [{"id": lot.id, "volume": 50}],
        }

        response = self.client.post(url, body, content_type="application/json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["type"], Operation.DEBT_REPAYMENT)
        self.assertEqual(data[0]["status"], Operation.VALIDATED)
        self.assertEqual(data[0]["volume"], -50)

    def test_repay_debt_creates_one_operation_per_repaid_debt(self):
        """201 with the created operations serialized as negative debits without recipient, validated by default."""
        lot_a = self.create_lot(1000)
        lot_b = self.create_lot(500)
        self.create_debt(lot_a, 300)
        self.create_debt(lot_a, 200)

        response = self.post_repay([{"id": lot_a.id, "volume": 250}, {"id": lot_b.id, "volume": 250}])

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = response.json()
        self.assertEqual(len(data), 2)
        self.assertEqual([operation["type"] for operation in data], [Operation.DEBT_REPAYMENT] * 2)
        self.assertEqual([operation["status"] for operation in data], [Operation.VALIDATED] * 2)
        self.assertEqual([operation["volume"] for operation in data], [-300, -200])
        self.assertIsNone(data[0]["credited_entity"])
        self.assertEqual(data[0]["debited_entity"]["id"], self.entity.id)

    def test_repay_debt_above_the_remaining_debt_returns_400(self):
        """Over-repaying is rejected with a volume error and nothing is created."""
        lot = self.create_lot(1000)
        self.create_debt(lot, 100)

        response = self.post_repay([{"id": lot.id, "volume": 150}])

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("volume", response.json())
        self.assertEqual(Operation.objects.filter(type=Operation.DEBT_REPAYMENT).count(), 0)

    def test_repay_debt_requires_the_current_entity_as_debited_entity(self):
        """The debited entity is required and must match the current entity."""
        lot = self.create_lot(1000)
        other_lot = self.create_lot(1000, entity=self.other_entity)
        self.create_debt(lot, 100)

        response = self.post_repay([{"id": lot.id, "volume": 100}], debited_entity=self.other_entity.id)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("debited_entity", response.json())

        response = self.post_repay([{"id": other_lot.id, "volume": 10}], debited_entity=self.other_entity.id)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        body = {
            "type": Operation.DEBT_REPAYMENT,
            "biofuel": self.biofuel.id,
            "customs_category": MatierePremiere.CONV,
            "lots": [{"id": lot.id, "volume": 10}],
        }
        response = self.client.post(
            f"{reverse('operations-list')}?entity_id={self.entity.id}", body, content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("debited_entity", response.json())

    def test_repay_debt_validates_the_payload(self):
        """An empty lot list or an unknown biofuel is a 400."""
        lot = self.create_lot(1000)
        self.create_debt(lot, 100)

        self.assertEqual(self.post_repay([]).status_code, status.HTTP_400_BAD_REQUEST)

        url = f"{reverse('operations-list')}?entity_id={self.entity.id}"
        body = {
            "type": Operation.DEBT_REPAYMENT,
            "biofuel": 999999,
            "customs_category": MatierePremiere.CONV,
            "debited_entity": self.entity.id,
            "lots": [{"id": lot.id, "volume": 10}],
        }
        response = self.client.post(url, body, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_repay_debt_refuses_a_recipient(self):
        """A repayment cannot credit another entity: nothing is created."""
        lot = self.create_lot(1000)
        self.create_debt(lot, 100)

        response = self.post_repay([{"id": lot.id, "volume": 10}], credited_entity=self.other_entity.id)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("credited_entity", response.json())
        self.assertEqual(Operation.objects.filter(type=Operation.DEBT_REPAYMENT).count(), 0)

    def test_repay_debt_refuses_a_null_debited_entity(self):
        """A null debited entity is a 400, not a server error."""
        lot = self.create_lot(1000)
        self.create_debt(lot, 100)

        response = self.post_repay([{"id": lot.id, "volume": 10}], debited_entity=None)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("debited_entity", response.json())
        self.assertEqual(Operation.objects.filter(type=Operation.DEBT_REPAYMENT).count(), 0)

    def test_repay_debt_requires_write_rights(self):
        """A read-only user cannot repay a debt."""
        lot = self.create_lot(1000)
        self.create_debt(lot, 100)
        UserRights.objects.filter(user=self.user, entity=self.entity).update(role=UserRights.RO)

        response = self.post_repay([{"id": lot.id, "volume": 10}])

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Operation.objects.filter(type=Operation.DEBT_REPAYMENT).count(), 0)

    def test_repay_debt_with_draft_status_creates_drafts(self):
        """status=DRAFT returns 201 with DRAFT operations."""
        lot = self.create_lot(1000)
        self.create_debt(lot, 300)

        response = self.post_repay([{"id": lot.id, "volume": 100}], status=Operation.DRAFT)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual([operation["status"] for operation in response.json()], [Operation.DRAFT])

    def test_repay_debt_normalizes_non_draft_status_to_validated(self):
        """A repayment is VALIDATED unless explicitly requested as a DRAFT."""
        lot = self.create_lot(1000)
        self.create_debt(lot, 100)

        for requested_status in (Operation.PENDING, Operation.CANCELED):
            with self.subTest(status=requested_status):
                response = self.post_repay([{"id": lot.id, "volume": 10}], status=requested_status)
                self.assertEqual(response.status_code, status.HTTP_201_CREATED)
                self.assertEqual(response.json()[0]["status"], Operation.VALIDATED)


class DebtsViewTest(DebtViewTestCase):
    def test_debts_returns_remaining_volume_per_biofuel_and_category(self):
        """The endpoint returns one row per (biofuel, customs_category) with the biofuel and the remaining volume."""
        lot = self.create_lot(1000)
        self.create_debt(lot, 300)

        response = self.get_debts()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["customs_category"], MatierePremiere.CONV)
        self.assertEqual(data[0]["remaining_volume"], 300)
        self.assertEqual(data[0]["biofuel"]["id"], self.biofuel.id)
        self.assertEqual(data[0]["biofuel"]["code"], "EMAG")

    def test_debts_is_a_plain_list_without_pagination(self):
        """No debt gives an empty plain list."""
        response = self.get_debts()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), [])


class DebtRepaymentOperationDisplayTest(DebtViewTestCase):
    def repay_one(self, volume=100):
        lot = self.create_lot(1000)
        debt = self.create_debt(lot, 300)
        self.post_repay([{"id": lot.id, "volume": volume}])
        return lot, debt, Operation.objects.get(type=Operation.DEBT_REPAYMENT)

    def test_detail_exposes_the_debt_lot_carbure_id(self):
        """Retrieving a repayment returns its debt with the lot carbure_id."""
        lot, debt, operation = self.repay_one()

        response = self.client.get(reverse("operations-detail", kwargs={"pk": operation.id}), {"entity_id": self.entity.id})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["debt"], {"id": debt.id, "lot": {"id": lot.id, "carbure_id": lot.carbure_id}})
        self.assertEqual(response.json()["type"], Operation.DEBT_REPAYMENT)

    def test_detail_debt_is_null_for_other_operations(self):
        """Operations that do not repay a debt return debt=null."""
        lot, _, _ = self.repay_one()
        credit = Operation.objects.filter(type=Operation.INCORPORATION, credited_entity=self.entity).first()

        response = self.client.get(reverse("operations-detail", kwargs={"pk": credit.id}), {"entity_id": self.entity.id})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNone(response.json()["debt"])

    def test_list_shows_the_repayment_as_a_negative_debit(self):
        """In the list the repayment is a DEBT_REPAYMENT debit with a negative volume and no recipient."""
        self.repay_one(volume=100)

        response = self.client.get(
            reverse("operations-list"), {"entity_id": self.entity.id, "operation": Operation.DEBT_REPAYMENT}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.json()["results"]
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["type"], Operation.DEBT_REPAYMENT)
        self.assertEqual(results[0]["volume"], -100)
        self.assertIsNone(results[0]["credited_entity"])
        self.assertNotIn("debt", results[0])

    def test_list_filters_by_debit_and_status(self):
        """The repayment is found by the DEBIT transaction filter and the VALIDATED status filter."""
        self.repay_one()

        for query in ({"type": "DEBIT"}, {"status": Operation.VALIDATED}):
            with self.subTest(query=query):
                response = self.client.get(reverse("operations-list"), {"entity_id": self.entity.id, **query})
                types = [operation["type"] for operation in response.json()["results"]]
                self.assertIn(Operation.DEBT_REPAYMENT, types)

    def test_excel_export_includes_the_repayment(self):
        """The Excel export does not break on an operation without recipient."""
        self.repay_one()

        response = self.client.get(
            reverse("operations-export-operations-to-excel"),
            {"entity_id": self.entity.id, "operation": Operation.DEBT_REPAYMENT},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)


class DraftDebtRepaymentTest(DebtViewTestCase):
    def draft_one(self, volume=100):
        lot = self.create_lot(1000)
        debt = self.create_debt(lot, 300)
        self.post_repay([{"id": lot.id, "volume": volume}], status=Operation.DRAFT)
        return lot, debt, Operation.objects.get(type=Operation.DEBT_REPAYMENT)

    def patch_status(self, operation, new_status):
        url = f"{reverse('operations-detail', kwargs={'pk': operation.id})}?entity_id={self.entity.id}"
        return self.client.patch(url, {"status": new_status}, content_type="application/json")

    def delete(self, operation):
        return self.client.delete(f"{reverse('operations-detail', kwargs={'pk': operation.id})}?entity_id={self.entity.id}")

    def test_patch_draft_to_validated_is_accepted(self):
        """A repayment draft can be validated, without any new volume check."""
        lot, debt, operation = self.draft_one()

        response = self.patch_status(operation, Operation.VALIDATED)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        operation.refresh_from_db()
        self.assertEqual(operation.status, Operation.VALIDATED)
        self.assertEqual(self.remaining(debt), 200)
        self.assertEqual(self.lot_balance(lot), 900)

    def test_patch_draft_to_other_statuses_is_refused(self):
        """From DRAFT, only VALIDATED is allowed for a repayment."""
        _, _, operation = self.draft_one()

        for new_status in (Operation.PENDING, Operation.CANCELED, Operation.DRAFT, Operation.ACCEPTED):
            with self.subTest(status=new_status):
                response = self.patch_status(operation, new_status)
                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertIn("status", response.json())
        operation.refresh_from_db()
        self.assertEqual(operation.status, Operation.DRAFT)

    def test_patch_validated_repayment_is_refused(self):
        """A VALIDATED repayment cannot change status any more."""
        _, _, operation = self.draft_one()
        self.patch_status(operation, Operation.VALIDATED)

        for new_status in (Operation.DRAFT, Operation.CANCELED, Operation.VALIDATED):
            with self.subTest(status=new_status):
                response = self.patch_status(operation, new_status)
                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertIn("status", response.json())
        operation.refresh_from_db()
        self.assertEqual(operation.status, Operation.VALIDATED)

    def test_delete_draft_repayment_frees_the_volume(self):
        """A draft is deletable (204): the debt is open again and the lot balance is back."""
        lot, debt, operation = self.draft_one()

        response = self.delete(operation)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Operation.objects.filter(id=operation.id).exists())
        self.assertEqual(self.remaining(debt), 300)
        self.assertEqual(self.lot_balance(lot), 1000)

    def test_delete_validated_repayment_is_forbidden(self):
        """A VALIDATED repayment is not deletable (403)."""
        _, _, operation = self.draft_one()
        self.patch_status(operation, Operation.VALIDATED)

        response = self.delete(operation)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Operation.objects.filter(id=operation.id).exists())

    def test_draft_is_listed_and_filterable_by_status(self):
        """The draft debit shows in the entity list, with its status, and by the DRAFT and DEBIT filters."""
        self.draft_one()

        for query in ({}, {"status": Operation.DRAFT}, {"type": "DEBIT"}):
            with self.subTest(query=query):
                response = self.client.get(reverse("operations-list"), {"entity_id": self.entity.id, **query})
                results = [r for r in response.json()["results"] if r["type"] == Operation.DEBT_REPAYMENT]
                self.assertEqual(len(results), 1)
                self.assertEqual(results[0]["status"], Operation.DRAFT)

        response = self.client.get(reverse("operations-list"), {"entity_id": self.entity.id, "status": Operation.VALIDATED})
        self.assertNotIn(Operation.DEBT_REPAYMENT, [r["type"] for r in response.json()["results"]])
