from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from core.models import Entity
from core.serializers import EntityPreviewSerializer
from elec.models import ElecProvisionCertificateQualicharge
from elec.serializers.elec_provision_certificate_qualicharge import BulkTransferQualichargeSerializer


class BulkTransferMixin:
    @extend_schema(
        operation_id="transfer_targets_provision_certificates_qualicharge",
        description="List CPOs authorized to receive volume transfers (those with parent_entity = current entity)",
        responses={
            status.HTTP_200_OK: OpenApiResponse(
                response=EntityPreviewSerializer(many=True),
                description="List of CPOs authorized to receive volume transfers",
            ),
        },
    )
    @action(
        detail=False,
        methods=["get"],
        url_path="transfer-targets",
        pagination_class=None,
    )
    def transfer_targets(self, request, *args, **kwargs):
        target_cpos = Entity.objects.filter(parent_entity=request.entity, entity_type=Entity.CPO)
        serializer = EntityPreviewSerializer(target_cpos, many=True)
        return Response(serializer.data)

    @extend_schema(
        operation_id="bulk_transfer_provision_certificates_qualicharge",
        description="Transfer non-double-validated volumes to another CPO (target must have parent_entity = current entity)",
        request=BulkTransferQualichargeSerializer,
        responses={
            status.HTTP_200_OK: OpenApiResponse(
                response={"status": "success", "transferred_count": 0},
                description="Success message with count of transferred certificates",
            ),
        },
    )
    @action(
        detail=False,
        methods=["post"],
        url_path="bulk-transfer",
    )
    def bulk_transfer(self, request, *args, **kwargs):
        serializer = BulkTransferQualichargeSerializer(data=request.data, many=False, context={"request": request})
        serializer.is_valid(raise_exception=True)

        target_cpo = serializer.validated_data["target_cpo"]
        operating_unit = serializer.validated_data["operating_unit"]

        queryset = self.get_queryset().exclude(validated_by=ElecProvisionCertificateQualicharge.BOTH)
        queryset = queryset.filter(operating_unit__in=operating_unit)

        if not queryset.exists():
            return Response(
                {"status": "error", "errors": ["No transferable certificates found"]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        queryset.update(cpo=target_cpo, validated_by=ElecProvisionCertificateQualicharge.NO_ONE)

        return Response({"status": "success"}, status=status.HTTP_200_OK)
