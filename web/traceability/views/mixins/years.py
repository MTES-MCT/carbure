from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response


class YearsActionMixin:
    """Add a years action based on an action's working date."""

    @extend_schema(
        filters=True,
        examples=[
            OpenApiExample(
                "Example of years response.",
                value=[2023, 2024, 2025],
                response_only=True,
            ),
        ],
        responses={status.HTTP_200_OK: {"type": "array", "items": {"type": "integer"}}},
    )
    @action(detail=False, methods=["get"], url_path="years")
    def get_years(self, request):
        years = self.filter_queryset(self.get_queryset()).values_list("working_date__year", flat=True).distinct()
        return Response(sorted(years))
