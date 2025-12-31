from django.db.models import Sum
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import action
from rest_framework.response import Response

from core.models import Entity
from elec.models import ElecProvisionCertificate, ElecTransferCertificate
from elec.services.readjustment_balance import get_readjustment_balance


class BalanceActionMixin:
    @extend_schema(
        request=None,
        responses={
            200: {
                "type": "object",
                "properties": {
                    "balance": {"type": "float"},
                    "readjustment_balance": {"type": "float"},
                },
            }
        },
    )
    @action(methods=["GET"], detail=False)
    def balance(self, request):
        entity = request.entity
        provisions = ElecProvisionCertificate.objects.all()
        transfers = ElecTransferCertificate.objects.all()

        if entity.entity_type == Entity.CPO:
            provisions = provisions.filter(cpo=entity)
            transfers = transfers.filter(supplier=entity)

        total_provision = provisions.aggregate(Sum("energy_amount")).get("energy_amount__sum") or 0
        total_transfer = transfers.aggregate(Sum("energy_amount")).get("energy_amount__sum") or 0
        missing_readjustment = get_readjustment_balance(cpo=entity)

        return Response(
            {
                "balance": round(total_provision - total_transfer, 2) or 0,
                "readjustment_balance": missing_readjustment,
            }
        )
