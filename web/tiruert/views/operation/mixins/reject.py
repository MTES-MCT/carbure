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

        # # Create a CANCELED operation for the rejected operation
        # canceled_operation = Operation.objects.get(pk=operation.pk)
        # canceled_operation.pk = None
        # canceled_operation.status = Operation.CANCELED
        # canceled_operation.save()
        #
        # # Copy the details of the rejected operation to the canceled operation
        # for detail in operation.details.all():
        # detail.pk = None
        # detail.operation = canceled_operation
        # detail.save()

        return Response({"status": "rejected"}, status=status.HTTP_200_OK)
