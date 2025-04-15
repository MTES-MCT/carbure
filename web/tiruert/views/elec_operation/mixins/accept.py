from datetime import datetime

from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from tiruert.models import ElecOperation


class AcceptActionMixinErrors:
    NOTHING_TO_DECLARE = "NOTHING_TO_DECLARE"
    OPERATION_NOT_FOUND = "OPERATION_NOT_FOUND"
    OPERATION_ALREADY_ACCEPTED_VALIDATED = "OPERATION_ALREADY_ACCEPTED_VALIDATED"
    OPERATION_TYPE_NOT_ALLOWED = "OPERATION_TYPE_NOT_ALLOWED"


class AcceptActionMixin:
    @extend_schema(
        operation_id="accept_elec_operation",
        description="Set status operation to ACCEPTED",
        request=None,
        responses={
            status.HTTP_200_OK: OpenApiResponse(response={"status": "accepted"}, description="Success message"),
            status.HTTP_404_NOT_FOUND: OpenApiResponse(
                response={"error": AcceptActionMixinErrors.OPERATION_NOT_FOUND}, description="Error message"
            ),
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

        if operation.status != ElecOperation.PENDING:
            return Response(
                {"error": AcceptActionMixinErrors.OPERATION_ALREADY_ACCEPTED_VALIDATED}, status=status.HTTP_400_BAD_REQUEST
            )

        if operation.type == ElecOperation.CESSION:
            operation.status = ElecOperation.ACCEPTED
        else:
            return Response(
                {"error": AcceptActionMixinErrors.OPERATION_TYPE_NOT_ALLOWED}, status=status.HTTP_400_BAD_REQUEST
            )

        operation.validation_date = datetime.now()
        operation.save()
        return Response({"status": "accepted"}, status=status.HTTP_200_OK)

    @extend_schema(
        operation_id="declare_teneur",
        description="Set teneur operations to DECLARED",
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
    def declare_teneur(self, request):
        queryset = self.filter_queryset(self.get_queryset()).filter(
            type=ElecOperation.TENEUR,
            status=ElecOperation.PENDING,
        )

        if not queryset.exists():
            return Response({"error": AcceptActionMixinErrors.NOTHING_TO_DECLARE}, status=status.HTTP_400_BAD_REQUEST)

        queryset.update(status=ElecOperation.DECLARED)

        return Response({"status": "declared"}, status=status.HTTP_200_OK)
