from typing import Callable

from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import OpenApiExample, OpenApiParameter, extend_schema
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response


def FiltersActionFactory(filters: Callable[[Request], dict[str, str]]):
    class FiltersActionMixin:
        @extend_schema(
            filters=True,
            parameters=[
                OpenApiParameter(
                    name="filter",
                    type=str,
                    location=OpenApiParameter.QUERY,
                    description="Filter string to apply",
                ),
            ],
            examples=[
                OpenApiExample(
                    "Example of filters response.",
                    value=[
                        "ETBE",
                        "Ethanol",
                        "EMHV",
                        "B100",
                        "HVOE",
                    ],
                    request_only=False,
                    response_only=True,
                ),
            ],
            responses={
                200: {
                    "type": "array",
                    "items": {
                        "type": "string",
                    },
                },
            },
        )
        @action(methods=["get"], detail=False)
        def filters(self, request):
            filter_param = request.query_params.get("filter")
            if not filter_param:
                raise Exception("No filter was specified")

            # Remove filter param and create filterset
            query_params = request.GET.copy()
            query_params.pop(filter_param, None)
            filterset = self.filterset_class(query_params, queryset=self.get_queryset())

            # Get DB field from FilterSet programmatically
            filter_obj = filterset.filters.get(filter_param)
            if not filter_obj or filter_obj.method:  # Skip custom method filters
                raise Exception(f"Filter '{filter_param}' not found")

            # Use pre-filtered queryset for distinct values
            values = filterset.qs.values_list(filter_obj.field_name, flat=True).distinct().order_by(filter_obj.field_name)
            return Response([v for v in values if v is not None])

    return FiltersActionMixin


class ViewMethodFilterBackend(DjangoFilterBackend):
    # Implementation of get_filterset_class
    def get_filterset_class(self, view, queryset=None):
        if hasattr(view, "get_filterset_class"):
            return view.get_filterset_class()
        return super().get_filterset_class(view, queryset)
