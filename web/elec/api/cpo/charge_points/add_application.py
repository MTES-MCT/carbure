import traceback
from django.http import HttpRequest
from django.db import transaction
from django.views.decorators.http import require_POST
from core.common import ErrorResponse, SuccessResponse
from core.decorators import check_user_rights
from core.models import Entity, UserRights
from elec.models.elec_charge_point import ElecChargePoint
from elec.models.elec_charge_point_application import ElecChargePointApplication
from elec.services.import_charge_point_excel import import_charge_point_excel


class AddChargePointApplicationError:
    MISSING_FILE = "MISSING_FILE"
    VALIDATION_FAILED = "VALIDATION_FAILED"
    FAILED = "FAILED"


@require_POST
@check_user_rights(role=[UserRights.ADMIN, UserRights.RW], entity_type=[Entity.CPO])
def add_application(request: HttpRequest, entity: Entity):
    excel_file = request.FILES.get("file")

    if not excel_file:
        return ErrorResponse(400, AddChargePointApplicationError.MISSING_FILE)

    try:
        charge_point_data, errors = import_charge_point_excel(excel_file)

        if len(errors) > 0:
            return ErrorResponse(400, AddChargePointApplicationError.VALIDATION_FAILED)

        with transaction.atomic():
            application = ElecChargePointApplication(cpo=entity)
            charge_points = [ElecChargePoint(**data, application=application, cpo=entity) for data in charge_point_data]

            application.save()
            ElecChargePoint.objects.bulk_create(charge_points)

        return SuccessResponse()

    except Exception:
        traceback.print_exc()
        return ErrorResponse(400, AddChargePointApplicationError.FAILED)
