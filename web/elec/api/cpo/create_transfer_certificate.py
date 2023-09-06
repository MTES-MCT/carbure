# /api/v5/elec/provision-certificate/snapshot

import traceback
import datetime

from django import forms
from django.db.models import Sum
from django.db import transaction
from django.views.decorators.http import require_POST
from core.common import SuccessResponse, ErrorResponse
from core.decorators import check_user_rights
from core.models import Entity, UserRights
from core.notifications import notify_elec_transfer_certificate
from elec.models import ElecProvisionCertificate, ElecTransferCertificate

from elec.serializers.elec_transfer_certificate import ElecTransferCertificateSerializer


class ElecTransferError:
    MALFORMED_PARAMS = "MALFORMED_PARAMS"
    CREATION_FAILED = "CREATION_FAILED"
    NOT_ENOUGH_ENERGY = "NOT_ENOUGH_ENERGY"


class ElecTransferForm(forms.Form):
    entity_id = forms.IntegerField()
    energy_mwh = forms.IntegerField()
    client_id = forms.ModelChoiceField(queryset=Entity.objects.all(), required=False)


@require_POST
@check_user_rights(role=[UserRights.ADMIN, UserRights.RW])
def create_transfer_certificate(request, *args, **kwargs):
    transfer_form = ElecTransferForm(request.POST)

    if not transfer_form.is_valid():
        return ErrorResponse(400, ElecTransferError.MALFORMED_PARAMS, transfer_form.errors)

    transfer_form_values = transfer_form.cleaned_data

    with transaction.atomic():
        # Parcourir les certificat de provision et vider au fur et à mesure tant que on a pas atteint la somme
        energy_pulled = 0

        entity_id = transfer_form_values["entity_id"]
        energy_required = transfer_form_values["energy_mwh"]

        available_provision_certificates = (
            ElecProvisionCertificate.objects.filter(cpo_id=entity_id)
            .exclude(remaining_energy_amount=0)
            .order_by("year", "quarter")
        )

        available_energy = available_provision_certificates.aggregate(Sum("remaining_energy_amount"))
        if available_energy["remaining_energy_amount__sum"] < energy_required:
            return ErrorResponse(400, ElecTransferError.NOT_ENOUGH_ENERGY)

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
                available_provision_certificates[current_certificate_idx].remaining_energy_amount = (
                    curr_certif_energy - missing_energy
                )
                energy_pulled = energy_required
            available_provision_certificates[current_certificate_idx].save()
            current_certificate_idx += 1

        try:
            transfer_certificate = ElecTransferCertificate(
                energy_amount=energy_required,
                client=transfer_form_values["client_id"],
                supplier_id=transfer_form_values["entity_id"],
                transfer_date=datetime.date.today(),
                status=ElecTransferCertificate.PENDING,
            )

            transfer_certificate.save()
            notify_elec_transfer_certificate(transfer_certificate)
            return SuccessResponse(ElecTransferCertificateSerializer(transfer_certificate).data)
        except:
            traceback.print_exc()
            return ErrorResponse(400, ElecTransferError.CREATION_FAILED)
