from decimal import ROUND_HALF_UP, Decimal

from traceability.models.material import Material

_PLACES = Decimal("0.001")


def _round(value):
    if value is None:
        return None
    return Decimal(value).quantize(_PLACES, rounding=ROUND_HALF_UP)


def _multiply(left, right):
    if left is None or right is None:
        return None
    return Decimal(left) * Decimal(right)


def _divide(left, right):
    if left is None or not right:
        return None
    return Decimal(left) / Decimal(right)


def convert_quantity(quantity, material):
    """Return mass (kg), volume (l) and energy (MJ).

    mass   = volume × density
    energy = mass × lhv

    A missing material or factor yields None for the value that needs it.
    """
    if quantity is None or material is None:
        return None, None, None

    quantity = Decimal(quantity)
    if material.unit == Material.KG:
        mass, volume, energy = quantity, _divide(quantity, material.density), _multiply(quantity, material.lhv)
    elif material.unit == Material.L:
        mass = _multiply(quantity, material.density)
        volume = quantity
        energy = _multiply(mass, material.lhv)
    elif material.unit == Material.MJ:
        mass = _divide(quantity, material.lhv)
        volume = _divide(mass, material.density)
        energy = quantity
    else:
        return None, None, None
    return _round(mass), _round(volume), _round(energy)


def attach_quantities(actions: list) -> list:
    """Set mass, volume and energy from the stored material, or previous_material.

    Call after ``attach_inherited_fields``.
    """
    for action in actions:
        material = action.material or action.inherited_fields["previous_material"]
        action.mass, action.volume, action.energy = convert_quantity(action.quantity, material)
    return actions
