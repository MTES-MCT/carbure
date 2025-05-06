from django.db.models import Q, Sum
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from core.models import Entity
from elec.models.elec_transfer_certificate import ElecTransferCertificate
from tiruert.models.elec_operation import ElecOperation
from tiruert.services.elec_balance import ElecBalanceService


class ElecOperationService:
    @staticmethod
    def update_operator_cpo_acquisition_operations(operator: Entity):
        """
        Compare the total amount of elec_transfer_certificates sent by a CPO to this operator
        with the already total amount of ACQUISITION_FROM_CPO elec_tiruert_operations of this operator,
        then create a new ACQUISITION_FROM_CPO elec_tiruert_operation with a quantity equal to the difference.
        Raise an exception if the difference is less than 0.
        Don't do anything if the difference is 0.
        """

        all_cpo_elec_certs = ElecTransferCertificate.objects.filter(
            supplier__entity_type=Entity.CPO,
            status=ElecTransferCertificate.ACCEPTED,
            client=operator,
        )

        all_elec_operations = ElecOperation.objects.filter(
            type=ElecOperation.ACQUISITION_FROM_CPO,
            status=ElecOperation.ACCEPTED,
            credited_entity=operator,
        )

        total_cpo_elec_certs = all_cpo_elec_certs.aggregate(Sum("energy_amount")).get("energy_amount__sum") or 0  # in MWh
        total_elec_operations = all_elec_operations.aggregate(Sum("quantity")).get("quantity__sum") or 0  # in MJ

        diff = (total_cpo_elec_certs * 3600) - total_elec_operations

        if diff < 0:
            raise Exception(
                "The total of TIRUERT acquisition certificates is greater than the total of certificates received from CPOs"
            )

        if diff > 0:
            return ElecOperation.objects.create(
                type=ElecOperation.ACQUISITION_FROM_CPO,
                status=ElecOperation.ACCEPTED,
                quantity=diff,
                credited_entity=operator,
            )

    @staticmethod
    def perform_checks_before_create(request, validated_data: dict, updated: ElecOperation = None):
        debited = validated_data.get("debited_entity")
        quantity = validated_data.get("quantity")

        if debited is None:
            return

        operations = ElecOperation.objects.filter(Q(credited_entity=debited) | Q(debited_entity=debited)).distinct()
        balance = ElecBalanceService.calculate_balance(operations, debited.id)

        available_balance = balance["available_balance"]
        if updated is not None:
            available_balance += updated.quantity

        if quantity > available_balance:
            raise serializers.ValidationError({"quantity": _("Quantity is greater than the available balance")})
