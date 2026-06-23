from decimal import Decimal

from django.db.models import DecimalField, F, Q, QuerySet, Sum
from django.db.models.functions import Coalesce

from stock_poc.models import Action


def with_available(queryset: QuerySet | None = None) -> QuerySet:
    """Annotate each action with `available = quantity - sum(reserving direct children)`."""
    queryset = queryset if queryset is not None else Action.objects.all()
    children_sum = Coalesce(
        Sum("children__quantity", filter=~Q(children__status=Action.REFUSED)),
        Decimal("0"),
        output_field=DecimalField(max_digits=20, decimal_places=2),
    )
    return queryset.annotate(available=F("quantity") - children_sum)
