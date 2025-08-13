from base64 import b64encode


def encode(b, binary=False):
    to_be_encoded = b if binary else bytes(b, "utf-8")
    return b64encode(to_be_encoded).decode("utf-8")


def encode_binary(b):
    return encode(b, binary=True)
