from django.db.models import Q
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.models import GenericCertificate
from core.serializers import GenericCertificateSerializer


@extend_schema(
    parameters=[
        OpenApiParameter(
            name="query",
            description="Search within the fields `certificate_id` and `certificate_holder`",
            required=False,
            type=str,
        ),
        OpenApiParameter(
            name="date",
            description="Only return certificates valid at the given date",
            required=False,
            type=str,
        ),
    ],
    responses=GenericCertificateSerializer(many=True),
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_certificates(request, *args, **kwargs):
    query = request.query_params.get("query")
    date = request.query_params.get("date")

    certs = GenericCertificate.objects.all()

    if query:
        certs = certs.filter(Q(certificate_id__icontains=query) | Q(certificate_holder__icontains=query))
    if date:
        certs = certs.filter(Q(valid_from__lte=date) & Q(valid_until__gte=date))

    serializer = GenericCertificateSerializer(certs[0:100], many=True)
    return Response(serializer.data)
