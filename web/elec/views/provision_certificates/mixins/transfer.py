import datetime

from django.db import transaction
from django.db.models import Sum
from drf_spectacular.utils import extend_schema
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.response import Response

from core.models import Entity
from core.notifications import notify_elec_transfer_certificate
from elec.models import ElecProvisionCertificate, ElecTransferCertificate
from elec.serializers.elec_transfer_certificate import ElecTransferCertificateSerializer


class ElecTransferSerializer(serializers.Serializer):
    energy_amount = serializers.FloatField()
    client = serializers.PrimaryKeyRelatedField(queryset=Entity.objects.filter(entity_type=Entity.OPERATOR, has_elec=True))


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
        client = transfer_form.validated_data["client"]

        available_provision_certificates = (
            ElecProvisionCertificate.objects.filter(cpo=entity)
            .exclude(remaining_energy_amount=0)
            .order_by("year", "quarter")
        )

        available_energy = available_provision_certificates.aggregate(Sum("remaining_energy_amount"))
        if available_energy["remaining_energy_amount__sum"] < energy_required:
            raise Exception("NOT_ENOUGH_ENERGY")

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

        transfer_certificate = ElecTransferCertificate.objects.create(
            energy_amount=energy_required,
            client=client,
            supplier=entity,
            transfer_date=datetime.date.today(),
            status=ElecTransferCertificate.PENDING,
        )

        notify_elec_transfer_certificate(transfer_certificate)
        return Response(ElecTransferCertificateSerializer(transfer_certificate).data)
