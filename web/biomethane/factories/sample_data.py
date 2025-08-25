import traceback

from biomethane.factories.contract import create_contract_with_amendments
from core.models import Entity
from entity.factories.entity import EntityFactory


def create_sample_data():
    print("Création des données d'exemple pour biomethane...")
    entity = EntityFactory.create(entity_type=Entity.BIOMETHANE_PRODUCER)
    try:
        create_contract_with_amendments(entity)
    except Exception as e:
        traceback.print_exc()
        print(f"Erreur lors de la création: {e}")
        raise
