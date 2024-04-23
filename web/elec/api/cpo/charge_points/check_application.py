from django.http import HttpRequest

from django.views.decorators.http import require_POST
from core.common import ErrorResponse, SuccessResponse
from core.decorators import check_user_rights
from core.models import Entity, UserRights
from elec.models.elec_charge_point_application import ElecChargePointApplication
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

    existing_charge_points = ChargePointRepository.get_registered_charge_points(entity)
    charge_points, errors = import_charge_point_excel(excel_file, existing_charge_points)

    new_charge_points = [cp["charge_point_id"] for cp in charge_points]
    replaced_charge_points = ChargePointRepository.get_replaced_charge_points(entity, new_charge_points)

    replaceable_applications = ElecChargePointApplication.objects.filter(
        cpo=entity, status__in=[ElecChargePointApplication.PENDING, ElecChargePointApplication.REJECTED]
    )

    data = {}
    data["file_name"] = excel_file.name
    data["charge_point_count"] = len(charge_points)
    data["errors"] = []
    data["error_count"] = 0
    data["replaced_count"] = replaced_charge_points.count()
    data["replaced"] = [cp.charge_point_id for cp in replaced_charge_points]
    data["pending_application_already_exists"] = replaceable_applications.count() > 0

    if len(errors) > 0:
        data["errors"] = errors
        data["error_count"] = len(data["errors"])
        return ErrorResponse(400, CheckChargePointApplicationError.VALIDATION_FAILED, data)

    if len(charge_points) == 0:
        data["errors"] = [{"error": "NO_CHARGE_POINT_DETECTED"}]
        data["error_count"] = 1
        return ErrorResponse(400, CheckChargePointApplicationError.NO_CHARGE_POINT_DETECTED, data)

    return SuccessResponse(data)
