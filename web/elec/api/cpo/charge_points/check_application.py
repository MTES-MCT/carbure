import traceback
from django.http import HttpRequest

from django.views.decorators.http import require_POST
from core.common import ErrorResponse, SuccessResponse
from core.decorators import check_user_rights
from core.models import Entity, UserRights
from elec.services.import_charge_point_excel import import_charge_point_excel


class CheckChargePointApplicationError:
    MISSING_FILE = "MISSING_FILE"
    CPO_ONLY = "CPO_ONLY"
    VALIDATION_FAILED = "VALIDATION_FAILED"
    FAILED = "FAILED"


@require_POST
@check_user_rights(role=[UserRights.ADMIN, UserRights.RW], entity_type=[Entity.CPO])
def check_application(request: HttpRequest):
    excel_file = request.FILES.get("file")

    if not excel_file:
        return ErrorResponse(400, CheckChargePointApplicationError.MISSING_FILE)

    try:
        charge_points, errors = import_charge_point_excel(excel_file)

        data = {}
        data["file_name"] = excel_file.name
        data["charging_point_count"] = len(charge_points)
        data["errors"] = []
        data["error_count"] = 0

        if len(errors) > 0:
            data["errors"] = errors
            data["error_count"] = len(data["errors"])
            return ErrorResponse(400, CheckChargePointApplicationError.VALIDATION_FAILED, data)

        return SuccessResponse(data)

    except Exception:
        traceback.print_exc()
        return ErrorResponse(400, CheckChargePointApplicationError.FAILED)
