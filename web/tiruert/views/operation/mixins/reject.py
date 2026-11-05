from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from tiruert.models import Operation


class RejectActionMixin:
    @extend_schema(
        operation_id="reject_operation",
        description="Set status operation to REJECTED",
        request=None,
        responses={
            status.HTTP_200_OK: OpenApiResponse(response={"status": "rejected"}, description="Success message"),
            status.HTTP_404_NOT_FOUND: OpenApiResponse(response={"detail": "Not found."}, description="Operation not found"),
        },
    )
    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        operation = self.get_object()
        if operation.type not in Operation.API_REJECTABLE_TYPES or operation.status != Operation.PENDING:
            return Response(status=status.HTTP_403_FORBIDDEN)

        operation.status = Operation.REJECTED
        operation.save()
        return Response({"status": "rejected"}, status=status.HTTP_200_OK)
