from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from tiruert.models import Operation


class AcceptActionMixin:
    @action(detail=True, methods=["post"])
    def accept(self, request, pk=None):
        operation = self.get_object()
        operation.status = Operation.ACCEPTED
        operation.save()
        return Response({"status": "accepted"}, status=status.HTTP_200_OK)
