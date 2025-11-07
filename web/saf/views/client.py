from django.db.models import Q
from rest_framework.mixins import (
    ListModelMixin,
    RetrieveModelMixin,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from core.models import Entity
from core.serializers import EntityPreviewSerializer
from saf.filters import ClientFilter


class ClientViewSet(
    ListModelMixin,
    RetrieveModelMixin,
    GenericViewSet,
):
    lookup_field = "id"
    queryset = Entity.objects.none()
    permission_classes = (IsAuthenticated,)
    serializer_class = EntityPreviewSerializer
    filterset_class = ClientFilter
    search_fields = ["name"]

    def get_queryset(self):
        query = Q()

        if self.request.entity.entity_type == Entity.SAF_TRADER:
            query = Q(entity_type=Entity.AIRLINE)
        else:
            is_airline = Q(entity_type=Entity.AIRLINE)
            is_saf_operator = Q(entity_type=Entity.OPERATOR, has_saf=True)
            is_saf_trader = Q(entity_type=Entity.SAF_TRADER)
            query = is_airline | is_saf_operator | is_saf_trader

        queryset = Entity.objects.filter(query).order_by("name")

        return queryset
