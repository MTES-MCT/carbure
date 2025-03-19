from django.db.models import F, Sum
from drf_spectacular.utils import OpenApiParameter, OpenApiTypes, extend_schema
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from core.models import Entity, UserRights
from core.pagination import MetadataPageNumberPagination
from saf.filters import TicketSourceFilter
from saf.models import SafTicketSource
from saf.permissions import HasUserRights
from saf.serializers import SafTicketSourceDetailsSerializer, SafTicketSourceSerializer

from .mixins import ActionMixin


class SafTicketSourcePagination(MetadataPageNumberPagination):
    aggregate_fields = {
        "total_available_volume": Sum(F("total_volume") - F("assigned_volume")),
    }


class SafTicketSourceViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet, ActionMixin):
    lookup_field = "id"
    permission_classes = (
        IsAuthenticated,
        HasUserRights(None, [Entity.OPERATOR]),
    )
    serializer_class = SafTicketSourceSerializer
    pagination_class = SafTicketSourcePagination
    filterset_class = TicketSourceFilter
    search_fields = [
        "carbure_id",
        "saf_tickets__client__name",
        "feedstock__name",
        "biofuel__name",
        "country_of_origin__name",
        "carbure_production_site__name",
        "unknown_production_site",
    ]

    def get_permissions(self):
        if self.action in ["grouped_assign", "assign", "credit"]:
            return [HasUserRights([UserRights.ADMIN, UserRights.RW], [Entity.OPERATOR])]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == "retrieve":
            return SafTicketSourceDetailsSerializer
        return super().get_serializer_class()

    def get_queryset(self):
        queryset = SafTicketSource.objects.none()
        if self.request and not self.request.user.is_anonymous:
            queryset = (
                SafTicketSource.objects.select_related(
                    "feedstock",
                    "biofuel",
                    "country_of_origin",
                    "carbure_production_site",
                )
                .prefetch_related("saf_tickets")
                .prefetch_related("saf_tickets__client")
            )
        return queryset

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
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
