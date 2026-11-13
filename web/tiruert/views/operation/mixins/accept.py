from datetime import datetime

from django.db import transaction
from django.db.models import Case, Value, When
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from tiruert.models import Operation


class AcceptActionMixinErrors:
    NOTHING_TO_DECLARE = "NOTHING_TO_DECLARE"
    OPERATION_ALREADY_ACCEPTED_VALIDATED = "OPERATION_ALREADY_ACCEPTED_VALIDATED"
    OPERATION_TYPE_NOT_ALLOWED = "OPERATION_TYPE_NOT_ALLOWED"


class AcceptActionMixin:
    @staticmethod
    def get_status_after_accept(operation_type):
        """Return the status an operation should have after being accepted."""
        status_by_type = {
            Operation.CESSION: Operation.ACCEPTED,
            Operation.TRANSFERT: Operation.ACCEPTED,
            Operation.INCORPORATION: Operation.VALIDATED,
        }
        return status_by_type.get(operation_type)

    @extend_schema(
        operation_id="accept_operation",
        description="Set status operation to ACCEPTED",
        request=None,
        responses={
            status.HTTP_200_OK: OpenApiResponse(response={"status": "accepted"}, description="Success message"),
            status.HTTP_404_NOT_FOUND: OpenApiResponse(response={"detail": "Not found."}, description="Operation not found"),
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(
                response={"error": AcceptActionMixinErrors.OPERATION_ALREADY_ACCEPTED_VALIDATED}, description="Error message"
            ),
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(
                response={"error": AcceptActionMixinErrors.OPERATION_TYPE_NOT_ALLOWED}, description="Error message"
            ),
        },
    )
    @action(detail=True, methods=["post"])
    def accept(self, request, pk=None):
        operation = self.get_object()

        if operation.status != Operation.PENDING:
            return Response(
                {"error": AcceptActionMixinErrors.OPERATION_ALREADY_ACCEPTED_VALIDATED}, status=status.HTTP_400_BAD_REQUEST
            )

        operation_status = self.get_status_after_accept(operation.type)

        if not operation_status:
            return Response(
                {"error": AcceptActionMixinErrors.OPERATION_TYPE_NOT_ALLOWED}, status=status.HTTP_400_BAD_REQUEST
            )

        operation.status = operation_status
        operation.validation_date = datetime.now()
        operation.save()
        return Response({"status": "accepted"}, status=status.HTTP_200_OK)

    @extend_schema(
        operation_id="declare_teneur",
        description="Declare pending teneur operations, marking GHG-corrected operations as CORRECTED",
        request=None,
        responses={
            status.HTTP_200_OK: OpenApiResponse(response={"status": "validated"}, description="Success message"),
            status.HTTP_404_NOT_FOUND: OpenApiResponse(
                response={"error": AcceptActionMixinErrors.NOTHING_TO_DECLARE}, description="Error message"
            ),
        },
    )
    @action(
        detail=False,
        methods=["post"],
        url_path="teneur/declare",
    )
    @transaction.atomic
    def declare_teneur(self, request):
        queryset = self.filter_queryset(self.get_queryset()).filter(
            type=Operation.TENEUR,
            status=Operation.PENDING,
        )

        updated_count = queryset.update(
            status=Case(
                When(corrected=True, then=Value(Operation.CORRECTED)),
                default=Value(Operation.DECLARED),
            )
        )
        if not updated_count:
            return Response({"error": AcceptActionMixinErrors.NOTHING_TO_DECLARE}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"status": "declared"}, status=status.HTTP_200_OK)
