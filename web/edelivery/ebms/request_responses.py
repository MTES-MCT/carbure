import xml.etree.ElementTree as ET
from datetime import datetime

from adapters.logger import log_error
from core.models import CarbureLot
from edelivery.ebms.materials import from_UDB_biofuel_code, from_UDB_feedstock_code
from edelivery.ebms.ntr import from_national_trade_register


class BaseRequestResponse:
    def __init__(self, payload):
        self.payload = payload
        self.parsed_XML = ET.fromstring(payload)

    def request_id(self):
        response_header_element = self.parsed_XML.find("./RESPONSE_HEADER")
        return response_header_element.attrib["REQUEST_ID"]

    def post_retrieval_action_result(self):
        pass


class InvalidRequestErrorResponse(BaseRequestResponse):
    def error_message(self):
        return self.parsed_XML.find("./RESPONSE_HEADER").attrib["OBSERVATION"]

    def post_retrieval_action_result(self):
        error_message = self.error_message()
        log_error("Invalid request", {"error": error_message})
        return {"error": "Invalid request", "message": error_message}


class NotFoundErrorResponse(BaseRequestResponse):
    def post_retrieval_action_result(self):
        log_error("Search returned no result")
        return {"error": "Not found"}


class EOGetTransactionResponse(BaseRequestResponse):
    def __init__(self, payload):
        super().__init__(payload)
        self.transaction_XML_element = self.parsed_XML.find("./EO_TRANS_HEADER/EO_TRANSACTION")

    def biofuel_code(self):
        return self.transaction_XML_element.find("./MATERIAL_CODE").text

    def client_id(self):
        return self.transaction_XML_element.find("./BUYER_ECONOMIC_OPERATOR_NUMBER").text

    def delivery_date(self):
        delivery_date_text = self.transaction_XML_element.find("./DELIVERY_DATE").text
        return datetime.fromisoformat(delivery_date_text)

    def feedstock_code(self):
        xpath = "./EO_TRANS_DETAIL_MATERIALS/POINT_OF_ORIGIN_MATERIAL_DATA/MATERIAL_CODE"
        return self.transaction_XML_element.find(xpath).text

    def iso_format_delivery_date(self):
        return self.delivery_date().date().isoformat()

    def period(self):
        delivery_date = self.delivery_date()
        return delivery_date.year * 100 + delivery_date.month

    def status(self):
        return self.transaction_XML_element.find("./STATUS").text

    def supplier_id(self):
        return self.transaction_XML_element.find("./SELLER_ECONOMIC_OPERATOR_NUMBER").text

    def to_lot_attributes(self):
        biofuel = from_UDB_biofuel_code(self.biofuel_code())
        client = from_national_trade_register(self.client_id())
        feedstock = from_UDB_feedstock_code(self.feedstock_code())
        lhv_amount = self.quantity() * 3600
        supplier = from_national_trade_register(self.supplier_id())

        return {
            "biofuel": biofuel,
            "carbure_client": client,
            "carbure_supplier": supplier,
            "delivery_date": self.iso_format_delivery_date(),
            "feedstock": feedstock,
            "period": self.period(),
            "lot_status": self.status(),
            "lhv_amount": lhv_amount,
            "year": self.year(),
        }

    def post_retrieval_action_result(self):
        lot_attributes = self.to_lot_attributes()
        lot, created = CarbureLot.objects.update_or_create(
            udb_transaction_id=self.udb_transaction_id(),
            defaults=lot_attributes,
        )

        return {"newLotCreated": created, "id": lot.id}

    def quantity(self):
        quantity = self.transaction_XML_element.find("./EO_TRANS_DETAIL_MATERIALS/QUANTITY").text
        return int(quantity)

    def udb_transaction_id(self):
        return self.transaction_XML_element.find("./TRANSACTION_ID").text

    def year(self):
        return self.delivery_date().year
