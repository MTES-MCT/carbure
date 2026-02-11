from datetime import datetime
from xml.etree import ElementTree as ET

from edelivery.ebms.converters import MaterialConverter, QuantityConverter, StatusConverter
from edelivery.ebms.ntr import from_national_trade_register


class Transaction:
    @classmethod
    def from_xml(cls, xml_data):
        return cls(ET.fromstring(xml_data))

    def __init__(self, xml_root_element):
        self.xml_root_element = xml_root_element

    def biofuel_code(self):
        return self.xml_root_element.find("./MATERIAL_CODE").text

    def carbure_status(self):
        return StatusConverter().from_udb(self.status())

    def client_id(self):
        return self.xml_root_element.find("./BUYER_ECONOMIC_OPERATOR_NUMBER").text

    def delivery_date(self):
        delivery_date_element = self.xml_root_element.find("./DELIVERY_DATE")
        if delivery_date_element is None:
            return None

        delivery_date_text = delivery_date_element.text
        return datetime.fromisoformat(delivery_date_text).date()

    def etd(self):
        etd_element = self.xml_root_element.find("./POS_DATA/ETD")
        return float(etd_element.text)

    def feedstock_code(self):
        xpath = "./EO_TRANS_DETAIL_MATERIALS/POINT_OF_ORIGIN_MATERIAL_DATA/MATERIAL_CODE"
        return self.xml_root_element.find(xpath).text

    def loading_date(self):
        loading_date_text = self.xml_root_element.find("./LOADING_DATE").text
        return datetime.fromisoformat(loading_date_text).date()

    def status(self):
        return self.xml_root_element.find("./STATUS").text

    def supplier_id(self):
        return self.xml_root_element.find("./SELLER_ECONOMIC_OPERATOR_NUMBER").text

    def to_lot_attributes(self):
        biofuel_code = MaterialConverter().from_udb_biofuel_code(self.biofuel_code())
        client_id = from_national_trade_register(self.client_id())
        feedstock_code = MaterialConverter().from_udb_feedstock_code(self.feedstock_code())
        lot_status = self.carbure_status()
        quantity_data = QuantityConverter().from_udb(self.unit(), self.quantity())
        supplier_id = from_national_trade_register(self.supplier_id())

        attributes = {
            "biofuel_code": biofuel_code,
            "carbure_client_id": client_id,
            "carbure_supplier_id": supplier_id,
            "dispatch_date": self.loading_date(),
            "etd": self.etd(),
            "feedstock_code": feedstock_code,
            "lot_status": lot_status,
            "udb_transaction_id": self.udb_transaction_id(),
            **quantity_data,
        }

        delivery_date = self.delivery_date()
        if delivery_date is not None:
            attributes["delivery_date"] = delivery_date

        return attributes

    def quantity(self):
        quantity = self.xml_root_element.find("./EO_TRANS_DETAIL_MATERIALS/QUANTITY").text
        return int(quantity)

    def udb_transaction_id(self):
        return self.xml_root_element.find("./TRANSACTION_ID").text

    def unit(self):
        return self.xml_root_element.find("./EO_TRANS_DETAIL_MATERIALS/MEASURE_UNIT").text
