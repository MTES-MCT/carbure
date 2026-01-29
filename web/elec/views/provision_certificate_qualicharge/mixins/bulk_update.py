from django.db import transaction
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from elec.models import ElecProvisionCertificateQualicharge
from elec.serializers.elec_provision_certificate_qualicharge import ProvisionCertificateUpdateBulkSerializer
from elec.services.qualicharge import create_provision_certificates_from_qualicharge


class BulkUpdateMixin:
    @extend_schema(
        operation_id="bulk_update_provision_certificates_qualicharge",
        description="Update multiple provision certificates in bulk (from Qualicharge)",
        request=ProvisionCertificateUpdateBulkSerializer,
        responses={
            status.HTTP_200_OK: OpenApiResponse(response={"status": "success", "errors": []}, description="Success message"),
        },
    )
    @action(
        detail=False,
        methods=["post"],
        url_path="bulk-update",
    )
    def bulk_update(self, request, *args, **kwargs):
        serializer = ProvisionCertificateUpdateBulkSerializer(data=request.data, many=False)
        serializer.is_valid(raise_exception=True)
        errors = []

        certificate_ids = serializer.validated_data.get("certificate_ids", [])
        validated_by = serializer.validated_data.get("validated_by")

        filters = {}
        if certificate_ids:
            filters = {"id__in": certificate_ids}
        else:
            if "cpo" in serializer.validated_data:
                filters["cpo__in"] = serializer.validated_data["cpo"]
            if "status" in serializer.validated_data:
                filters["validated_by__in"] = serializer.validated_data["status"]
            if "operating_unit" in serializer.validated_data:
                filters["operating_unit__in"] = serializer.validated_data["operating_unit"]
            if "station_id" in serializer.validated_data:
                filters["station_id__in"] = serializer.validated_data["station_id"]
            if "date_from" in serializer.validated_data:
                filters["date_from__in"] = serializer.validated_data["date_from"]

        qualicharge_certificates = self.get_queryset().filter(**filters)

        if not qualicharge_certificates.exists():
            return Response(
                {"status": "error", "errors": ["No valid certificates found"]}, status=status.HTTP_400_BAD_REQUEST
            )

        # Check if any of the certificates are already double validated
        for q_certificate in qualicharge_certificates:
            if q_certificate.validated_by == ElecProvisionCertificateQualicharge.BOTH:
                errors.append(
                    {
                        "certificate_id": q_certificate.id,
                        "error": "Certificate already double validated",
                    }
                )
                qualicharge_certificates = qualicharge_certificates.exclude(id=q_certificate.id)

        with transaction.atomic():
            CPO = ElecProvisionCertificateQualicharge.CPO
            DGEC = ElecProvisionCertificateQualicharge.DGEC
            BOTH = ElecProvisionCertificateQualicharge.BOTH
            NO_ONE = ElecProvisionCertificateQualicharge.NO_ONE

            qualicharge_certificates.filter(validated_by=NO_ONE).update(validated_by=validated_by)

            if validated_by == DGEC:
                qualicharge_certificates.filter(validated_by=CPO).update(validated_by=BOTH)

            elif validated_by == CPO:
                qualicharge_certificates.filter(validated_by=DGEC).update(validated_by=BOTH)

            create_provision_certificates_from_qualicharge(qualicharge_certificates)

        return Response({"status": "success", "errors": errors}, status=status.HTTP_200_OK)
