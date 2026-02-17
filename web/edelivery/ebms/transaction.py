from datetime import datetime
from xml.etree import ElementTree as ET

from edelivery.ebms.converters import MaterialConverter, QuantityConverter, StatusConverter
from edelivery.ebms.ntr import from_national_trade_register
from transactions.helpers import compute_lot_quantity


class Transaction:
    @classmethod
    def from_xml(cls, xml_data):
        return cls(ET.fromstring(xml_data))

    def __init__(self, xml_root_element):
        self.xml_root_element = xml_root_element

    def biofuel_code(self):
        return self.xml_root_element.find("./MATERIAL_CODE").text

    def client_id(self):
        return self.xml_root_element.find("./BUYER_ECONOMIC_OPERATOR_NUMBER").text

    def delivery_date(self):
        delivery_date_text = self.xml_root_element.find("./DELIVERY_DATE").text
        return datetime.fromisoformat(delivery_date_text)

    def feedstock_code(self):
        xpath = "./EO_TRANS_DETAIL_MATERIALS/POINT_OF_ORIGIN_MATERIAL_DATA/MATERIAL_CODE"
        return self.xml_root_element.find(xpath).text

    def iso_format_delivery_date(self):
        return self.delivery_date().date().isoformat()

    def period(self):
        delivery_date = self.delivery_date()
        return delivery_date.year * 100 + delivery_date.month

    def status(self):
        return self.xml_root_element.find("./STATUS").text

    def supplier_id(self):
        return self.xml_root_element.find("./SELLER_ECONOMIC_OPERATOR_NUMBER").text

    def to_lot_attributes(self):
        biofuel = MaterialConverter().from_udb_biofuel_code(self.biofuel_code())
        client = from_national_trade_register(self.client_id())
        feedstock = MaterialConverter().from_udb_feedstock_code(self.feedstock_code())
        lot_status = StatusConverter().from_udb(self.status())
        quantity_data = QuantityConverter().from_udb(self.unit(), self.quantity())
        computed_quantity_data = compute_lot_quantity(biofuel, quantity_data)
        supplier = from_national_trade_register(self.supplier_id())

        return {
            "biofuel": biofuel,
            "carbure_client": client,
            "carbure_supplier": supplier,
            "delivery_date": self.iso_format_delivery_date(),
            "feedstock": feedstock,
            "period": self.period(),
            "lot_status": lot_status,
            "year": self.year(),
            **computed_quantity_data,
        }

    def quantity(self):
        quantity = self.xml_root_element.find("./EO_TRANS_DETAIL_MATERIALS/QUANTITY").text
        return int(quantity)

    def udb_transaction_id(self):
        return self.xml_root_element.find("./TRANSACTION_ID").text

    def unit(self):
        return self.xml_root_element.find("./EO_TRANS_DETAIL_MATERIALS/MEASURE_UNIT").text

    def year(self):
        return self.delivery_date().year
