from django.db.models.query_utils import Q
from drf_spectacular.utils import OpenApiParameter, OpenApiTypes, extend_schema
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.response import Response

from doublecount.models import DoubleCountingApplication
from doublecount.serializers import DoubleCountingApplicationPartialSerializer


class ApplicationListeSerializer(serializers.Serializer):
    rejected = DoubleCountingApplicationPartialSerializer(many=True)
    pending = DoubleCountingApplicationPartialSerializer(many=True)


class ListActionMixin:
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
        responses=ApplicationListeSerializer,
    )
    @action(methods=["get"], detail=False, url_path="list-admin")
    def list_admin(self, request, *args, **kwargs):
        applications = self.get_queryset()
        rejected_data = applications.filter(status=DoubleCountingApplication.REJECTED)

        pending_data = applications.filter(
            ~Q(
                status__in=[
                    DoubleCountingApplication.ACCEPTED,
                    DoubleCountingApplication.REJECTED,
                ]
            )
        )
        rejected = DoubleCountingApplicationPartialSerializer(rejected_data, many=True)
        pending = DoubleCountingApplicationPartialSerializer(pending_data, many=True)

        data = {
            "rejected": rejected.data,
            "pending": pending.data,
        }
        return Response(data)
