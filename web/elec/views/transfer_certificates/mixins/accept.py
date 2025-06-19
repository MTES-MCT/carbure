from django.db import transaction
from drf_spectacular.utils import extend_schema
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.response import Response

from elec.models import ElecTransferCertificate
from tiruert.services.elec_operation import ElecOperationService


class ElecTransferAcceptSerializer(serializers.Serializer):
    used_in_tiruert = serializers.CharField()
    consumption_date = serializers.DateField(required=False)


class AcceptActionMixin:
    @extend_schema(
        request=ElecTransferAcceptSerializer,
        responses=None,
    )
    @action(methods=["POST"], detail=True)
    @transaction.atomic
    def accept(self, request, id=None):
        transfer_certificate = self.get_object()
        accept_form = ElecTransferAcceptSerializer(data=request.data)
        accept_form.is_valid(raise_exception=True)

        used_in_tiruert = accept_form.validated_data.get("used_in_tiruert")
        consumption_date = accept_form.validated_data.get("consumption_date")

        if transfer_certificate.client != request.entity:
            raise Exception("NOT_ALLOWED")

        transfer_certificate.status = ElecTransferCertificate.ACCEPTED
        transfer_certificate.used_in_tiruert = used_in_tiruert == "true"
        if consumption_date:
            transfer_certificate.consumption_date = consumption_date
        transfer_certificate.save()

        ElecOperationService.update_operator_cpo_acquisition_operations(transfer_certificate.client)

        return Response()
