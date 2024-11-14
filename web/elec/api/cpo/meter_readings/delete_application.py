from django.http import HttpRequest
from django.views.decorators.http import require_POST
from rest_framework import serializers

from core.common import ErrorResponse, SuccessResponse
from core.decorators import check_user_rights
from core.models import Entity, UserRights
from elec.models import ElecMeterReadingApplication


class DeleteElecMeterReadingApplicationSerializer(serializers.Serializer):
    id = serializers.PrimaryKeyRelatedField(queryset=ElecMeterReadingApplication.objects.all())


class RemoveElecMeterReadingApplicationError:
    WRONG_ENTITY = "WRONG_ENTITY"
    APPLICATION_NOT_PENDING = "APPLICATION_NOT_PENDING"


@require_POST
@check_user_rights(role=[UserRights.ADMIN, UserRights.RW], entity_type=[Entity.CPO])
def delete_application(request: HttpRequest, entity: Entity):
    serializer = DeleteElecMeterReadingApplicationSerializer(data=request.POST)
    serializer.is_valid(raise_exception=True)

    application = serializer.validated_data["id"]
    if application.cpo != entity:
        return ErrorResponse(400, RemoveElecMeterReadingApplicationError.WRONG_ENTITY)

    if application.status != ElecMeterReadingApplication.PENDING:
        return ErrorResponse(400, RemoveElecMeterReadingApplicationError.APPLICATION_NOT_PENDING)

    elec_meter_readings = application.elec_meter_readings.all()
    # delete all meter readings
    elec_meter_readings.delete()
    # delete meter readings application
    application.delete()

    return SuccessResponse()
