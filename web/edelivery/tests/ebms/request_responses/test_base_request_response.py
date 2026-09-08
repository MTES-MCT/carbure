from unittest import TestCase

from edelivery.ebms.request_responses.base_request_response import BaseRequestResponse


class BaseRequestResponseTest(TestCase):
    def test_returns_default_success_confirmation_message(self):
        response = BaseRequestResponse("<SOME_TAG />")
        result = response.post_retrieval_action_result()
        self.assertEqual({"responseStatus": "success"}, result)
