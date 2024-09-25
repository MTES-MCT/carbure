from rest_framework import serializers, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from core.excel import ExcelResponse
from elec.serializers.elec_audit_charge_point import ElecAuditChargePointSerializer
from elec.services.export_audited_charge_points_sample_to_excel import (
    export_audited_charge_points_sample_to_excel,
)


class GetSampleSerializer(serializers.Serializer):
    export = serializers.BooleanField(required=False)


class GetSampleActionMixin:
    @action(methods=["get"], detail=True)
    def get_sample(self, request, id=None):
        application = self.get_object()

        serializer = GetSampleSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        export = serializer.validated_data["export"]
        audit_sample = application.audit_sample.first()

        if not audit_sample:
            raise ValidationError({"message": "NO_SAMPLE_FOUND"})

        audited_charge_points = audit_sample.audited_charge_points.all().select_related("charge_point")

        if export:
            excel_file = export_audited_charge_points_sample_to_excel(audited_charge_points, audit_sample.cpo)
            return ExcelResponse(excel_file)

        return Response(
            ElecAuditChargePointSerializer(audited_charge_points, many=True).data,
            status=status.HTTP_200_OK,
        )
