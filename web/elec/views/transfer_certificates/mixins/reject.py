from django.db import transaction
from drf_spectacular.utils import OpenApiExample, OpenApiParameter, OpenApiTypes, extend_schema
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.response import Response

from elec.models import ElecTransferCertificate


class ElecTransferRejectSerializer(serializers.Serializer):
    comment = serializers.CharField()


class RejectActionMixin:
    @extend_schema(
        parameters=[
            OpenApiParameter(
                "entity_id",
                OpenApiTypes.INT,
                OpenApiParameter.QUERY,
                description="Entity ID",
                required=True,
            )
        ],
        examples=[
            OpenApiExample(
                "Example of assign response.",
                value={},
                request_only=False,
                response_only=True,
            ),
        ],
    )
    @action(methods=["POST"], detail=True, serializer_class=ElecTransferRejectSerializer)
    @transaction.atomic
    def reject(self, request, id=None):
        transfer_certificate = self.get_object()
        accept_form = ElecTransferRejectSerializer(data=request.data)
        accept_form.is_valid(raise_exception=True)

        if transfer_certificate.client != request.entity:
            raise Exception("NOT_ALLOWED")

        transfer_certificate.status = ElecTransferCertificate.REJECTED
        transfer_certificate.comment = accept_form.validated_data["comment"]
        transfer_certificate.save()

        return Response()
