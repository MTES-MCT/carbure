from adapters.logger import log_error
from edelivery.ebms.request_responses import BaseRequestResponse


class InvalidRequestErrorResponse(BaseRequestResponse):
    def error_message(self):
        return self.parsed_XML.find("./RESPONSE_HEADER").attrib["OBSERVATION"]

    def post_retrieval_action_result(self):
        error_message = self.error_message()
        log_error("Invalid request", {"error": error_message})
        return {"error": "Invalid request", "message": error_message}


class NotFoundErrorResponse(BaseRequestResponse):
    def post_retrieval_action_result(self):
        log_error("UDB Search returned no result")
        return {"error": "Not found"}


class UnknownStatusErrorResponse(BaseRequestResponse):
    def status(self):
        return self.parsed_XML.find("./RESPONSE_HEADER").attrib["STATUS"]

    def post_retrieval_action_result(self):
        status = self.status()
        log_error("Received UDB response with unknown status", {"status": status})
        return {"error": "Unknown response status", "status": status}
