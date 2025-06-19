from django.db.models import Sum
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import action
from rest_framework.response import Response

from elec.models import ElecProvisionCertificate, ElecTransferCertificate


class BalanceActionMixin:
    @extend_schema(
        request=None,
        responses={
            200: {
                "type": "object",
                "properties": {"balance": {"type": "integer"}},
            }
        },
    )
    @action(methods=["GET"], detail=False)
    def balance(self, request):
        entity = request.entity
        provisions = ElecProvisionCertificate.objects.filter(cpo=entity)
        transfers = ElecTransferCertificate.objects.filter(supplier=entity)
        total_provision = provisions.aggregate(Sum("energy_amount")).get("energy_amount__sum") or 0
        total_transfer = transfers.aggregate(Sum("energy_amount")).get("energy_amount__sum") or 0
        return Response({"balance": round(total_provision - total_transfer, 2) or 0})
