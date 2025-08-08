import traceback

from biomethane.factories.contract import BiomethaneEntityConfigAmendmentFactory


def create_sample_data():
    print("Création des données d'exemple pour biomethane...")
    try:
        BiomethaneEntityConfigAmendmentFactory.create_batch(5)
        print("5 configurations complètes créées avec succès !")
    except Exception as e:
        traceback.print_exc()
        print(f"Erreur lors de la création: {e}")
        raise
