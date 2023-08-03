from django.http import JsonResponse, HttpResponse
from core.common import ErrorResponse, SuccessResponse
from core.decorators import check_rights, is_admin_or_external_admin
import boto3
import os
from doublecount.models import (
    DoubleCountingApplication,
)
from doublecount.serializers import DoubleCountingApplicationPartialSerializer
from doublecount.serializers import (
    DoubleCountingApplicationFullSerializerWithForeignKeys,
)
from core.xlsx_v3 import (
    export_dca,
)


class DoubleCountingApplicationError:
    MALFORMED_PARAMS = "MALFORMED_PARAMS"
    APPLICATION_NOT_FOUND = "APPLICATION_NOT_FOUND"


@is_admin_or_external_admin
def get_application(request, *args, **kwargs):
    application_id = request.GET.get("dca_id", None)
    export = request.GET.get("export", False)

    if not application_id:
        return ErrorResponse(400, DoubleCountingApplicationError.MALFORMED_PARAMS)
    try:
        application = DoubleCountingApplication.objects.get(id=application_id)
    except:
        return ErrorResponse(400, DoubleCountingApplicationError.APPLICATION_NOT_FOUND)

    serializer = DoubleCountingApplicationFullSerializerWithForeignKeys(application)
    if not export:
        return SuccessResponse(serializer.data)
    else:
        f = serializer.data["documents"][0]
        filename = f["file_name"]
        s3 = boto3.client(
            "s3",
            aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
            aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
            region_name=os.environ["AWS_S3_REGION_NAME"],
            endpoint_url=os.environ["AWS_S3_ENDPOINT_URL"],
            use_ssl=os.environ["AWS_S3_USE_SSL"],
        )
        filepath = "/tmp/%s" % filename
        s3filepath = "{year}/{entity}/{filename}".format(
            year=application.period_start.year, entity=application.producer.name, filename=filename
        )
        with open(filepath, "wb") as file:
            s3.download_fileobj(os.environ["AWS_DCDOCS_STORAGE_BUCKET_NAME"], s3filepath, file)
        with open(filepath, "rb") as file:
            data = file.read()
            ctype = "application/force-download"
            response = HttpResponse(content=data, content_type=ctype)
            response["Content-Disposition"] = 'attachment; filename="%s"' % (filename)
        return response
