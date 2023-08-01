from django.http import JsonResponse, HttpResponse
from core.common import ErrorResponse, SuccessResponse
from core.decorators import check_rights, is_admin_or_external_admin

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
    # if not export:
    # return JsonResponse({"status": "success", "data": serializer.data})
    return SuccessResponse(serializer.data)
    # else:
    #     file_location = export_dca(application)
    #     with open(file_location, "rb") as excel:
    #         data = excel.read()
    #         ctype = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    #         response = HttpResponse(content=data, content_type=ctype)
    #         response["Content-Disposition"] = 'attachment; filename="%s"' % (file_location)
    #     return response
