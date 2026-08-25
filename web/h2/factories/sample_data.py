from datetime import date
from decimal import Decimal

from core.factories.sample_data import set_user_access, setup_admin_user, setup_france, setup_regular_user
from core.models import Entity
from entity.factories.entity import EntityFactory
from h2.factories import H2StationFactory
from h2.models import H2Station
from traceability.factories import ActionFactory
from traceability.models import Action, Material


def setup_h2_entity() -> Entity:
    admin_user = setup_admin_user()
    regular_user = setup_regular_user()

    hrs_entity = EntityFactory(
        name="Distributeur H2",
        entity_type=Entity.HRS,
    )

    set_user_access(admin_user, hrs_entity, "ADMIN")
    set_user_access(regular_user, hrs_entity, "RW")

    return hrs_entity


def setup_h2_stations() -> tuple[H2Station, H2Station]:
    holder = setup_h2_entity()
    france = setup_france()

    h2_station_paris = H2StationFactory(
        name="Station H2 Paris",
        created_by=holder,
        country=france,
        access_type="PUBLIC",
        distributed_pressure=[350, 700],
        has_personal_vehicle_connector=True,
        storage_capacity=1000,
        distribution_capacity=500,
    )

    h2_station_lyon = H2StationFactory(
        name="Station H2 Lyon",
        created_by=holder,
        country=france,
        access_type="PRIVATE",
        distributed_pressure=[350, 700],
        has_personal_vehicle_connector=True,
        storage_capacity=1000,
        distribution_capacity=500,
    )

    return h2_station_paris, h2_station_lyon


def setup_h2_materials() -> tuple[Material, Material]:
    h2_rfnbo, _ = Material.objects.get_or_create(
        code="H2-RFBNO",
        defaults={"name": "Hydrogène RFNBO"},
    )

    h2_bio, _ = Material.objects.get_or_create(
        code="H2-BIO",
        defaults={"name": "Bio-H2"},
    )

    return h2_rfnbo, h2_bio


def setup_h2_lots_init() -> tuple[Action, Action]:
    holder = setup_h2_entity()
    paris_station, lyon_station = setup_h2_stations()
    h2_rfnbo, h2_bio = setup_h2_materials()

    h2_lot_01 = ActionFactory(
        pos_id="H2-DEMO-INIT-001",
        holder=holder,
        industry=Action.H2,
        type=Action.INIT,
        material=h2_rfnbo,
        quantity=Decimal("120000.000"),
        site=paris_station,
        shipping_date=date(2026, 1, 15),
        shipping_distance=25,
        shipping_method=Action.ROAD,
        working_date=date(2026, 1, 15),
    )

    h2_lot_02 = ActionFactory(
        pos_id="H2-DEMO-INIT-002",
        holder=holder,
        industry=Action.H2,
        type=Action.INIT,
        material=h2_bio,
        quantity=Decimal("240000.000"),
        site=lyon_station,
        shipping_date=date(2026, 2, 20),
        shipping_distance=80,
        shipping_method=Action.ROAD,
        working_date=date(2026, 2, 20),
    )

    return h2_lot_01, h2_lot_02


def create_sample_data():
    setup_h2_entity()
    setup_h2_stations()
    setup_h2_materials()
    setup_h2_lots_init()
