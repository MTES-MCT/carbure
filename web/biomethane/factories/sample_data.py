import os
from datetime import date

from django.conf import settings
from django.core.management import call_command

from biomethane.factories.contract import create_contract_with_amendments
from biomethane.factories.digestate import create_digestate
from biomethane.factories.energy import create_biomethane_energy
from biomethane.factories.injection_site import create_injection_site
from biomethane.factories.production_unit import create_production_unit
from biomethane.factories.supply_plan import create_supply_plan
from biomethane.models import BiomethaneDeclarationPeriod
from biomethane.services.annual_declaration import BiomethaneAnnualDeclarationService
from core.factories.sample_data import set_user_access, setup_admin_user, setup_regular_user
from core.models import Entity
from entity.factories.entity import EntityFactory


def setup_declaration_period():
    """Open the current declaration year for the whole calendar year (local sample data)."""
    declaration_year = BiomethaneAnnualDeclarationService.get_current_declaration_year()
    calendar_year = date.today().year
    BiomethaneDeclarationPeriod.objects.update_or_create(
        year=declaration_year,
        defaults={
            "start_date": date(calendar_year, 1, 1),
            "end_date": date(calendar_year, 12, 31),
        },
    )


def setup_feedstocks():
    """Import the biomethane feedstock catalog used by the supply plan."""
    os.environ.setdefault("CARBURE_HOME", settings.CARBURE_HOME)
    call_command("import_biomethane_feedstocks_and_classifications")


def create_sample_data():
    setup_declaration_period()
    setup_feedstocks()

    admin_user = setup_admin_user()
    regular_user = setup_regular_user()

    entity = EntityFactory.create(
        name="Producteur de biométhane Test",
        entity_type=Entity.BIOMETHANE_PRODUCER,
    )

    set_user_access(admin_user, entity, "ADMIN")
    set_user_access(regular_user, entity, "RO")

    create_contract_with_amendments(entity)
    create_production_unit(entity)
    create_injection_site(entity)
    create_biomethane_energy(entity)
    create_supply_plan(entity)
    create_digestate(entity)
