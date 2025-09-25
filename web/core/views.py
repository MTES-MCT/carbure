from django_filters.rest_framework import DjangoFilterBackend


class ViewMethodFilterBackend(DjangoFilterBackend):
    # Implementation of get_filterset_class
    def get_filterset_class(self, view, queryset=None):
        if hasattr(view, "get_filterset_class"):
            return view.get_filterset_class()
        return super().get_filterset_class(view, queryset)
