from carbure.tasks import background_bulk_sanity_checks, background_bulk_scoring
from core.carburetypes import CarbureSanityCheckErrors
from core.models import CarbureLot, GenericError
from entity.serializers.depot import CreateDepotSerializer
from entity.services.geolocation import get_coordinates


def do_create(depot_data, entity):
    serializer = CreateDepotSerializer(data=depot_data)
    serializer.is_valid(raise_exception=True)
    depot = serializer.save()

    depot.gps_coordinates = get_gps_coordinates(depot)
    depot.save()

    lots = CarbureLot.objects.filter(carbure_client=entity, carbure_delivery_site=depot)
    background_bulk_scoring(lots)
    background_bulk_sanity_checks(lots)
    GenericError.objects.filter(lot__in=lots, error=CarbureSanityCheckErrors.DEPOT_NOT_CONFIGURED).delete()

    return depot


def get_gps_coordinates(depot):
    address = depot.address + " " + depot.postal_code + " " + depot.city + ", " + depot.country.name
    xy = get_coordinates(address)
    return f"{xy[0]},{xy[1]}" if xy else None
