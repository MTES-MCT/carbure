import random
from datetime import date, timedelta

import factory
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile

from biomethane.models import BiomethaneContract, BiomethaneContractAmendment
from core.models import Entity
from entity.factories.entity import EntityFactory

User = get_user_model()


class BiomethaneContractFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = BiomethaneContract

    entity = factory.SubFactory(EntityFactory, entity_type=Entity.BIOMETHANE_PRODUCER)
    buyer = Entity.objects.filter(entity_type=Entity.OPERATOR).order_by("?").first()

    # Tariff reference - choisir aléatoirement parmi les choix valides
    tariff_reference = factory.Faker(
        "random_element", elements=[choice[0] for choice in BiomethaneContract.TARIFF_REFERENCE_CHOICES]
    )

    # Installation category - requis pour TARIFF_RULE_1 (2011, 2020)
    installation_category = factory.LazyAttribute(
        lambda obj: random.choice([choice[0] for choice in BiomethaneContract.INSTALLATION_CATEGORIES])
        if obj.tariff_reference in BiomethaneContract.TARIFF_RULE_1
        else None
    )

    # cmax - requis pour TARIFF_RULE_1 (2011, 2020)
    cmax = factory.LazyAttribute(
        lambda obj: round(random.uniform(50.0, 500.0), 2)
        if obj.tariff_reference in BiomethaneContract.TARIFF_RULE_1
        else None
    )

    # cmax_annualized - requis pour TARIFF_RULE_1 (2011, 2020)
    cmax_annualized = factory.LazyAttribute(
        lambda obj: random.choice([True, False]) if obj.tariff_reference in BiomethaneContract.TARIFF_RULE_1 else False
    )

    # cmax_annualized_value - requis si cmax_annualized est True
    cmax_annualized_value = factory.LazyAttribute(
        lambda obj: round(random.uniform(80.0, 200.0), 2) if obj.cmax_annualized else None
    )

    # pap_contracted - requis pour TARIFF_RULE_2 (2021, 2023)
    pap_contracted = factory.LazyAttribute(
        lambda obj: round(random.uniform(50.0, 200.0), 2)
        if obj.tariff_reference in BiomethaneContract.TARIFF_RULE_2
        else None
    )

    # Dates optionnelles (pour contrat signé)
    signature_date = None
    effective_date = None

    # Fichiers optionnels
    general_conditions_file = None
    specific_conditions_file = None


class BiomethaneSignedContractFactory(BiomethaneContractFactory):
    signature_date = factory.LazyFunction(lambda: date.today() - timedelta(days=random.randint(1, 365)))
    effective_date = factory.LazyAttribute(lambda obj: obj.signature_date + timedelta(days=random.randint(1, 30)))

    general_conditions_file = factory.LazyFunction(
        lambda: ContentFile("conditions generales content".encode(), name="conditions_generales.pdf")
    )
    specific_conditions_file = factory.LazyFunction(
        lambda: ContentFile("conditions particulieres content".encode(), name="conditions_particulieres.pdf")
    )


class BiomethaneEntityConfigAmendmentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = BiomethaneContractAmendment

    contract = factory.SubFactory(BiomethaneContractFactory)

    # Dates obligatoires
    signature_date = factory.LazyFunction(lambda: date.today() - timedelta(days=random.randint(1, 180)))
    effective_date = factory.LazyAttribute(lambda obj: obj.signature_date + timedelta(days=random.randint(1, 90)))

    # Amendment object - liste de choix parmi les constantes
    amendment_object = factory.LazyFunction(
        lambda: [random.choice([choice[0] for choice in BiomethaneContractAmendment.AMENDMENT_OBJECT_CHOICES])]
    )

    # Fichier d'avenant obligatoire
    amendment_file = factory.LazyFunction(lambda: ContentFile("amendment content".encode(), name="amendment.pdf"))

    # Amendment details - optionnel sauf si OTHER est dans amendment_object
    amendment_details = factory.LazyAttribute(
        lambda obj: "Details pour l'avenant OTHER" if BiomethaneContractAmendment.OTHER in obj.amendment_object else None
    )


def create_contract_with_amendments(entity):
    contract = BiomethaneSignedContractFactory(entity=entity)
    BiomethaneEntityConfigAmendmentFactory.create_batch(
        2,
        contract=contract,
    )

    return contract
