from django.db import transaction
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from elec.models import ElecProvisionCertificateQualicharge
from elec.serializers.elec_provision_certificate_qualicharge import ProvisionCertificateBulkSerializer
from elec.services.qualicharge import handle_bulk_create_validation_errors, process_certificates_batch


class BulkCreateMixin:
    @extend_schema(
        operation_id="bulk_create_provision_certificates_qualicharge",
        description="Create multiple provision certificates in bulk (from Qualicharge)",
        request=ProvisionCertificateBulkSerializer,
        responses={
            status.HTTP_201_CREATED: OpenApiResponse(
                response={"status": "success", "errors": []}, description="Success message"
            ),
        },
    )
    @action(
        detail=False,
        methods=["post"],
        url_path="bulk-create",
    )
    def bulk_create(self, request, *args, **kwargs):
        serializer = ProvisionCertificateBulkSerializer(data=request.data, many=True)

        if not serializer.is_valid():
            handle_bulk_create_validation_errors(request, serializer)

        # Fetch already double-validated certificates to avoid duplicates
        double_validated = self._get_double_validated_certificates()

        with transaction.atomic():
            errors = process_certificates_batch(serializer.validated_data, double_validated)

            # If business errors occurred, rollback the transaction
            if errors:
                transaction.set_rollback(True)
                return Response({"status": "error", "errors": errors}, status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_201_CREATED)

    def _get_double_validated_certificates(self):
        """Fetch already double-validated certificates to prevent duplicates."""
        return set(
            ElecProvisionCertificateQualicharge.objects.filter(
                validated_by=ElecProvisionCertificateQualicharge.BOTH
            ).values_list("station_id", "date_from", "date_to")
        )
