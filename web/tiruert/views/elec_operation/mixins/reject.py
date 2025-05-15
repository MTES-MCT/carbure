from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from tiruert.models import ElecOperation


class RejectActionMixinErrors:
    OPERATION_NOT_FOUND = "OPERATION_NOT_FOUND"


class RejectActionMixin:
    @extend_schema(
        operation_id="reject_elec_operation",
        description="Set status operation to REJECTED",
        request=None,
        responses={
            status.HTTP_200_OK: OpenApiResponse(response={"status": "rejected"}, description="Success message"),
            status.HTTP_404_NOT_FOUND: OpenApiResponse(
                response={"error": RejectActionMixinErrors.OPERATION_NOT_FOUND}, description="Error message"
            ),
        },
    )
    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        operation = self.get_object()
        operation.status = ElecOperation.REJECTED
        operation.save()
        return Response({"status": "rejected"}, status=status.HTTP_200_OK)
