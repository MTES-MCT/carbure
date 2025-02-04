from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from tiruert.models import Operation


class AcceptActionMixinErrors:
    NOTHING_TO_VALIDATE = "NOTHING_TO_VALIDATE"


class AcceptActionMixin:
    @extend_schema(
        operation_id="accept_operation",
        description="Set status operation to ACCEPTED",
        request=None,
        responses={
            status.HTTP_200_OK: OpenApiResponse(response={"status": "accepted"}, description="Success message"),
            status.HTTP_404_NOT_FOUND: OpenApiResponse(
                response={"error": "Operation not found"}, description="Error message"
            ),
        },
    )
    @action(detail=True, methods=["post"])
    def accept(self, request, pk=None):
        operation = self.get_object()
        operation.status = Operation.ACCEPTED
        operation.save()
        return Response({"status": "accepted"}, status=status.HTTP_200_OK)

    @extend_schema(
        operation_id="validate_teneur",
        description="Set teneur operations to ACCEPTED",
        request=None,
        responses={
            status.HTTP_200_OK: OpenApiResponse(response={"status": "validated"}, description="Success message"),
            status.HTTP_404_NOT_FOUND: OpenApiResponse(
                response={"error": AcceptActionMixinErrors.NOTHING_TO_VALIDATE}, description="Error message"
            ),
        },
    )
    @action(
        detail=False,
        methods=["post"],
        url_path="teneur/validate",
    )
    def validate_teneur(self, request):
        queryset = (
            self.filter_queryset(self.get_queryset())
            .filter(type=Operation.TENEUR, status=Operation.PENDING)
            .order_by("created_at")
        )

        if not queryset.exists():
            return Response({"error": AcceptActionMixinErrors.NOTHING_TO_VALIDATE}, status=status.HTTP_400_BAD_REQUEST)

        # Get the first one to know which month to validate
        month = queryset.first().created_at.month
        queryset = queryset.filter(created_at__month=month)

        queryset.update(status=Operation.ACCEPTED)

        return Response({"status": "validated", "month": month}, status=status.HTTP_200_OK)
