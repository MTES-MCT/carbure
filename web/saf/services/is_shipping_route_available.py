from saf.models.saf_logistics import SafLogistics
from transactions.models import Airport
from transactions.models.depot import Depot


def is_shipping_route_available(
    origin_depot: Depot,
    destination_airport: Airport,
    shipping_method: str,
    has_intermediary_depot: bool,
):
    # accepter les tickets sans aéroport et méthode de transport
    # pour tolérer les échanges directs entre 2 opérateurs pétroliers
    if not destination_airport and not shipping_method:
        return True

    # autrement, bloquer les tickets incomplets
    if not (origin_depot and destination_airport and shipping_method):
        return False

    # les camions peuvent aller vraiment depuis n'importe où vers n'importe où
    if shipping_method == SafLogistics.TRUCK:
        return True

    shipping_routes = SafLogistics.objects.filter(
        origin_depot=origin_depot,
        destination_airport=destination_airport,
        shipping_method=shipping_method,
        has_intermediary_depot=has_intermediary_depot,
    )

    return shipping_routes.exists()
