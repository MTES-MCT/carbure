from django.db.models import Q

from saf.models.saf_logistics import SafLogistics
from transactions.models import airport
from transactions.models.depot import Depot


def is_shipping_route_available(origin_depot: Depot, destination_airport: airport, shipping_method: str):
    if not origin_depot or not destination_airport or not shipping_method:
        return True

    # condition à débattre : son but est de permettre d'ajouter graduellement des routes logistiques
    # et de ne pas bloquer les dépôts et aéroports pour lesquels rien n'a encore été défini
    if not SafLogistics.objects.filter(Q(origin_depot=origin_depot) | Q(destination_airport=destination_airport)).exists():
        return True

    shipping_routes = SafLogistics.objects.filter(
        origin_depot=origin_depot,
        destination_airport=destination_airport,
        shipping_method=shipping_method,
    )

    return shipping_routes.exists()
