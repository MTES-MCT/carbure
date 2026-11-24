from django.db.models import CharField, Func


class Conv(Func):
    """MySQL CONV: number written in another base, uppercase."""

    function = "CONV"
    output_field = CharField()
