from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiTypes,
    extend_schema,
)
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.models import Entity
from elec.models import ElecProvisionCertificate, ElecTransferCertificate
from elec.permissions import HasCpoUserRights, HasElecAdminRights


@extend_schema(
    parameters=[
        OpenApiParameter(
            "entity_id",
            OpenApiTypes.INT,
            OpenApiParameter.QUERY,
            description="Entity ID",
            required=True,
        )
    ],
    examples=[
        OpenApiExample(
            "Example of filters response.",
            value=[
                2020,
                2021,
                2022,
                2023,
                2024,
            ],
            request_only=False,
            response_only=True,
        ),
    ],
    responses={200: {"type": "array", "items": {"type": "integer"}}},
)
@api_view(["GET"])
@permission_classes([IsAuthenticated & (HasCpoUserRights | HasElecAdminRights)])
def get_years(request, *args, **kwargs):
    entity = request.entity

    provision_years = ElecProvisionCertificate.objects.values_list("year", flat=True).distinct()
    transfer_years = ElecTransferCertificate.objects.values_list("transfer_date__year", flat=True).distinct()

    if entity.entity_type == Entity.CPO:
        provision_years = provision_years.filter(cpo=entity)
        transfer_years = transfer_years.filter(supplier=entity)

    years = list(set(list(provision_years) + list(transfer_years)))
    return Response(years)
