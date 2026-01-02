import xml.etree.ElementTree as ET
from datetime import datetime

from core.models import CarbureLot, Entity
from edelivery.ebms.feedstocks import from_UDB_feedstock_code
from edelivery.ebms.ntr import from_national_trade_register


class BaseRequestResponse:
    def __init__(self, payload):
        self.payload = payload
        self.parsed_XML = ET.fromstring(payload)

    def request_id(self):
        response_header_element = self.parsed_XML.find("./RESPONSE_HEADER")
        return response_header_element.attrib["REQUEST_ID"]


class EOGetTransactionResponse(BaseRequestResponse):
    def __init__(self, payload):
        super().__init__(payload)
        self.transaction_XML_element = self.parsed_XML.find("./EO_TRANS_HEADER/EO_TRANSACTION")

    def client_id(self):
        ntr = self.transaction_XML_element.find("./BUYER_ECONOMIC_OPERATOR_NUMBER").text
        return from_national_trade_register(ntr)

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
        ntr = self.transaction_XML_element.find("./SELLER_ECONOMIC_OPERATOR_NUMBER").text
        return from_national_trade_register(ntr)

    def to_lot(self):
        client = Entity.objects.get(registration_id=self.client_id())
        supplier = Entity.objects.get(registration_id=self.supplier_id())
        feedstock = from_UDB_feedstock_code(self.feedstock_code())

        return CarbureLot(
            carbure_client=client,
            carbure_supplier=supplier,
            delivery_date=self.iso_format_delivery_date(),
            feedstock=feedstock,
            period=self.period(),
            lot_status=self.status(),
            year=self.year(),
        )

    def year(self):
        return self.delivery_date().year
