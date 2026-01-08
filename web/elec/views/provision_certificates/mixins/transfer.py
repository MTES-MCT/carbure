import datetime

from django.conf import settings
from django.db import transaction
from drf_spectacular.utils import extend_schema
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.exceptions import ParseError
from rest_framework.response import Response

from core.models import Entity
from core.notifications import notify_elec_transfer_certificate
from elec.models import ElecTransferCertificate
from elec.serializers.elec_transfer_certificate import ElecTransferCertificateSerializer
from elec.services.certificate_balance import get_certificate_balance
from elec.services.readjustment_balance import get_readjustment_balance
from tiruert.serializers.fields import RoundedFloatField


class ElecTransferSerializer(serializers.Serializer):
    energy_amount = RoundedFloatField(min_value=0.01, decimal_places=2)
    client = serializers.PrimaryKeyRelatedField(
        queryset=Entity.objects.filter(entity_type=Entity.OPERATOR, has_elec=True), required=False
    )
    is_readjustment = serializers.BooleanField(default=False, required=False)


class TransferActionMixin:
    @extend_schema(
        request=ElecTransferSerializer,
        responses={200: ElecTransferCertificateSerializer},
    )
    @action(methods=["POST"], detail=False)
    @transaction.atomic
    def transfer(self, request):
        entity = request.entity

        transfer_form = ElecTransferSerializer(data=request.POST)
        transfer_form.is_valid(raise_exception=True)

        energy_amount = transfer_form.validated_data["energy_amount"]
        client = transfer_form.validated_data.get("client")
        is_readjustment = transfer_form.validated_data.get("is_readjustment", False)

        missing_readjustment = 0
        if is_readjustment:
            client = Entity.objects.filter(name=settings.ELEC_READJUSTMENT_ENTITY).first()
            missing_readjustment = get_readjustment_balance(cpo=entity)

        if not client:
            raise ParseError("MISSING_CLIENT")

        if energy_amount > get_certificate_balance(cpo=entity):
            raise ParseError("NOT_ENOUGH_ENERGY")

        if is_readjustment and energy_amount > missing_readjustment:
            raise ParseError("READJUSTING_TOO_MUCH")

        status = ElecTransferCertificate.PENDING
        if is_readjustment:
            status = ElecTransferCertificate.ACCEPTED

        transfer_certificate = ElecTransferCertificate.objects.create(
            energy_amount=energy_amount,
            client=client,
            supplier=entity,
            transfer_date=datetime.date.today(),
            status=status,
            is_readjustment=is_readjustment,
        )

        notify_elec_transfer_certificate(transfer_certificate)
        return Response(ElecTransferCertificateSerializer(transfer_certificate).data)
