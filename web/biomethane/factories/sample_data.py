import traceback

from django.db import transaction

from biomethane.factories.contract import create_contract_with_amendments
from biomethane.factories.energy import create_biomethane_energy
from biomethane.factories.injection_site import create_injection_site
from biomethane.factories.production_unit import create_production_unit
from biomethane.factories.supply_plan import create_supply_plan
from core.models import Entity
from entity.factories.entity import EntityFactory


def create_sample_data():
    print("Création des données d'exemple pour biomethane...")

    try:
        with transaction.atomic():
            entity = EntityFactory.create(entity_type=Entity.BIOMETHANE_PRODUCER)
            create_contract_with_amendments(entity)
            create_production_unit(entity)
            create_injection_site(entity)
            create_biomethane_energy(entity)
            create_supply_plan(entity)
    except Exception as e:
        traceback.print_exc()
        transaction.rollback()
        print(f"Erreur lors de la création: {e}")
        raise
