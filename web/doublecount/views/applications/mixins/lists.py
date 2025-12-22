from drf_spectacular.utils import extend_schema
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
        filters=True,
        responses=ApplicationListeSerializer,
    )
    @action(methods=["get"], detail=False, url_path="list-admin")
    def list_admin(self, request, *args, **kwargs):
        applications = self.filter_queryset(self.get_queryset())

        rejected_data = applications.filter(status=DoubleCountingApplication.REJECTED)

        pending_data = applications.exclude(
            status__in=[
                DoubleCountingApplication.ACCEPTED,
                DoubleCountingApplication.REJECTED,
            ]
        )
        rejected = DoubleCountingApplicationPartialSerializer(rejected_data, many=True)
        pending = DoubleCountingApplicationPartialSerializer(pending_data, many=True)

        data = {
            "rejected": rejected.data,
            "pending": pending.data,
        }
        return Response(data)
