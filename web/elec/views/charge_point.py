from drf_spectacular.utils import OpenApiParameter, OpenApiTypes, extend_schema
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from core.models import Entity
from core.permissions import HasAdminRights
from elec.models import ElecChargePoint
from elec.serializers.elec_charge_point import ElecChargePointSerializer
from elec.services.replace_charge_point_id import replace_charge_point_id


class ReplaceChargePointIdSerializer(serializers.Serializer):
    cpo = serializers.PrimaryKeyRelatedField(queryset=Entity.objects.filter(entity_type=Entity.CPO))
    file = serializers.FileField()


@extend_schema(
    parameters=[
        OpenApiParameter(
            "entity_id",
            OpenApiTypes.INT,
            OpenApiParameter.QUERY,
            description="Entity ID",
            required=True,
        ),
    ],
)
class ChargePointViewSet(GenericViewSet):
    queryset = ElecChargePoint.objects.all()
    serializer_class = ElecChargePointSerializer
    pagination_class = None
    permission_classes = [HasAdminRights]

    @action(methods=["post"], detail=False, url_path="replace-ids", serializer_class=ReplaceChargePointIdSerializer)
    def replace_ids(self, request, *args, **kwargs):
        serializer = ReplaceChargePointIdSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        cpo = serializer.validated_data.get("cpo")
        file = serializer.validated_data.get("file")

        updated, deleted, not_found = replace_charge_point_id(cpo, file)

        return Response(
            {
                "updated": [cp.charge_point_id for cp in updated],
                "deleted": [cp.charge_point_id for cp in deleted],
                "not_found_on_tdg": not_found,
            }
        )
