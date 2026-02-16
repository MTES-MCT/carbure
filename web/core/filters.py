import django_filters
from drf_spectacular.utils import OpenApiExample, OpenApiParameter, extend_schema
from rest_framework.decorators import action
from rest_framework.response import Response


def FiltersActionFactory():
    class FiltersActionMixin:
        @classmethod
        def _get_available_filter_fields_static(cls, filterset_class, queryset):
            """
            Static version to get available filter fields from the filterset.
            Used in __init_subclass__.
            """
            # Create a temporary instance of the filterset to access its filters
            filterset = filterset_class({}, queryset=queryset)

            # Get the names of the filters, excluding those with custom methods
            available_filters = []
            excluded_filters = ["entity_id"]
            for filter_name, filter_obj in filterset.filters.items():
                if not filter_obj.method and filter_name not in excluded_filters:
                    available_filters.append(filter_name)

            return sorted(available_filters)

        def __init_subclass__(cls, **kwargs):
            """
            Called automatically when a class inherits from this mixin.
            Automatically configures the schema with available filters.
            """
            super().__init_subclass__(**kwargs)

            # Check if the class has a filterset_class
            if hasattr(cls, "filterset_class") and cls.filterset_class:
                try:
                    # Get a queryset to create the filterset
                    if hasattr(cls, "queryset") and cls.queryset is not None:
                        queryset = cls.queryset
                    elif hasattr(cls, "model") and cls.model:
                        queryset = cls.model.objects.all()
                    else:
                        print(f"Cannot configure dynamic filters for {cls.__name__}: no queryset or model found")
                        return

                    # Use the static method to get available filters
                    available_filters = cls._get_available_filter_fields_static(cls.filterset_class, queryset)

                    # Create the decorator with dynamic enum
                    schema_decorator = extend_schema(
                        filters=True,
                        parameters=[
                            OpenApiParameter(
                                name="filter",
                                type=str,
                                location=OpenApiParameter.QUERY,
                                description="Filter string to apply",
                                required=True,
                                enum=available_filters,
                            ),
                        ],
                        examples=[
                            OpenApiExample(
                                "Example of filters response.",
                                value=available_filters[:5] if len(available_filters) > 5 else available_filters,
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

                    # Apply the schema to the filters method
                    if hasattr(cls, "filters") and callable(cls.filters):
                        cls.filters = schema_decorator(cls.filters)

                except Exception as e:
                    print(f"Error configuring dynamic filters for {cls.__name__}: {e}")

        def get_available_filter_fields(self):
            """
            Get dynamically the list of available filter fields from the filterset class.
            """
            qs = self.get_queryset()
            filterset_class = self.filterset_class
            if hasattr(self, "get_filterset_class"):
                filterset_class = self.get_filterset_class()
            return self._get_available_filter_fields_static(filterset_class, qs)

        @action(methods=["get"], detail=False)
        def filters(self, request):
            filter_param = request.query_params.get("filter")
            if not filter_param:
                raise Exception("No filter was specified")

            # Check if filter_param is valid
            available_filters = self.get_available_filter_fields()
            if filter_param not in available_filters:
                raise Exception(f"Filter '{filter_param}' not found. Available filters: {available_filters}")

            # Remove filter param and create filterset
            query_params = request.GET.copy()
            query_params.pop(filter_param, None)
            filterset = self.filterset_class(query_params, queryset=self.get_queryset(), request=request)

            # Get DB field from FilterSet programmatically
            filter_obj = filterset.filters.get(filter_param)

            # Use pre-filtered queryset for distinct values
            values = filterset.qs.values_list(filter_obj.field_name, flat=True).distinct().order_by(filter_obj.field_name)
            return Response([v for v in values if v is not None])

    return FiltersActionMixin


class MultipleBooleanFilter(django_filters.TypedMultipleChoiceFilter):
    """
    Use this filter for boolean filtering, it will automatically give you True/False checks
    and allows you to have both selected at the same time.
    """

    def __init__(self, field_name, **kwargs):
        super().__init__(
            field_name=field_name,
            coerce=MultipleBooleanFilter.strtobool,
            choices=[("true", "True"), ("false", "False")],
            **kwargs,
        )

    @staticmethod
    def strtobool(val: str) -> bool:
        return val.lower() == "true"


class AllAnnotatedValuesMultipleFilter(django_filters.MultipleChoiceFilter):
    """
    A modified version of AllValuesMultipleFilter that allows adding annotation to the current query
    and filtering on the obtained values. It is compatible with the FiltersActionMixin.

    Usage:

    class TicketSourceFilter(django_filters.FilterSet):

        supplier = AllAnnotatedValuesMultipleFilter(
            field_name="supplier",
            annotation=Coalesce(
                "parent_lot__carbure_supplier__name",
                "parent_lot__unknown_supplier",
                "parent_ticket__supplier__name",
            ),
        )

    """

    def __init__(self, *args, **kwargs):
        self.annotation = kwargs.pop("annotation")
        super().__init__(*args, **kwargs)

    @property
    def field(self):
        qs = self.model._default_manager.distinct()
        qs = self.annotate(qs)
        qs = qs.order_by(self.field_name).values_list(self.field_name, flat=True)
        self.extra["choices"] = [(o, o) for o in qs]
        return super().field

    def filter(self, qs, value):
        qs = self.annotate(qs)
        return super().filter(qs, value)

    def annotate(self, qs):
        annotation = {self.field_name: self.annotation}
        return qs.annotate(**annotation)
