from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from tiruert.models import Operation


class RejectActionMixin:
    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        operation = self.get_object()
        operation.status = Operation.REJECTED
        operation.save()
        return Response({"status": "rejected"}, status=status.HTTP_200_OK)
