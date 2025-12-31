import datetime

from django.conf import settings
from django.db import transaction
from django.db.models import Sum
from drf_spectacular.utils import extend_schema
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.exceptions import ParseError
from rest_framework.response import Response

from core.models import Entity
from core.notifications import notify_elec_transfer_certificate
from elec.models import ElecProvisionCertificate, ElecTransferCertificate
from elec.serializers.elec_transfer_certificate import ElecTransferCertificateSerializer
from elec.services.readjustment_balance import get_readjustment_balance


class ElecTransferSerializer(serializers.Serializer):
    energy_amount = serializers.FloatField()
    client = serializers.PrimaryKeyRelatedField(
        queryset=Entity.objects.filter(entity_type=Entity.OPERATOR, has_elec=True), required=False
    )
    is_readjustment = serializers.BooleanField(default=False)


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

        # Parcourir les certificat de provision et vider au fur et à mesure tant que on a pas atteint la somme

        energy_pulled = 0
        energy_required = round(transfer_form.validated_data["energy_amount"], 3)
        client = transfer_form.validated_data.get("client")
        is_readjustment = transfer_form.validated_data.get("is_readjustment", False)

        missing_readjustment = 0
        if is_readjustment:
            client = Entity.objects.filter(name=settings.ELEC_READJUSTMENT_ENTITY).first()
            missing_readjustment = get_readjustment_balance(cpo=entity)

        if not client:
            raise ParseError("MISSING_CLIENT")

        available_provision_certificates = (
            ElecProvisionCertificate.objects.filter(cpo=entity)
            .exclude(remaining_energy_amount=0)
            .order_by("year", "quarter")
        )

        available_energy_dict = available_provision_certificates.aggregate(Sum("remaining_energy_amount"))
        available_energy = available_energy_dict["remaining_energy_amount__sum"] or 0

        if energy_required > available_energy:
            raise ParseError("NOT_ENOUGH_ENERGY")

        if is_readjustment and energy_required > missing_readjustment:
            raise ParseError("READJUSTING_TOO_MUCH")

        available_provision_certificates = list(available_provision_certificates)

        total_certificates = len(available_provision_certificates)
        current_certificate_idx = 0
        while (energy_pulled < energy_required) and (current_certificate_idx < total_certificates):
            curr_certif_energy = available_provision_certificates[current_certificate_idx].remaining_energy_amount

            # Le certificat n'a pas assez d'énergie
            missing_energy = energy_required - energy_pulled
            if curr_certif_energy <= missing_energy:
                available_provision_certificates[current_certificate_idx].remaining_energy_amount = 0
                energy_pulled += curr_certif_energy
            # Le certificat a assez d'énergie
            else:
                remaining_energy_amount = round(curr_certif_energy - missing_energy, 3)
                available_provision_certificates[current_certificate_idx].remaining_energy_amount = remaining_energy_amount
                energy_pulled = energy_required
            available_provision_certificates[current_certificate_idx].save()
            current_certificate_idx += 1

        status = ElecTransferCertificate.ACCEPTED if is_readjustment else ElecTransferCertificate.PENDING

        transfer_certificate = ElecTransferCertificate.objects.create(
            energy_amount=energy_required,
            client=client,
            supplier=entity,
            transfer_date=datetime.date.today(),
            status=status,
            is_readjustment=is_readjustment,
        )

        notify_elec_transfer_certificate(transfer_certificate)
        return Response(ElecTransferCertificateSerializer(transfer_certificate).data)
