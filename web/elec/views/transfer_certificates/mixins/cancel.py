from django.db import transaction
from django.db.models import F
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import action
from rest_framework.exceptions import ParseError
from rest_framework.response import Response

from core.models import CarbureNotification
from elec.models import ElecProvisionCertificate, ElecTransferCertificate


class CancelActionMixin:
    @extend_schema(request=None, responses=None)
    @action(methods=["POST"], detail=True)
    @transaction.atomic
    def cancel(self, request, id=None):
        transfer_certificate = self.get_object()

        if transfer_certificate.status == ElecTransferCertificate.ACCEPTED:
            raise ParseError("ALREADY_ACCEPTED")

        # Parcourir les certificat de provision et vider au fur et à mesure tant que on a pas atteint la somme
        energy_filled = 0

        entity_id = transfer_certificate.supplier_id
        energy_required = transfer_certificate.energy_amount

        available_provision_certificates = (
            ElecProvisionCertificate.objects.filter(cpo_id=entity_id)
            .exclude(remaining_energy_amount=F("energy_amount"))
            .order_by("-year", "-quarter")
        )

        current_certificate_idx = 0
        total_certificates = len(available_provision_certificates)
        while (energy_filled < energy_required) and (current_certificate_idx < total_certificates):
            curr_missing_energy = (
                available_provision_certificates[current_certificate_idx].energy_amount
                - available_provision_certificates[current_certificate_idx].remaining_energy_amount
            )

            remaining_transfer_energy = energy_required - energy_filled
            # Le certificat n'a pas assez de place
            if curr_missing_energy < remaining_transfer_energy:
                available_provision_certificates[
                    current_certificate_idx
                ].remaining_energy_amount = available_provision_certificates[current_certificate_idx].energy_amount
                energy_filled += curr_missing_energy
            # Le certificat a assez de place
            else:
                available_provision_certificates[
                    current_certificate_idx
                ].remaining_energy_amount += remaining_transfer_energy
                energy_filled = energy_required
            available_provision_certificates[current_certificate_idx].remaining_energy_amount = round(
                available_provision_certificates[current_certificate_idx].remaining_energy_amount, 3
            )
            available_provision_certificates[current_certificate_idx].save()
            current_certificate_idx += 1

        transfer_certificate.delete()
        CarbureNotification.objects.filter(meta__transfer_certificate_id=transfer_certificate.id).delete()
        return Response()
