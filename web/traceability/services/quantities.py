from django.db.models import Case, DecimalField, Expression, ExpressionWrapper, F, Value, When
from django.db.models.functions import Round

QUANTITY_FIELD = DecimalField(max_digits=13, decimal_places=3)


def _expression_wrapper(expression: Expression) -> ExpressionWrapper:
    return ExpressionWrapper(expression, output_field=QUANTITY_FIELD)


def quantities_db_annotation() -> dict:
    """Annotate mass (kg), volume (l) and energy (MJ) from the material's factors.

    mass   = volume × density
    energy = mass × lhv

    Reads `material.lhv` / `material.density`. Missing factors yield NULL.
    """
    from traceability.models.material import Material

    quantity = F("quantity")
    lhv = F("material__lhv")
    density = F("material__density")
    empty = Value(None, output_field=QUANTITY_FIELD)

    mass = Round(
        Case(
            When(material__unit=Material.KG, then=quantity),
            When(material__unit=Material.L, then=_expression_wrapper(quantity * density)),
            When(material__unit=Material.MJ, then=_expression_wrapper(quantity / lhv)),
            default=empty,
            output_field=QUANTITY_FIELD,
        ),
        precision=3,
    )
    volume = Round(
        Case(
            When(material__unit=Material.L, then=quantity),
            When(material__unit=Material.KG, then=_expression_wrapper(quantity / density)),
            When(material__unit=Material.MJ, then=_expression_wrapper(quantity / lhv / density)),
            default=empty,
            output_field=QUANTITY_FIELD,
        ),
        precision=3,
    )
    energy = Round(
        Case(
            When(material__unit=Material.MJ, then=quantity),
            When(material__unit=Material.KG, then=_expression_wrapper(quantity * lhv)),
            When(material__unit=Material.L, then=_expression_wrapper(quantity * density * lhv)),
            default=empty,
            output_field=QUANTITY_FIELD,
        ),
        precision=3,
    )
    return {"mass": mass, "volume": volume, "energy": energy}
