from decimal import Decimal

from django.db.models import DecimalField, F, Q, QuerySet, Sum
from django.db.models.functions import Coalesce

from stock_poc.models import Action


def with_available(queryset: QuerySet | None = None) -> QuerySet:
    """Annotate each action with `available = quantity - sum(direct children quantities)`.

    Only ACCEPTED children reserve quantity; PENDING/REFUSED/null children are ignored.
    """
    queryset = queryset if queryset is not None else Action.objects.all()
    children_sum = Coalesce(
        Sum("children__quantity", filter=Q(children__status__in=[Action.ACCEPTED, Action.PENDING])),
        Decimal("0"),
        output_field=DecimalField(max_digits=20, decimal_places=2),
    )
    return queryset.annotate(available=F("quantity") - children_sum)


def available_for_consumption(entity) -> QuerySet:
    """Physical stock the entity can still consume.

    For each CREATION_H2 action owned by the entity, whose parent is not a
    VALORISATION, with a strictly positive available balance.
    """
    return (
        with_available()
        .filter(type=Action.CREATION_H2, owner=entity)
        .exclude(parent__type=Action.VALORISATION)
        .filter(available__gt=0)
    )


def available_for_certificates(entity) -> QuerySet:
    """Accounting stock the entity can still transfer as certificates.

    For each VALORISATION action owned by the entity with a strictly positive
    available balance.
    """
    return with_available().filter(type=Action.VALORISATION, owner=entity).filter(available__gt=0)
