import xml.etree.ElementTree as ET
from datetime import datetime

from adapters.logger import log_error
from core.models import CarbureLot
from edelivery.ebms.converters import QuantityConverter
from edelivery.ebms.materials import UDBConversionError, from_UDB_biofuel_code, from_UDB_feedstock_code
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
        quantity_data = QuantityConverter().from_udb(self.unit(), self.quantity())
        supplier = from_national_trade_register(self.supplier_id())

        return {
            "biofuel": biofuel,
            "carbure_client": client,
            "carbure_supplier": supplier,
            "delivery_date": self.iso_format_delivery_date(),
            "feedstock": feedstock,
            "period": self.period(),
            "lot_status": self.status(),
            "year": self.year(),
            **quantity_data,
        }

    def post_retrieval_action_result(self):
        try:
            lot_attributes = self.to_lot_attributes()
            lot, created = CarbureLot.objects.update_or_create(
                udb_transaction_id=self.udb_transaction_id(),
                defaults=lot_attributes,
            )

            return {"newLotCreated": created, "id": lot.id}

        except UDBConversionError as e:
            error_message = "Unable to convert UDB transaction into CarbuRe lot"
            cause = e.message
            log_error(error_message, {"cause": cause})

            return {"error": error_message, "cause": cause}

    def quantity(self):
        quantity = self.transaction_XML_element.find("./EO_TRANS_DETAIL_MATERIALS/QUANTITY").text
        return int(quantity)

    def udb_transaction_id(self):
        return self.transaction_XML_element.find("./TRANSACTION_ID").text

    def unit(self):
        return self.transaction_XML_element.find("./EO_TRANS_DETAIL_MATERIALS/MEASURE_UNIT").text

    def year(self):
        return self.delivery_date().year
