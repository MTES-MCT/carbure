from datetime import datetime

from django.db.models.query_utils import Q
from drf_spectacular.utils import OpenApiParameter, OpenApiTypes, extend_schema
from rest_framework import serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from certificates.models import DoubleCountingRegistration
from doublecount.models import DoubleCountingApplication
from doublecount.permissions import HasDoubleCountingAdminRights, HasProducerRights


class ApplicationSnapshotSerializer(serializers.Serializer):
    applications_pending = serializers.IntegerField()
    applications_rejected = serializers.IntegerField()
    agreements_incoming = serializers.IntegerField()
    agreements_active = serializers.IntegerField()
    agreements_expired = serializers.IntegerField()


class SafSnapshotError:
    MALFORMED_PARAMS = "MALFORMED_PARAMS"
    SNAPSHOT_FAILED = "SNAPSHOT_FAILED"


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
    responses=ApplicationSnapshotSerializer,
)
@api_view(["GET"])
@permission_classes([HasProducerRights | HasDoubleCountingAdminRights])
def get_snapshot(request, *args, **kwargs):
    current_year = datetime.now().year

    applications = DoubleCountingApplication.objects.filter()

    applications_pending = applications.filter(
        ~Q(
            status__in=[
                DoubleCountingApplication.ACCEPTED,
                DoubleCountingApplication.REJECTED,
            ]
        )
    )
    applications_rejected = applications.filter(Q(status=DoubleCountingApplication.REJECTED))

    agreements_incoming = DoubleCountingRegistration.objects.filter(Q(valid_from__year__gt=current_year))
    agreements_active = DoubleCountingRegistration.objects.filter(
        Q(valid_from__year__lte=current_year) & Q(valid_until__year__gte=current_year)
    )
    agreements_expired = DoubleCountingRegistration.objects.filter(Q(valid_until__year__lt=current_year))

    return Response(
        {
            "applications_pending": applications_pending.count(),
            "applications_rejected": applications_rejected.count(),
            "agreements_incoming": agreements_incoming.count(),
            "agreements_active": agreements_active.count(),
            "agreements_expired": agreements_expired.count(),
        }
    )
