from datetime import datetime

from django.db.models.query_utils import Q
from drf_spectacular.utils import OpenApiParameter, OpenApiTypes, extend_schema
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.response import Response

from certificates.serializers import DoubleCountingRegistrationSerializer

from .utils import add_quotas_to_agreements


class AgreementListsSerializer(serializers.Serializer):
    active = DoubleCountingRegistrationSerializer(many=True)
    incoming = DoubleCountingRegistrationSerializer(many=True)
    expired = DoubleCountingRegistrationSerializer(many=True)


class AgreementAdminListActionMixin:
    @extend_schema(
        filters=True,
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
                required=False,
            ),
        ],
        responses=AgreementListsSerializer,
    )
    @action(methods=["get"], detail=False, url_path="agreement-admin")
    def agreement_admin(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        year = self.request.query_params.get("year", datetime.now().year)

        agreements_active = (
            queryset.filter(Q(valid_from__year__lte=year) & Q(valid_until__year__gte=year))
            .select_related("production_site")
            .order_by("production_site__name")
        )

        agreements_incoming = queryset.filter(Q(valid_from__year__gt=year)).select_related("production_site")
        agreements_expired = queryset.filter(Q(valid_until__year__lt=year)).select_related("production_site")

        active_agreements = DoubleCountingRegistrationSerializer(agreements_active, many=True).data
        active_agreements_with_quotas = add_quotas_to_agreements(year, active_agreements)

        data = {
            "active": active_agreements_with_quotas,
            "incoming": DoubleCountingRegistrationSerializer(agreements_incoming, many=True).data,
            "expired": DoubleCountingRegistrationSerializer(agreements_expired, many=True).data,
        }
        return Response(data)
