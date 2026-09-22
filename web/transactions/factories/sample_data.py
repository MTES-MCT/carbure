from datetime import date

from core.factories.sample_data import set_user_access, setup_admin_user, setup_france, setup_regular_user
from core.models import Entity, UserRights
from entity.factories.entity import EntityFactory
from transactions.models import ProductionSite

PRODUCER_NAME = "Producteur de biocarburants Test"
PRODUCTION_SITE_NAME = "Site de production Test"


def setup_producer() -> Entity:
    admin_user = setup_admin_user()
    regular_user = setup_regular_user()
    france = setup_france()

    producer = EntityFactory.create(
        name=PRODUCER_NAME,
        entity_type=Entity.PRODUCER,
        registered_country=france,
    )

    set_user_access(admin_user, producer, UserRights.ADMIN)
    set_user_access(regular_user, producer, UserRights.RW)

    return producer


def setup_production_site() -> ProductionSite:
    producer = setup_producer()

    production_site, _ = ProductionSite.objects.get_or_create(
        name=PRODUCTION_SITE_NAME,
        created_by=producer,
        defaults={
            "country": setup_france(),
            "date_mise_en_service": date(2020, 1, 1),
        },
    )

    return production_site


def create_sample_data():
    setup_producer()
    setup_production_site()
