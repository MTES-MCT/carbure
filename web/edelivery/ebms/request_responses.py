import xml.etree.ElementTree as ET

from django.core.exceptions import ObjectDoesNotExist

from adapters.logger import log_error
from core.models import Biocarburant, CarbureLot, Entity, MatierePremiere
from edelivery.ebms.converters import UDBConversionError
from edelivery.ebms.transaction import Transaction
from transactions.services.lots import LotCreationFailure, LotUpdateFailure, create_lot, do_update_lot


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
    def handle_error(self, message, cause=None):
        if cause:
            log_error(message, {"cause": cause})
            return {"error": message, "cause": cause}

        log_error(message)
        return {"error": message}

    def post_retrieval_action_result(self):
        return [self.update_or_create_lot(transaction) for transaction in self.transactions()]

    def transactions(self):
        for parsed_transaction_data in self.parsed_XML.iter("EO_TRANSACTION"):
            yield Transaction(parsed_transaction_data)

    def update_or_create_lot(self, transaction):
        def accomodate_attributes_to_do_update_lot_api(attributes):
            biofuel_code = attributes.pop("biofuel_code")
            attributes["biofuel_id"] = Biocarburant.objects.get(code=biofuel_code).id
            feedstock_code = attributes.pop("feedstock_code")
            attributes["feedstock_id"] = MatierePremiere.objects.get(code=feedstock_code).id

            attributes.pop("lot_status")

        try:
            no_user = None
            lot_attributes = transaction.to_lot_attributes()
            udb_transaction_id = transaction.udb_transaction_id()
            existing_lot = CarbureLot.objects.get(udb_transaction_id=udb_transaction_id)  # May throw ObjectNotExist

            accomodate_attributes_to_do_update_lot_api(lot_attributes)
            do_update_lot(no_user, existing_lot.carbure_supplier, existing_lot, lot_attributes)
            existing_lot.refresh_from_db()
            new_lot_created = False

        except ObjectDoesNotExist:
            supplier = Entity.objects.get(id=lot_attributes["carbure_supplier_id"])
            created_lot_data = create_lot(no_user, supplier, "UDB", lot_attributes)
            existing_lot = CarbureLot.objects.get(id=created_lot_data["id"])
            new_lot_created = True

        except UDBConversionError as e:
            return self.handle_error("Unable to convert UDB transaction into CarbuRe lot", e.message)

        except LotCreationFailure:
            return self.handle_error("Failed to create CarburRe lot from UDB transaction")

        except LotUpdateFailure as e:
            return self.handle_error(
                "Failed to update CarbuRe lot from UDB transaction data due to unmet integrity checks", e.data
            )

        except Exception as e:
            return self.handle_error("CarbuRe lot field update forbidden", str(e))

        existing_lot.lot_status = transaction.carbure_status()
        existing_lot.save()
        return {"newLotCreated": new_lot_created, "id": existing_lot.id}
