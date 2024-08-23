from django.db import transaction
from django.http import HttpRequest
from django.views.decorators.http import require_POST
from pandas.core.frame import DataFrame

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

    charge_point_data, errors, original = import_charge_point_excel(excel_file)

    if len(errors) > 0:
        return ErrorResponse(400, AddChargePointApplicationError.VALIDATION_FAILED)

    if len(charge_point_data) == 0:
        return ErrorResponse(400, AddChargePointApplicationError.NO_CHARGE_POINT_DETECTED)

    new_charge_points = [cp["charge_point_id"] for cp in charge_point_data]
    replaced_charge_points = ChargePointRepository.get_replaced_charge_points(entity, new_charge_points)
    replaced_charge_points_by_id = replaced_charge_points.values_list("charge_point_id", flat=True)

    duplicate = False
    if isinstance(original, DataFrame):
        for _, row in original.iterrows():
            charge_point_id = row["charge_point_id"]
            if charge_point_id in replaced_charge_points_by_id:
                duplicate = True
                break

    if duplicate:
        return ErrorResponse(400, AddChargePointApplicationError.VALIDATION_FAILED)

    with transaction.atomic():
        application = ElecChargePointApplication(cpo=entity)

        charge_points = [
            ElecChargePoint(
                **data,
                application=application,
                cpo=entity,
            )
            for data in charge_point_data
        ]

        application.save()
        ElecChargePoint.objects.bulk_create(charge_points)

    return SuccessResponse()
