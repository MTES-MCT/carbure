from django.http import HttpRequest
from django.db import transaction
from django.views.decorators.http import require_POST
from core.common import ErrorResponse, SuccessResponse
from core.decorators import check_user_rights
from core.models import Entity, UserRights
from elec.models.elec_charge_point import ElecChargePoint
from elec.models.elec_charge_point_application import ElecChargePointApplication
from elec.repositories.charge_point_repository import ChargePointRepository
from elec.services.import_charge_point_excel import import_charge_point_excel


class AddChargePointApplicationError:
    MISSING_FILE = "MISSING_FILE"
    VALIDATION_FAILED = "VALIDATION_FAILED"
    NO_CHARGE_POINT_DETECTED = "NO_CHARGE_POINT_DETECTED"


@require_POST
@check_user_rights(role=[UserRights.ADMIN, UserRights.RW], entity_type=[Entity.CPO])
def add_application(request: HttpRequest, entity: Entity):
    excel_file = request.FILES.get("file")

    if not excel_file:
        return ErrorResponse(400, AddChargePointApplicationError.MISSING_FILE)

    existing_charge_points = ChargePointRepository.get_registered_charge_points(entity)
    charge_point_data, errors = import_charge_point_excel(excel_file, existing_charge_points)

    if len(errors) > 0:
        return ErrorResponse(400, AddChargePointApplicationError.VALIDATION_FAILED)

    if len(charge_point_data) == 0:
        return ErrorResponse(400, AddChargePointApplicationError.NO_CHARGE_POINT_DETECTED)

    new_charge_points = [cp["charge_point_id"] for cp in charge_point_data]
    replaced_charge_points = ChargePointRepository.get_replaced_charge_points(entity, new_charge_points)
    replaced_charge_points_by_id = {cp.charge_point_id: cp for cp in replaced_charge_points}

    with transaction.atomic():
        replaced_applications = ElecChargePointApplication.objects.filter(
            cpo=entity, status__in=[ElecChargePointApplication.PENDING, ElecChargePointApplication.REJECTED]
        )

        # delete older pending applications
        replaced_applications.delete()

        application = ElecChargePointApplication(cpo=entity)

        charge_points = [
            ElecChargePoint(
                **data,
                application=application,
                cpo=entity,
                previous_version=replaced_charge_points_by_id.get(data["charge_point_id"])
            )
            for data in charge_point_data
        ]

        application.save()
        ElecChargePoint.objects.bulk_create(charge_points)

    return SuccessResponse()
