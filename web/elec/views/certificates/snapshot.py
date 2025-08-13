from drf_spectacular.utils import OpenApiExample, OpenApiParameter, OpenApiTypes, extend_schema
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from core.models import Entity, ExternalAdminRights
from elec.models import ElecProvisionCertificate, ElecTransferCertificate
from elec.permissions import HasCpoRights, HasElecAdminRights, HasElecOperatorRights, HasElecTransferAdminRights


@extend_schema(
    parameters=[
        OpenApiParameter(
            "entity_id",
            OpenApiTypes.INT,
            OpenApiParameter.QUERY,
            description="Entity ID",
            required=True,
        ),
        OpenApiParameter(
            "year",
            OpenApiTypes.INT,
            OpenApiParameter.QUERY,
            description="Year",
            required=True,
        ),
    ],
    examples=[
        OpenApiExample(
            "Example of filters response.",
            value={"provision_certificates_available": 5, "transfer_certificates_pending": 10, "...": "..."},
            request_only=False,
            response_only=True,
        ),
    ],
    responses={
        200: {
            "type": "object",
            "properties": {
                "provision_certificates_available": {"type": "integer"},
                "provision_certificates_history": {"type": "integer"},
                "transfer_certificates_pending": {"type": "integer"},
                "transfer_certificates_accepted": {"type": "integer"},
                "transfer_certificates_rejected": {"type": "integer"},
            },
            "required": [
                "provision_certificates_available",
                "provision_certificates_history",
                "transfer_certificates_pending",
                "transfer_certificates_accepted",
                "transfer_certificates_rejected",
            ],
        },
    },
)
@api_view(["GET"])
@permission_classes([HasCpoRights | HasElecOperatorRights | HasElecAdminRights | HasElecTransferAdminRights])
def get_snapshot(request, *args, **kwargs):
    entity = request.entity
    year = request.query_params.get("year")

    provision_certificates = ElecProvisionCertificate.objects.filter(year=year)
    transfer_certificates = ElecTransferCertificate.objects.filter(transfer_date__year=year)

    if entity.entity_type == Entity.CPO:
        provision_certificates = provision_certificates.filter(cpo=entity)
        transfer_certificates = transfer_certificates.filter(supplier=entity)
    elif entity.entity_type == Entity.OPERATOR:
        provision_certificates = provision_certificates.none()
        transfer_certificates = transfer_certificates.filter(client=entity)
    elif entity.has_external_admin_right(ExternalAdminRights.TRANSFERRED_ELEC):
        provision_certificates = provision_certificates.none()

    snapshot = {
        "provision_certificates_available": provision_certificates.filter(remaining_energy_amount__gt=0.01).count(),
        "provision_certificates_history": provision_certificates.filter(remaining_energy_amount__lte=0.01).count(),
        "transfer_certificates_pending": transfer_certificates.filter(status=ElecTransferCertificate.PENDING).count(),
        "transfer_certificates_accepted": transfer_certificates.filter(status=ElecTransferCertificate.ACCEPTED).count(),
        "transfer_certificates_rejected": transfer_certificates.filter(status=ElecTransferCertificate.REJECTED).count(),
    }

    return Response(snapshot)
