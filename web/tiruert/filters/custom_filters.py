from django_filters.constants import EMPTY_VALUES
from django_filters.filters import OrderingFilter


class CustomOrderingFilter(OrderingFilter):
    def __init__(self, *args, extra_valid_fields=None, **kwargs):
        self.extra_valid_fields = extra_valid_fields or []
        super().__init__(*args, **kwargs)

    def build_choices(self, fields, labels):
        choices = super().build_choices(fields, labels)

        # Add extra fields (extra_valid_fields) to choices
        for field in self.extra_valid_fields:
            choices.append((field, field))
            choices.append((f"-{field}", f"{field} (descending)"))

        return choices

    def filter(self, qs, value):
        if value in EMPTY_VALUES:
            return qs

        # Remove extra valid fields from the value list
        extra_valid_fields_reverse = [f"-{v}" for v in self.extra_valid_fields]
        value = [v for v in value if v not in self.extra_valid_fields + extra_valid_fields_reverse]

        ordering = [self.get_ordering_value(param) for param in value if param not in EMPTY_VALUES]
        return qs.order_by(*ordering)
