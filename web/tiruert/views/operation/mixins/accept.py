from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from tiruert.models import Operation


class AcceptActionMixinErrors:
    NOTHING_TO_VALIDATE = "NOTHING_TO_VALIDATE"


class AcceptActionMixin:
    @action(detail=True, methods=["post"])
    def accept(self, request, pk=None):
        operation = self.get_object()
        operation.status = Operation.ACCEPTED
        operation.save()
        return Response({"status": "accepted"}, status=status.HTTP_200_OK)

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

        return Response({"status": "validated"}, status=status.HTTP_200_OK)
