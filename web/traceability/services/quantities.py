from django.db.models import Case, DecimalField, Expression, ExpressionWrapper, F, Value, When
from django.db.models.functions import Round

QUANTITY_FIELD = DecimalField(max_digits=13, decimal_places=3)


def _expression_wrapper(expression: Expression) -> ExpressionWrapper:
    return ExpressionWrapper(expression, output_field=QUANTITY_FIELD)


def quantities_db_annotation() -> dict:
    """Annotate mass (kg), volume (l) and energy (MJ) from the action's snapped factors.

    mass   = volume × density
    energy = mass × lhv

    Uses `action.lhv` / `action.density` (copied at tree root creation), not the material.
    Missing factors yield NULL.
    """
    from traceability.models.action import Action

    quantity = F("quantity")
    lhv = F("lhv")
    density = F("density")
    empty = Value(None, output_field=QUANTITY_FIELD)

    mass = Round(
        Case(
            When(unit=Action.KG, then=quantity),
            When(unit=Action.L, then=_expression_wrapper(quantity * density)),
            When(unit=Action.MJ, then=_expression_wrapper(quantity / lhv)),
            default=empty,
            output_field=QUANTITY_FIELD,
        ),
        precision=3,
    )
    volume = Round(
        Case(
            When(unit=Action.L, then=quantity),
            When(unit=Action.KG, then=_expression_wrapper(quantity / density)),
            When(unit=Action.MJ, then=_expression_wrapper(quantity / lhv / density)),
            default=empty,
            output_field=QUANTITY_FIELD,
        ),
        precision=3,
    )
    energy = Round(
        Case(
            When(unit=Action.MJ, then=quantity),
            When(unit=Action.KG, then=_expression_wrapper(quantity * lhv)),
            When(unit=Action.L, then=_expression_wrapper(quantity * density * lhv)),
            default=empty,
            output_field=QUANTITY_FIELD,
        ),
        precision=3,
    )
    return {"mass": mass, "volume": volume, "energy": energy}
