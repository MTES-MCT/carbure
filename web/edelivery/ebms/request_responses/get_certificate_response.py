from .base_request_response import BaseRequestResponse


class GetCertificateResponse(BaseRequestResponse):
    def post_retrieval_action_result(self):
        return self.payload
