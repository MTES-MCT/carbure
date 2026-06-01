from django.db.models import Case, F, IntegerField, When
from django.db.models.functions import Cast, Substr

from tiruert.models.operation import Operation

# Nom de l'annotation SQL (distinct de la propriété Operation.year).
DB_FIELD = "_operation_year"


def resolve(
    operation_type: str,
    durability_period: str | None,
    declaration_year: int | None,
) -> int | None:
    """
    Année affichée / filtrable :
    - incorporation, MAC bio, livraison directe → année de la période de durabilité ;
    - autres opérations → année de déclaration Tiruert.
    """
    if operation_type in Operation.CREDIT_TYPES and durability_period:
        return int(durability_period[:4])
    return declaration_year


def db_annotation():
    """Expression SQL alignée sur resolve() (filtres et agrégations)."""
    return Case(
        When(
            type__in=Operation.CREDIT_TYPES,
            durability_period__isnull=False,
            then=Cast(
                Substr("durability_period", 1, 4),
                output_field=IntegerField(),
            ),
        ),
        default=F("declaration_year"),
        output_field=IntegerField(),
    )
