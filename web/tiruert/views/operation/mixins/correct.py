from django.db import transaction
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from tiruert.serializers import OperationCorrectionSerializer


class CorrectActionMixinErrors:
    OPERATION_NOT_FOUND = "OPERATION_NOT_FOUND"
    NOT_ENOUGH_VOLUME = "NOT_ENOUGH_VOLUME"


class CorrectActionMixin:
    @extend_schema(
        operation_id="correct_operation",
        description="Create a new operation 'CUSTOMS_CORRECTION' with a volume to add or remove",
        request=OperationCorrectionSerializer,
        responses={
            status.HTTP_200_OK: OpenApiResponse(response={"status": "corected"}, description="Success message"),
            status.HTTP_404_NOT_FOUND: OpenApiResponse(
                response={"error": CorrectActionMixinErrors.OPERATION_NOT_FOUND}, description="Error message"
            ),
            status.HTTP_404_NOT_FOUND: OpenApiResponse(
                response={"error": CorrectActionMixinErrors.NOT_ENOUGH_VOLUME}, description="Error message"
            ),
        },
    )
    @action(detail=True, methods=["post"])
    def correct(self, request, pk=None):
        with transaction.atomic():
            operation = self.get_object()

            serializer = OperationCorrectionSerializer(
                operation,
                data=request.data,
                context={"request": request},
            )
            if serializer.is_valid():
                serializer.save()
                return Response({"status": "corrected"}, status=status.HTTP_200_OK)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
