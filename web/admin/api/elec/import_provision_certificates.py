import traceback
from core.common import ErrorResponse, SuccessResponse
from core.decorators import check_admin_rights
from core.models import ExternalAdminRights
from elec.models.elec_provision_certificate import ElecProvisionCertificate
import pandas as pd


class CertificateImportError:
    MISSING_FILE = "MISSING_FILE"
    CSV_WRITE_ERROR = "CSV_WRITE_ERROR"
    DB_INSERTION_ERROR = "DB_INSERTION_ERROR"
    CSV_PARSE_ERROR = "CSV_PARSE_ERROR"


@check_admin_rights(allow_external=[ExternalAdminRights.ELEC])
def import_provision_certificate_excel(request):
    file = request.FILES.get("file")
    if file is None:
        return ErrorResponse(400, CertificateImportError.MISSING_FILE, "Missing File")

    # Read CSV and insert data into SQL database
    try:
        filename = "/tmp/transfer_certificates.csv"
        with open(filename, "wb+") as destination:
            for chunk in file.chunks():
                destination.write(chunk)
    except:
        return ErrorResponse(400, CertificateImportError.CSV_WRITE_ERROR)

    try:
        certificate_df = pd.read_csv(filename)
    except:
        return ErrorResponse(400, CertificateImportError.CSV_PARSE_ERROR)

    certificate_model_instances = [
        ElecProvisionCertificate(
            cpo_id=record["cpo_id"],
            quarter=record["quarter"],
            year=record["year"],
            operating_unit=record["operating_unit"],
            energy_amount=record["energy_amount"],
            remaining_energy_amount=record["energy_amount"],
        )
        for record in certificate_df.to_dict("records")
    ]

    try:
        ElecProvisionCertificate.objects.bulk_create(certificate_model_instances)
    except:
        traceback.print_exc()
        return ErrorResponse(400, CertificateImportError.DB_INSERTION_ERROR, "Error during data insert")

    return SuccessResponse()
