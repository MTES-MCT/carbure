from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from core.models import Entity, UserRights
from tiruert.filters import OperationFilter
from tiruert.models import Operation
from tiruert.permissions import HasUserRights
from tiruert.serializers import OperationInputSerializer, OperationOutputSerializer

from .mixins import ActionMixin


class OperationViewSet(ModelViewSet, ActionMixin):
    queryset = Operation.objects.all()
    serializer_class = OperationOutputSerializer
    permission_classes = (
        IsAuthenticated,
        HasUserRights(None, [Entity.OPERATOR]),
    )
    filterset_class = OperationFilter

    def get_permissions(self):
        if self.action in ["reject", "accept", "balance"]:
            return [HasUserRights([UserRights.ADMIN, UserRights.RW])]
        return super().get_permissions()

    def get_serializer(self, *args, **kwargs):
        entity_id = self.request.GET.get("entity_id")
        details = self.request.GET.get("details", "0") == "1"
        kwargs["context"] = self.get_serializer_context()
        kwargs["context"]["entity_id"] = entity_id
        kwargs["context"]["details"] = details
        return super().get_serializer(*args, **kwargs)

    def create(self, request):
        serializer = OperationInputSerializer(
            data=request.data,
            context={"request": request},
        )
        if serializer.is_valid():
            operation = serializer.save()
            return Response(OperationOutputSerializer(operation).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.type == Operation.CESSION and instance.status in [Operation.PENDING, Operation.REJECTED]:
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_403_FORBIDDEN)
