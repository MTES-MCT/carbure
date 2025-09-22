from edelivery.adapters.edelivery_adapter import send_SOAP_request
from edelivery.soap.responses import ListPendingMessagesResponse


class ListPendingMessages:
    def __init__(self, send_callback=send_SOAP_request):
        self.name = "listPendingMessages"
        self.send_callback = send_callback

    def payload(self):
        return """\
<soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope" xmlns:_1="http://eu.domibus.wsplugin/">
  <soap:Header/>
  <soap:Body>
    <_1:listPendingMessagesRequest></_1:listPendingMessagesRequest>
  </soap:Body>
</soap:Envelope>"""

    def perform(self):
        response = self.send_callback(action=self.name, payload=self.payload())
        return ListPendingMessagesResponse(response.text)
