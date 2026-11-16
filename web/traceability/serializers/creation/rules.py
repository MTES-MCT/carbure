from django.utils.translation import gettext_lazy as _
from rest_framework import serializers


def check_quantity(quantity, parent):
    if quantity <= 0:
        raise serializers.ValidationError(_("La quantité doit être strictement positive."))

    if parent is not None and quantity > parent.quantity_available:
        raise serializers.ValidationError(_("La quantité dépasse la quantité restante."))

    return quantity
