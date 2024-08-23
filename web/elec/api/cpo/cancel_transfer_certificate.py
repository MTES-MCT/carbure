# /api/elec/provision-certificate/snapshot

import traceback

from django import forms
from django.db import transaction
from django.db.models import F
from django.views.decorators.http import require_POST

from core.common import ErrorResponse, SuccessResponse
from core.decorators import check_user_rights
from core.models import CarbureNotification, UserRights
from elec.models import ElecProvisionCertificate, ElecTransferCertificate
from elec.serializers.elec_transfer_certificate import ElecTransferCertificateSerializer


class ElecCancelError:
    ALREADY_ACCEPTED = "ALREADY_ACCEPTED"
    MALFORMED_PARAMS = "MALFORMED_PARAMS"
    CANCEL_FAILED = "CANCEL_FAILED"


class ElecTransferForm(forms.Form):
    entity_id = forms.IntegerField()
    transfer_certificate_id = forms.ModelChoiceField(queryset=ElecTransferCertificate.objects.all(), required=False)


@require_POST
@check_user_rights(role=[UserRights.ADMIN, UserRights.RW])
def cancel_transfer_certificate(request, *args, **kwargs):
    transfer_form = ElecTransferForm(request.POST)

    if not transfer_form.is_valid():
        return ErrorResponse(400, ElecCancelError.MALFORMED_PARAMS, transfer_form.errors)

    transfer_certificate = transfer_form.cleaned_data["transfer_certificate_id"]

    if transfer_certificate.status == ElecTransferCertificate.ACCEPTED:
        return ErrorResponse(400, ElecCancelError.ALREADY_ACCEPTED)

    with transaction.atomic():
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
                available_provision_certificates[current_certificate_idx].remaining_energy_amount = (
                    available_provision_certificates[current_certificate_idx].energy_amount
                )
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

        try:
            transfer_certificate.delete()
            CarbureNotification.objects.filter(meta__transfer_certificate_id=transfer_certificate.id).delete()
            return SuccessResponse(ElecTransferCertificateSerializer(transfer_certificate).data)
        except:
            traceback.print_exc()
            return ErrorResponse(400, ElecCancelError.CANCEL_FAILED)

    # TODO: Create verification function to preserve integrity of the certificates
