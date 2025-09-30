from datetime import date

from django.db.models import Q
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from core.models import GenericCertificate
from core.serializers import GenericCertificateSerializer


@extend_schema(
    parameters=[
        OpenApiParameter(
            name="query",
            required=False,
            type=str,
        ),
    ],
    responses=GenericCertificateSerializer(many=True),
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_systeme_national_certificates(request: Request):
    today = date.today()
    query = request.query_params.get("query")

    sn_certificates = GenericCertificate.objects.order_by("-certificate_id").filter(
        certificate_type=GenericCertificate.SYSTEME_NATIONAL,
        valid_from__lte=today,
        valid_until__gte=today,
    )

    if query:
        sn_certificates = sn_certificates.filter(Q(certificate_id__contains=query) | Q(certificate_holder__contains=query))

    serializer = GenericCertificateSerializer(sn_certificates, many=True)
    return Response(serializer.data)
