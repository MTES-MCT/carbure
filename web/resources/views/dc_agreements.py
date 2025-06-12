from django.db.models import Q
from django.utils import timezone
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from certificates.models import DoubleCountingRegistration
from certificates.serializers import DoubleCountingRegistrationResourceSerializer


@extend_schema(
    parameters=[
        OpenApiParameter(
            name="query",
            description="Search within the fields `certificate_id`",
            required=False,
            type=str,
        ),
    ],
    responses=DoubleCountingRegistrationResourceSerializer(many=True),
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_dc_agreements(request, *args, **kwargs):
    query = request.query_params.get("query", "")

    year = timezone.now().year

    agreements_active = (
        DoubleCountingRegistration.objects.filter(Q(valid_from__year__lte=year) & Q(valid_until__year__gte=year))
        .filter(certificate_id__icontains=query)
        .select_related("production_site")
        .order_by("production_site__name")
    )

    serializer = DoubleCountingRegistrationResourceSerializer(agreements_active, many=True)
    return Response(serializer.data)
