from os import environ

import requests

from edelivery.adapters.base64_encoder import encode


def request_headers():
    encoded_credentials = encode(f"""{environ["DOMIBUS_API_LOGIN"]}:{environ["DOMIBUS_API_PASSWORD"]}""")
    return {
        "Authorization": f"""Basic {encoded_credentials}""",
        "Content-Type": "text/xml",
    }


def request_URL(action):
    return f"""{environ["DOMIBUS_BASE_URL"]}/services/wsplugin/{action}"""


def send_SOAP_request(action, payload):
    return requests.post(request_URL(action), headers=request_headers(), data=payload)
