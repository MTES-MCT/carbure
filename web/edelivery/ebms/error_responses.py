from adapters.logger import log_error
from edelivery.ebms.request_responses import BaseRequestResponse


class BaseErrorResponse(BaseRequestResponse):
    def __init__(self, payload, description):
        super().__init__(payload)
        self.description = description

    def error_message(self):
        response_header_attributes = self.parsed_XML.find("./RESPONSE_HEADER").attrib
        return response_header_attributes.get("OBSERVATION", None)

    def post_retrieval_action_result(self):
        additional_infos_to_log = None
        additional_infos_to_return = {}
        error_message = self.error_message()
        if error_message is not None:
            additional_infos_to_log = {"error": error_message}
            additional_infos_to_return = {"message": error_message}

        log_error(self.description, additional_infos_to_log)
        return {"error": self.description, **additional_infos_to_return}


class FailedErrorResponse(BaseErrorResponse):
    def __init__(self, payload):
        super().__init__(payload, "UDB failed to respond")


class InvalidRequestErrorResponse(BaseErrorResponse):
    def __init__(self, payload):
        super().__init__(payload, "Invalid request")


class NotFoundErrorResponse(BaseErrorResponse):
    def __init__(self, payload):
        super().__init__(payload, "UDB Search returned no result")


class UnknownStatusErrorResponse(BaseRequestResponse):
    def status(self):
        return self.parsed_XML.find("./RESPONSE_HEADER").attrib["STATUS"]

    def post_retrieval_action_result(self):
        status = self.status()
        log_error("Received UDB response with unknown status", {"status": status})
        return {"error": "Received UDB response with unknown status", "status": status}
