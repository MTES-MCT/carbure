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
    ],
    responses=GenericCertificateSerializer(many=True),
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_certificates(request, *args, **kwargs):
    query = request.query_params.get("query")

    objects = GenericCertificate.objects.filter(Q(certificate_id__icontains=query) | Q(certificate_holder__icontains=query))[
        0:100
    ]
    serializer = GenericCertificateSerializer(objects, many=True)
    return Response(serializer.data)
