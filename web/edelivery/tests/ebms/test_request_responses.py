from unittest import TestCase

from edelivery.ebms.request_responses import BaseRequestResponse


class BaseRequestResponseTest(TestCase):
    def payload(_, request_id):
        return f"""\
<?xml version="1.0" encoding="UTF-8"?>
<udb:GetSourcingContactByIDResponse
  xmlns:udb="http://udb.ener.ec.europa.eu/services/udbModelService/udbService/v1">
  <RESPONSE_HEADER REQUEST_ID="{request_id}"/>
  <!-- … -->
</udb:GetSourcingContactByIDResponse>"""

    def test_extract_request_id(self):
        response = BaseRequestResponse(self.payload("12345"))
        self.assertEqual("12345", response.request_id())
