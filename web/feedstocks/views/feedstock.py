from rest_framework.mixins import ListModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from feedstocks.filters import FeedstockFilter
from feedstocks.models import Feedstock
from feedstocks.serializers import FeedstocksSerializer


class FeedstockViewSet(GenericViewSet, ListModelMixin):
    queryset = Feedstock.objects.all()
    filterset_class = FeedstockFilter
    serializer_class = FeedstocksSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None
