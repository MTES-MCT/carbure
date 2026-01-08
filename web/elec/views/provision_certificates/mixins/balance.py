from drf_spectacular.utils import extend_schema
from rest_framework.decorators import action
from rest_framework.response import Response

from core.models import Entity
from elec.models import ElecProvisionCertificate, ElecTransferCertificate
from elec.services.certificate_balance import get_certificate_balance
from elec.services.readjustment_balance import get_readjustment_balance


class BalanceActionMixin:
    @extend_schema(
        request=None,
        responses={
            200: {
                "type": "object",
                "properties": {
                    "balance": {"type": "number"},
                    "readjustment_balance": {"type": "number"},
                },
            }
        },
    )
    @action(methods=["GET"], detail=False)
    def balance(self, request):
        entity = request.entity
        provisions = ElecProvisionCertificate.objects.all()
        transfers = ElecTransferCertificate.objects.all()

        total_balance = 0
        missing_readjustment = 0

        if entity.entity_type == Entity.CPO:
            provisions = provisions.filter(cpo=entity)
            transfers = transfers.filter(supplier=entity)
            total_balance = get_certificate_balance(cpo=entity)
            missing_readjustment = get_readjustment_balance(cpo=entity)
        else:
            total_balance = get_certificate_balance()

        return Response(
            {
                "balance": total_balance,
                "readjustment_balance": missing_readjustment,
            }
        )
