from django.db import models, transaction
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from elec.models import ElecProvisionCertificate, ElecProvisionCertificateQualicharge
from elec.serializers.elec_provision_certificate_qualicharge import ProvisionCertificateUpdateBulkSerializer


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

        qualicharge_certificates = ElecProvisionCertificateQualicharge.objects.filter(id__in=certificate_ids)
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

            self._create_provision_certificates_from_qualicharge(qualicharge_certificates)

        return Response({"status": "success", "errors": errors}, status=status.HTTP_200_OK)

    @staticmethod
    def _create_provision_certificates_from_qualicharge(qualicharge_certificates):
        """
        Create provision certificates from Qualicharge data if validated_by is BOTH.
        Groups certificates by CPO, operating unit, and date range, then creates
        corresponding provision certificates.
        """
        BOTH = ElecProvisionCertificateQualicharge.BOTH

        # Group certificates and calculate total energy amounts
        grouped_certificates = (
            qualicharge_certificates.values("cpo", "operating_unit", "date_from", "date_to", "year")
            .filter(validated_by=BOTH)
            .annotate(total_energy_amount=models.Sum("energy_amount"))
            .order_by("cpo", "operating_unit", "date_from", "date_to")
        )

        provision_certificates_to_create = []
        for q_certificate in grouped_certificates:
            provision_certificates_to_create.append(
                ElecProvisionCertificate(
                    cpo_id=q_certificate["cpo"],
                    operating_unit=q_certificate["operating_unit"],
                    energy_amount=q_certificate["total_energy_amount"],
                    quarter=(q_certificate["date_from"].month - 1) // 3 + 1,
                    year=q_certificate["year"],
                    remaining_energy_amount=q_certificate["total_energy_amount"],
                    compensation=False,
                    source=ElecProvisionCertificate.QUALICHARGE,
                )
            )

        ElecProvisionCertificate.objects.bulk_create(provision_certificates_to_create)
