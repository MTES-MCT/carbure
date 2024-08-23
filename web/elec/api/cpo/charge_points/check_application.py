from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_POST
from pandas.core.frame import DataFrame

from core.common import ErrorResponse, SuccessResponse
from core.decorators import check_user_rights
from core.models import Entity, UserRights
from elec.repositories.charge_point_repository import ChargePointRepository
from elec.services.import_charge_point_excel import import_charge_point_excel


class CheckChargePointApplicationError:
    MISSING_FILE = "MISSING_FILE"
    VALIDATION_FAILED = "VALIDATION_FAILED"
    NO_CHARGE_POINT_DETECTED = "NO_CHARGE_POINT_DETECTED"


@require_POST
@check_user_rights(role=[UserRights.ADMIN, UserRights.RW], entity_type=[Entity.CPO])
def check_application(request: HttpRequest, entity):
    excel_file = request.FILES.get("file")

    if not excel_file:
        return ErrorResponse(400, CheckChargePointApplicationError.MISSING_FILE)

    charge_points, errors, original = import_charge_point_excel(excel_file)
    new_charge_points = [cp["charge_point_id"] for cp in charge_points]
    replaced_charge_points = ChargePointRepository.get_replaced_charge_points(entity, new_charge_points)
    replaced_charge_points_by_id = replaced_charge_points.values_list("charge_point_id", flat=True)

    duplicates = {}
    if isinstance(original, DataFrame):
        for __, row in original.iterrows():
            charge_point_id = row["charge_point_id"]
            if charge_point_id in replaced_charge_points_by_id:
                duplicates[charge_point_id] = row["line"]

    data = {}
    data["file_name"] = excel_file.name
    data["charge_point_count"] = len(charge_points) - len(duplicates)
    data["errors"] = []
    data["error_count"] = 0

    if duplicates:
        for charge_point_id, line in duplicates.items():
            errors.append(
                {
                    "error": "INVALID_DATA",
                    "line": line,
                    "meta": {"charge_point_id": [_(f"Le point de recharge {charge_point_id} existe déjà")]},
                }
            )
        data["errors"] = errors
        data["error_count"] = len(errors)
        return ErrorResponse(400, CheckChargePointApplicationError.VALIDATION_FAILED, data)

    if len(errors) > 0:
        data["errors"] = errors
        data["error_count"] = len(data["errors"])
        return ErrorResponse(400, CheckChargePointApplicationError.VALIDATION_FAILED, data)

    if len(charge_points) == 0:
        data["errors"] = [{"error": "NO_CHARGE_POINT_DETECTED"}]
        data["error_count"] = 1
        return ErrorResponse(400, CheckChargePointApplicationError.NO_CHARGE_POINT_DETECTED, data)

    return SuccessResponse(data)
