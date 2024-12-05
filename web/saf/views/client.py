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
    permission_classes = (IsAuthenticated,)
    serializer_class = EntityPreviewSerializer
    filterset_class = ClientFilter
    search_fields = ["name"]

    def get_queryset(self):
        is_airline = Q(entity_type=Entity.AIRLINE)
        is_saf_operator = Q(entity_type=Entity.OPERATOR, has_saf=True)
        queryset = Entity.objects.filter(is_airline | is_saf_operator).order_by("name")
        return queryset
