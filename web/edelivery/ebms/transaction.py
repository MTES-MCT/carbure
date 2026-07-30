from datetime import datetime

from core.models.entity import Entity
from edelivery.ebms.converters import MaterialConverter, QuantityConverter, TransactionStatusConverter
from edelivery.ebms.ntr import NationalTradeRegister
from edelivery.ebms.udb_element import UDBElement


class Transaction(UDBElement):
    def biofuel_code(self):
        return self.xml_root_element.find("./MATERIAL_CODE").text

    def carbure_status(self):
        return TransactionStatusConverter().from_udb(self.status())

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
        if etd_element is None:
            return None

        return float(etd_element.text)

    def feedstock_code(self):
        xpath = "./EO_TRANS_DETAIL_MATERIALS/POINT_OF_ORIGIN_MATERIAL_DATA/MATERIAL_CODE"
        return self.xml_root_element.find(xpath).text

    def loading_date(self):
        loading_date_text = self.xml_root_element.find("./LOADING_DATE").text
        return datetime.fromisoformat(loading_date_text).date()

    def loading_site_name(self):
        return self.xml_root_element.find("./PLACE_OF_LOADING_NAME").text

    def loading_site_zipcode(self):
        return self.xml_root_element.find("./PLACE_OF_LOADING_POSTCODE").text

    def status(self):
        return self.xml_root_element.find("./STATUS").text

    def supplier_id(self):
        return self.xml_root_element.find("./SELLER_ECONOMIC_OPERATOR_NUMBER").text

    def to_lot_attributes(self):
        def entity_id(ntr_id):
            ntr = NationalTradeRegister.from_id(ntr_id)
            entity = Entity.from_national_trade_register(ntr)
            return entity.id

        biofuel_code = MaterialConverter().from_udb_biofuel_code(self.biofuel_code())
        client_id = entity_id(self.client_id())
        feedstock_code = MaterialConverter().from_udb_feedstock_code(self.feedstock_code())
        lot_status = self.carbure_status()
        quantity_data = QuantityConverter().from_udb(self.unit(), self.quantity())
        supplier_id = entity_id(self.supplier_id())

        attributes = {
            "biofuel_code": biofuel_code,
            "carbure_client_id": client_id,
            "carbure_supplier_id": supplier_id,
            "dispatch_date": self.loading_date(),
            "feedstock_code": feedstock_code,
            "lot_status": lot_status,
            "udb_transaction_id": self.udb_transaction_id(),
            **quantity_data,
        }

        delivery_date = self.delivery_date()
        if delivery_date is not None:
            attributes["delivery_date"] = delivery_date

        etd = self.etd()
        if etd is not None:
            attributes |= {"etd": etd}

        return attributes

    def quantity(self):
        quantity = self.xml_root_element.find("./EO_TRANS_DETAIL_MATERIALS/QUANTITY").text
        return int(quantity)

    def udb_transaction_id(self):
        return self.xml_root_element.find("./TRANSACTION_ID").text

    def unit(self):
        return self.xml_root_element.find("./EO_TRANS_DETAIL_MATERIALS/MEASURE_UNIT").text
