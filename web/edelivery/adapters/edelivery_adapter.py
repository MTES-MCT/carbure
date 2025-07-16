from os import environ

import requests

from edelivery.adapters.base64_encoder import encode


def request_headers():
    encoded_credentials = encode(f"""{environ["DOMIBUS_API_LOGIN"]}:{environ["DOMIBUS_API_PASSWORD"]}""")
    return {
        "Authorization": f"""Basic {encoded_credentials}""",
        "Content-Type": "text/xml",
    }


def request_URL():
    return f"""{environ["DOMIBUS_BASE_URL"]}/services/wsplugin/submitMessage"""


def send_SOAP_request(envelope):
    requests.post(request_URL(), headers=request_headers(), data=envelope.payload())
