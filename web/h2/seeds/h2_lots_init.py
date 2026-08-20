from datetime import date
from decimal import Decimal

from h2.seeds.h2_materials import get_bio_hydrogen, get_rfnbo_hydrogen
from h2.seeds.h2_stations import get_h2_lyon_station, get_h2_paris_station
from h2.seeds.hrs import get_hrs_entity
from traceability.factories import ActionFactory
from traceability.models import Action


def setup_h2_lots_init():
    holder = get_hrs_entity()

    renewable_hydrogen = get_rfnbo_hydrogen()
    low_carbon_hydrogen = get_bio_hydrogen()

    paris_station = get_h2_paris_station()
    lyon_station = get_h2_lyon_station()

    ActionFactory(
        pos_id="H2-DEMO-INIT-001",
        holder=holder,
        industry=Action.H2,
        type=Action.INIT,
        material=renewable_hydrogen,
        quantity=Decimal("120000.000"),
        site=paris_station,
        shipping_date=date(2026, 1, 15),
        shipping_distance=25,
        shipping_method=Action.ROAD,
        working_date=date(2026, 1, 15),
    )

    ActionFactory(
        pos_id="H2-DEMO-INIT-002",
        holder=holder,
        industry=Action.H2,
        type=Action.INIT,
        material=low_carbon_hydrogen,
        quantity=Decimal("240000.000"),
        site=lyon_station,
        shipping_date=date(2026, 2, 20),
        shipping_distance=80,
        shipping_method=Action.ROAD,
        working_date=date(2026, 2, 20),
    )
