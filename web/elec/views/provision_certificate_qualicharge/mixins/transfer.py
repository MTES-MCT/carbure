from django.db import transaction
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from elec.serializers.elec_provision_certificate_qualicharge import TransferCertificateSerializer


class TransferMixin:
    @extend_schema(
        operation_id="transfer_provision_certificate_qualicharge",
        description="Transfer a Qualicharge provision certificate to another entity with the same registration ID",
        request=TransferCertificateSerializer,
        responses={
            status.HTTP_200_OK: OpenApiResponse(
                response={"status": "success", "message": "Certificate transferred successfully"},
                description="Success message",
            ),
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(
                response={"status": "error", "error": "Error message"}, description="Error message"
            ),
        },
    )
    @action(
        detail=False,
        methods=["post"],
        url_path="transfer",
    )
    def transfer(self, request, *args, **kwargs):
        serializer = TransferCertificateSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        certificate = serializer.validated_data["certificate"]
        target_entity = serializer.validated_data["target_entity"]

        with transaction.atomic():
            certificate.cpo = target_entity
            certificate.save(update_fields=["cpo"])

        return Response(status=status.HTTP_200_OK)
