from io import BytesIO
from tempfile import SpooledTemporaryFile, TemporaryDirectory
from zipfile import ZipFile

from edelivery.adapters.base64_encoder import decode, encode_binary

UDB_REQUEST_ENCAPSULATING_FILE_NAME = "udb-request.xml"
UDB_RESPONSE_ENCAPSULATING_FILE_NAME = "udb-response.xml"


def zip_and_stream_udb_request(s):
    with SpooledTemporaryFile() as f:
        with ZipFile(f, "w") as zip_file:
            zip_file.writestr(UDB_REQUEST_ENCAPSULATING_FILE_NAME, s)

        f.seek(0)
        data = f.read()
        return encode_binary(data)


def unzip_base64_encoded_stream(s):
    buffer = decode(s)
    zip_archive = BytesIO(buffer)
    with TemporaryDirectory() as directory:
        with ZipFile(zip_archive) as z:
            unzipped_file_path = z.extract(UDB_RESPONSE_ENCAPSULATING_FILE_NAME, directory)
        with open(unzipped_file_path, "r") as unzipped_file:
            return unzipped_file.read()
