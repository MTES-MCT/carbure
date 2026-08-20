from core.seeds.geography import get_country
from h2.factories import H2StationFactory
from h2.models import H2Station
from h2.seeds.hrs import get_hrs_entity


def setup_h2_stations():
    holder = get_hrs_entity()
    country = get_country("FR")

    H2StationFactory(
        name="Station H2 Paris",
        created_by=holder,
        country=country,
        access_type="PUBLIC",
        distributed_pressure=[350, 700],
        has_personal_vehicle_connector=True,
        storage_capacity=1000,
        distribution_capacity=500,
    )

    H2StationFactory(
        name="Station H2 Lyon",
        created_by=holder,
        country=country,
        access_type="PRIVATE",
        distributed_pressure=[350, 700],
        has_personal_vehicle_connector=True,
        storage_capacity=1000,
        distribution_capacity=500,
    )


def get_h2_paris_station():
    return H2Station.objects.get(name="Station H2 Paris")


def get_h2_lyon_station():
    return H2Station.objects.get(name="Station H2 Lyon")
