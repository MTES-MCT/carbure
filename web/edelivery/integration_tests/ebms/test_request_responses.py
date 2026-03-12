from datetime import date

from django.test import TestCase

from core.models import Biocarburant, CarbureLot, Entity, MatierePremiere, Pays
from edelivery.ebms.request_responses import BaseRequestResponse, EOGetTransactionResponse
from edelivery.tests.ebms.fixtures.udb_xml_data import transaction_data
from edelivery.tests.ebms.test_request_responses import BaseRequestResponseTest
from transactions.api.lots.tests.tests_utils import get_lot

class EOGetTransactionResponseTest(TestCase):
    def payload(self, nb_transactions=1, **kwargs):
        transactions = "".join([transaction_data(**kwargs) for i in range(0, nb_transactions)])

        return f"""\
<udb:EOGetTransactionResponse xmlns:udb="http://udb.ener.ec.europa.eu/services/udbModelService/udbService/v1">
  <RESPONSE_HEADER REQUEST_ID="e0907dde-11f5-423b-90e7-6a79728a5ef8"
            PROCESSING_DATE="2025-12-23T11:11:57.548+01:00"
            STATUS="FOUND" />
  <EO_TRANS_HEADER>
    {transactions}
  </EO_TRANS_HEADER>
</udb:EOGetTransactionResponse>"""

    @classmethod
    def setUpTestData(cls):
        Biocarburant.objects.create(code="EMAG", pci_kg=27.0, pci_litre=21.0, masse_volumique=0.778)
        MatierePremiere.objects.create(code="COLZA")
        france = Pays.objects.create(code_pays="FR")
        cls.entite = Entity.objects.create(registered_country=france, registration_id="123456789")

    def test_creates_lot_with_non_draft_status(self):
        payload = self.payload(
            biofuel={"code": "FBM0003", "name": "FAME"},
            client_id="FR_SIREN_CD123456789",
            feedstock={"code": "URWR001", "name": "Rapeseed"},
            status="PENDING",
            supplier_id="FR_SIREN_CD123456789",
        )
        response = EOGetTransactionResponse(payload)

        result = response.post_retrieval_action_result()
        created_lot = CarbureLot.objects.get(id=result[0]["id"])
        self.assertEqual("PENDING", created_lot.lot_status)

    def test_updates_exising_lot(self):
        existing_lot = CarbureLot.objects.create(
            added_by=self.entite,
            carbure_client=self.entite,
            carbure_supplier=self.entite,
            dispatch_date=date(2026, 1, 31),
            period=202601,
            udb_transaction_id="12345",
            year=2026,
        )

        response = EOGetTransactionResponse(self.payload(
            biofuel={"code": "FBM0003", "name": "FAME"},
            client_id="FR_SIREN_CD123456789",
            feedstock={"code": "URWR001", "name": "Rapeseed"},
            supplier_id="FR_SIREN_CD123456789",
            udb_transaction_id="12345",
            loading_date=date(2026,3,15),
        ))
        response.post_retrieval_action_result()
        existing_lot.refresh_from_db()
        self.assertEqual(date(2026,3,15), existing_lot.dispatch_date)
