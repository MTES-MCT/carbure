from datetime import datetime

from rest_framework import serializers


class LookupSlugRelatedField(serializers.SlugRelatedField):
    """Resolve related objects from handler lookups, cached on the serializer context.

    The first access for a `lookup` runs `handler.lookups.<lookup>(entity)` once and stores
    `{slug: instance}` on `context["serializer_cache"][lookup]`. Later rows hit that dict.

    Set `slug_field` and `lookup` as class attributes or pass them to the constructor.
    Explicit constructor arguments take precedence over class attributes.
    """

    slug_field = None
    lookup = None

    def __init__(self, slug_field=serializers.empty, *, lookup=serializers.empty, **kwargs):
        self.lookup = self.lookup if lookup is serializers.empty else lookup
        assert self.lookup is not None, "The `lookup` argument or class attribute is required."
        slug_field = self.slug_field if slug_field is serializers.empty else slug_field
        super().__init__(slug_field=slug_field, **kwargs)

    def get_queryset(self):
        return getattr(self.context["handler"].lookups, self.lookup)(self.context.get("entity"))

    def to_internal_value(self, data):
        try:
            serializer_cache = self.context.setdefault("serializer_cache", {})
            if self.lookup not in serializer_cache:
                serializer_cache[self.lookup] = {
                    getattr(instance, self.slug_field): instance for instance in self.get_queryset()
                }
            return serializer_cache[self.lookup][data]
        except KeyError:
            self.fail("does_not_exist", slug_name=self.slug_field, value=data)


class ExcelDateField(serializers.DateField):
    """
    Excel reader converts dates to datetime objects so we need to convert them back to date objects.
    """

    def to_internal_value(self, value):
        if isinstance(value, datetime):
            value = value.date()
        return super().to_internal_value(value)


class ExcelMonthYearField(ExcelDateField):
    """Parse MM/YYYY (or an Excel datetime) and store the first day of that month."""

    def to_internal_value(self, value):
        value = super().to_internal_value(value)
        if value:
            return value.replace(day=1)
        return value
