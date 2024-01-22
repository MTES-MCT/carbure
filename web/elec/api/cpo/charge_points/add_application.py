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


@require_POST
@check_user_rights(role=[UserRights.ADMIN, UserRights.RW], entity_type=[Entity.CPO])
def add_application(request: HttpRequest, entity: Entity):
    excel_file = request.FILES.get("file")

    if not excel_file:
        return ErrorResponse(400, AddChargePointApplicationError.MISSING_FILE)

    # @TODO actually list existing charge points to enable duplicate checks
    existing_charge_points = []

    charge_point_data, errors = import_charge_point_excel(excel_file, existing_charge_points)

    if len(errors) > 0:
        return ErrorResponse(400, AddChargePointApplicationError.VALIDATION_FAILED)

    with transaction.atomic():
        replaced_applications = ElecChargePointApplication.objects.filter(
            cpo=entity, status__in=[ElecChargePointApplication.PENDING, ElecChargePointApplication.REJECTED]
        )

        # delete older pending applications
        replaced_applications.delete()

        application = ElecChargePointApplication(cpo=entity)
        charge_points = [ElecChargePoint(**data, application=application, cpo=entity) for data in charge_point_data]

        application.save()
        ElecChargePoint.objects.bulk_create(charge_points)

    return SuccessResponse()
