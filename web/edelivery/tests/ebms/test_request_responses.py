from unittest import TestCase
from unittest.mock import patch

from core.models import CarbureLot, Entity, MatierePremiere
from edelivery.ebms.request_responses import BaseRequestResponse, EOGetTransactionResponse


class BaseRequestResponseTest(TestCase):
    def payload(_, request_id):
        return f"""\
<?xml version="1.0" encoding="UTF-8"?>
<udb:GetSourcingContactByIDResponse
  xmlns:udb="http://udb.ener.ec.europa.eu/services/udbModelService/udbService/v1">
  <RESPONSE_HEADER REQUEST_ID="{request_id}"/>
  <!-- … -->
</udb:GetSourcingContactByIDResponse>"""

    def test_extract_request_id(self):
        response = BaseRequestResponse(self.payload("12345"))
        self.assertEqual("12345", response.request_id())


class EOGetTransactionResponseTest(TestCase):
    def setUp(self):
        self.patched_entity = patch("edelivery.ebms.request_responses.Entity").start()
        self.patched_entity.objects.get.return_value = Entity()

        self.patched_from_UDB_feedstock_code = patch("edelivery.ebms.request_responses.from_UDB_feedstock_code").start()
        self.patched_from_UDB_feedstock_code.return_value = MatierePremiere()

    def tearDown(self):
        patch.stopall()

    @staticmethod
    def payload(
        client_id="FR_SIREN_CD222222222",
        delivery_date="2025-01-30T00:00:00.000Z",
        feedstock=None,
        status="ACCEPTED",
        supplier_id="FR_SIREN_CD111111111",
        udb_transaction_id="TRN-0000000159437-1766484490",
    ):
        if feedstock is None:
            feedstock = {"code": "URWS023", "name": "Sugar beet"}

        return f"""\
<udb:EOGetTransactionResponse xmlns:udb="http://udb.ener.ec.europa.eu/services/udbModelService/udbService/v1">
  <RESPONSE_HEADER REQUEST_ID="e0907dde-11f5-423b-90e7-6a79728a5ef8"
            PROCESSING_DATE="2025-12-23T11:11:57.548+01:00"
            STATUS="FOUND" />
  <EO_TRANS_HEADER>
    <EO_TRANSACTION>
      <SELLER_ECONOMIC_OPERATOR_NUMBER>{supplier_id}</SELLER_ECONOMIC_OPERATOR_NUMBER>
      <SELLER_CERTIFICATE_NUMBER>EU-ISCC-Cert-Test-FR004</SELLER_CERTIFICATE_NUMBER>
      <BUYER_ECONOMIC_OPERATOR_NUMBER>{client_id}</BUYER_ECONOMIC_OPERATOR_NUMBER>
      <LOADING_DATE>2025-12-26T00:00:00.000Z</LOADING_DATE>
      <PLACE_OF_LOADING_NAME>TestSite004</PLACE_OF_LOADING_NAME>
      <PLACE_OF_LOADING_POSTCODE>1004</PLACE_OF_LOADING_POSTCODE>
      <DELIVERY_DATE>{delivery_date}</DELIVERY_DATE>
      <REFERENCE_NUMBER>SOME_REFERENCE</REFERENCE_NUMBER>
      <TRADE_DATE>2025-12-22T00:00:00.000Z</TRADE_DATE>
      <MATERIAL_CODE>SFC0015</MATERIAL_CODE>
      <STATUS>{status}</STATUS>
      <POS_ID>POS-0000000219349-1766484490</POS_ID>
      <TRANSACTION_ID>{udb_transaction_id}</TRANSACTION_ID>
      <NON_RECOGNISED_VS>false</NON_RECOGNISED_VS>
      <MATERIAL_NAME>Biogas</MATERIAL_NAME>
      <EO_TRANS_DETAIL_MATERIALS>
        <ORIGINAL_POS>POS-0000000219348-1766484297</ORIGINAL_POS>
        <PREVIOUS_POS>POS-0000000219347-1766484297</PREVIOUS_POS>
        <QUANTITY>2000</QUANTITY>
        <MEASURE_UNIT>MWh</MEASURE_UNIT>
        <CONSIGNMENT_MATERIAL_DATA>
          <NON_RECOGNISED_VS>false</NON_RECOGNISED_VS>
          <COUNTRY_OF_PRODUCTION>FR</COUNTRY_OF_PRODUCTION>
          <PRODUCTION_PLANT_START_DATE>2025-12-22T00:00:00.000Z</PRODUCTION_PLANT_START_DATE>
        </CONSIGNMENT_MATERIAL_DATA>
        <POINT_OF_ORIGIN_MATERIAL_DATA>
          <ORIGINAL_POS>POS-0000000202542-1759499603</ORIGINAL_POS>
          <MATERIAL_CODE>{feedstock["code"]}</MATERIAL_CODE>
          <MATERIAL_NAME>{feedstock["name"]}</MATERIAL_NAME>
          <BIOMASS_LAND_CRITERIA>false</BIOMASS_LAND_CRITERIA>
          <LOW_ILUC>false</LOW_ILUC>
          <COUNTRY_OF_ORIGIN>FR</COUNTRY_OF_ORIGIN>
        </POINT_OF_ORIGIN_MATERIAL_DATA>
        <GHG_DETAILS>
          <GHG_METHOD_TYPE>AV</GHG_METHOD_TYPE>
          <GHG_TOTAL_VALUE>31.8</GHG_TOTAL_VALUE>
          <GHG_MEASURING_UNIT_ACR>gCO2eq/MJ</GHG_MEASURING_UNIT_ACR>
          <EEC>10</EEC>
          <EP>20</EP>
          <ETD>1.8</ETD>
          <DISTANCE_ROAD>100</DISTANCE_ROAD>
          <DDV_APPLIED_FOR_SOIL_N2O_EMISSIONS>false</DDV_APPLIED_FOR_SOIL_N2O_EMISSIONS>
          <FUEL_BONUS_IF_BIOMASS_FROM_RESTORED_DEGRADED_LAND>false</FUEL_BONUS_IF_BIOMASS_FROM_RESTORED_DEGRADED_LAND>
        </GHG_DETAILS>
      </EO_TRANS_DETAIL_MATERIALS>
      <POS_DATA>
        <POS_FLAG>true</POS_FLAG>
        <METHOD_TYPE>AV</METHOD_TYPE>
        <ETD>2</ETD>
        <COMMENTS>Anyway.</COMMENTS>
        <SELLER_TRANSPORT>
          <TRANSPORT_DATA>
            <MODE_OF_TRANSPORT_ROAD_DISTANCE_KM>120</MODE_OF_TRANSPORT_ROAD_DISTANCE_KM>
          </TRANSPORT_DATA>
        </SELLER_TRANSPORT>
      </POS_DATA>
    </EO_TRANSACTION>
  </EO_TRANS_HEADER>
</udb:EOGetTransactionResponse>"""

    def test_converts_into_carbure_lot(self):
        response = EOGetTransactionResponse(self.payload())
        carbure_lot = response.to_lot()
        self.assertIsInstance(carbure_lot, CarbureLot)

    def test_knows_its_udb_transaction_id(self):
        response = EOGetTransactionResponse(self.payload(udb_transaction_id="TRN-0000000000001-1234567890"))
        self.assertEqual("TRN-0000000000001-1234567890", response.udb_transaction_id())

        carbure_lot = response.to_lot()
        self.assertEqual("TRN-0000000000001-1234567890", carbure_lot.udb_transaction_id)

    def test_knows_its_delivery_date_in_ISO_format(self):
        response = EOGetTransactionResponse(self.payload(delivery_date="2025-12-22T00:00:00.000Z"))
        self.assertEqual("2025-12-22", response.iso_format_delivery_date())

        carbure_lot = response.to_lot()
        self.assertEqual("2025-12-22", carbure_lot.delivery_date)

    def test_knows_its_delivery_month_period(self):
        response = EOGetTransactionResponse(self.payload(delivery_date="2025-12-22T00:00:00.000Z"))
        self.assertEqual(202512, response.period())

        carbure_lot = response.to_lot()
        self.assertEqual(202512, carbure_lot.period)

    def test_knows_its_year(self):
        response = EOGetTransactionResponse(self.payload(delivery_date="2025-12-22T00:00:00.000Z"))
        self.assertEqual(2025, response.year())

        carbure_lot = response.to_lot()
        self.assertEqual(2025, carbure_lot.year)

    def test_knows_its_supplier(self):
        entity = Entity(name="Some Entity")
        entity_get = self.patched_entity.objects.get
        entity_get.return_value = entity

        response = EOGetTransactionResponse(self.payload(supplier_id="FR_SIREN_CD123456789"))
        self.assertEqual("123456789", response.supplier_id())
        entity_get.assert_not_called()

        lot_carbure = response.to_lot()
        entity_get.assert_any_call(registration_id="123456789")
        self.assertEqual("Some Entity", lot_carbure.carbure_supplier.name)

    def test_knows_its_client_id(self):
        entity = Entity(name="Some Entity")
        entity_get = self.patched_entity.objects.get
        entity_get.return_value = entity

        response = EOGetTransactionResponse(self.payload(client_id="FR_SIREN_CD123456780"))
        self.assertEqual("123456780", response.client_id())
        entity_get.assert_not_called()

        lot_carbure = response.to_lot()
        entity_get.assert_any_call(registration_id="123456780")
        self.assertEqual("Some Entity", lot_carbure.carbure_client.name)

    def test_knows_its_status(self):
        response = EOGetTransactionResponse(self.payload(status="PENDING"))
        self.assertEqual("PENDING", response.status())

        carbure_lot = response.to_lot()
        self.assertEqual("PENDING", carbure_lot.lot_status)

    def test_knows_its_feedstock_code(self):
        self.patched_from_UDB_feedstock_code.return_value = MatierePremiere(name="Betterave")

        response = EOGetTransactionResponse(self.payload(feedstock={"code": "URWS023", "name": "Sugar beet"}))
        self.assertEqual("URWS023", response.feedstock_code())
        self.patched_from_UDB_feedstock_code.assert_not_called()

        carbure_lot = response.to_lot()
        self.patched_from_UDB_feedstock_code.assert_called_with("URWS023")
        self.assertEqual("Betterave", carbure_lot.feedstock.name)
