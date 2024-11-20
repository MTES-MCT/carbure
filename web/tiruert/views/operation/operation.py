from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from core.models import UserRights
from tiruert.models import Operation
from tiruert.permissions import HasUserRights
from tiruert.serializers import OperationSerializer

from .mixins import ActionMixin


class OperationViewSet(ModelViewSet, ActionMixin):
    queryset = Operation.objects.all()
    serializer_class = OperationSerializer

    def get_permissions(self):
        if self.action in ["reject", "accept"]:
            return [HasUserRights([UserRights.ADMIN, UserRights.RW])]
        return super().get_permissions()

    def create(self, request):
        serializer = OperationSerializer(data=request.data)
        if serializer.is_valid():
            operation = serializer.save()
            return Response(OperationSerializer(operation).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
