from tempfile import SpooledTemporaryFile
from zipfile import ZipFile

from edelivery.adapters.base64_encoder import encode_binary

UDB_REQUEST_ENCAPSULATING_FILE_NAME = "udb-request.xml"


def zip_and_stream_udb_request(s):
    with SpooledTemporaryFile() as f:
        with ZipFile(f, "w") as zip_file:
            zip_file.writestr(UDB_REQUEST_ENCAPSULATING_FILE_NAME, s)

        f.seek(0)
        data = f.read()
        return encode_binary(data)
