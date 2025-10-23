from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response


class YearsActionMixin:
    """
    Mixin to add a years action to a ViewSet.

    The ViewSet queryset must have a 'year' field.
    Returns a sorted list of distinct years from the queryset.
    """

    @extend_schema(
        examples=[
            OpenApiExample(
                "Example of years response.",
                value=[
                    2020,
                    2021,
                    2022,
                    2023,
                    2024,
                ],
                request_only=False,
                response_only=True,
            ),
        ],
        responses={status.HTTP_200_OK: {"type": "array", "items": {"type": "integer"}}},
    )
    @action(
        detail=False,
        methods=["get"],
        url_path="years",
    )
    def get_years(self, request, *args, **kwargs):
        """Return a sorted list of distinct years from the queryset."""
        years = self.filter_queryset(self.get_queryset()).values_list("year", flat=True).distinct()
        return Response(sorted(years))
