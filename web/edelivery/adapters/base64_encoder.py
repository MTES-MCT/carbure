import base64


def encode(s):
    return base64.b64encode(bytes(s, "utf-8")).decode("utf-8")
