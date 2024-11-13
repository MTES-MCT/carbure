from django.http import HttpRequest
from django.views.decorators.http import require_POST
from rest_framework import serializers

from core.common import ErrorResponse, SuccessResponse
from core.decorators import check_user_rights
from core.models import Entity, UserRights
from elec.models import ElecChargePointApplication


class DeleteChargePointApplicationSerializer(serializers.Serializer):
    id = serializers.PrimaryKeyRelatedField(queryset=ElecChargePointApplication.objects.all())


class RemoveChargePointApplicationError:
    WRONG_ENTITY = "WRONG_ENTITY"
    APPLICATION_NOT_PENDING = "APPLICATION_NOT_PENDING"


@require_POST
@check_user_rights(role=[UserRights.ADMIN, UserRights.RW], entity_type=[Entity.CPO])
def delete_application(request: HttpRequest, entity: Entity):
    serializer = DeleteChargePointApplicationSerializer(data=request.POST)
    serializer.is_valid(raise_exception=True)

    application = serializer.validated_data["id"]
    if application.cpo != entity:
        return ErrorResponse(400, RemoveChargePointApplicationError.WRONG_ENTITY)

    if application.status != ElecChargePointApplication.PENDING:
        return ErrorResponse(400, RemoveChargePointApplicationError.APPLICATION_NOT_PENDING)

    cp = application.elec_charge_points.all()
    for cp_ in cp:
        # delete all elec_metes
        em = cp_.elec_meters.all()
        em.delete()
    # delete all charge points
    cp.delete()
    # delete charge point application
    application.delete()

    return SuccessResponse()
