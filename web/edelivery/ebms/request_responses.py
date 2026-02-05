import xml.etree.ElementTree as ET

from adapters.logger import log_error
from core.models import CarbureLot
from edelivery.ebms.converters import UDBConversionError
from edelivery.ebms.transaction import Transaction


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
    def post_retrieval_action_result(self):
        return [self.update_or_create_lot(transaction) for transaction in self.transactions()]

    def transactions(self):
        for parsed_transaction_data in self.parsed_XML.iter("EO_TRANSACTION"):
            yield Transaction(parsed_transaction_data)

    def update_or_create_lot(self, transaction):
        try:
            lot_attributes = transaction.to_lot_attributes()
            lot, created = CarbureLot.objects.update_or_create(
                udb_transaction_id=transaction.udb_transaction_id(),
                defaults=lot_attributes,
            )

            return {"newLotCreated": created, "id": lot.id}

        except UDBConversionError as e:
            error_message = "Unable to convert UDB transaction into CarbuRe lot"
            cause = e.message
            log_error(error_message, {"cause": cause})

            return {"error": error_message, "cause": cause}
