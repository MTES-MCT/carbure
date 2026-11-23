import decimal
from datetime import datetime

from rest_framework import serializers


class LookupSlugRelatedField(serializers.SlugRelatedField):
    """Resolve related objects from handler lookups, cached on the serializer context.

    The first access for a `lookup` runs `handler.lookups.<lookup>(entity)` once and stores
    `{slug: instance}` on `context["serializer_cache"][lookup]`. Later rows hit that dict.
    """

    def __init__(self, *args, lookup, **kwargs):
        self.lookup = lookup
        super().__init__(*args, **kwargs)

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


# 3 digits before the decimal point, 10 after. Excel stores an IEEE float:
# a displayed 15.339 can be saved as 15.339000000000002. Digits past 10
# decimals are truncated before the precision check, which would otherwise
# reject the cell.
EMISSION_DECIMAL = {"max_digits": 13, "decimal_places": 10}


class TruncatingDecimalField(serializers.DecimalField):
    """Cut digits past ``decimal_places`` before the precision check.

    DRF rejects extra decimal places before quantizing. An Excel cell such as
    ``1.2349`` would fail a 3-place column. The extra digits are dropped first
    (``1.2349`` becomes ``1.234``), then the usual digit limits apply.
    """

    def __init__(self, **kwargs):
        kwargs["rounding"] = decimal.ROUND_DOWN
        super().__init__(**kwargs)

    def validate_precision(self, value):
        if self.decimal_places is not None:
            quantum = decimal.Decimal(1).scaleb(-self.decimal_places)
            value = value.quantize(quantum, rounding=decimal.ROUND_DOWN)
        return super().validate_precision(value)
