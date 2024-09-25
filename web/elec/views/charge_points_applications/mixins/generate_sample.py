from django.shortcuts import get_object_or_404
from rest_framework import serializers, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from elec.models import ElecChargePointApplication
from elec.models.elec_audit_charge_point import ElecAuditChargePoint
from elec.models.elec_audit_sample import ElecAuditSample
from elec.serializers.elec_charge_point import ElecChargePointSampleSerializer
from elec.services.extract_audit_sample import extract_audit_sample


class GenerateSampleSerializer(serializers.Serializer):
    percentage = serializers.IntegerField(required=False)


class GenereateSampleActionMixin:
    @action(methods=["post"], detail=True)
    def generate_sample(self, request, id=None):
        application = get_object_or_404(ElecChargePointApplication, id=id)

        serializer = GenerateSampleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        percentage = serializer.validated_data["percentage"]
        application_audits = ElecAuditSample.objects.filter(charge_point_application=application)

        # delete any pending audit sample for this application
        application_audits.filter(status=ElecAuditSample.IN_PROGRESS).delete()

        # send an error if the audit is already in progress or done
        if application_audits.filter(status=ElecAuditSample.AUDITED).count() > 0:
            raise ValidationError({"message": "ALREADY_AUDITED"})

        charge_points = (
            application.elec_charge_points.filter(cpo=application.cpo, is_deleted=False)
            .order_by("station_id", "charge_point_id")
            .select_related("cpo")
        )

        charge_point_sample = extract_audit_sample(charge_points, percentage)

        new_audit = ElecAuditSample.objects.create(
            charge_point_application=application,
            cpo=application.cpo,
            percentage=percentage * 100,
        )

        charge_point_audits = [
            ElecAuditChargePoint(audit_sample=new_audit, charge_point=charge_point) for charge_point in charge_point_sample
        ]
        ElecAuditChargePoint.objects.bulk_create(charge_point_audits)

        return Response(
            {
                "application_id": application.id,
                "percentage": new_audit.percentage,
                "charge_points": ElecChargePointSampleSerializer(charge_point_sample, many=True).data,
            },
            status=status.HTTP_200_OK,
        )
