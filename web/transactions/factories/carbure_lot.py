import random
from datetime import datetime

import factory

from core.models import Biocarburant, CarbureLot, Entity, MatierePremiere, Pays
from transactions.models import Site as Depot
from transactions.models import Site as ProductionSite


class CarbureLotFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CarbureLot

    carbure_id = factory.Faker("lexify", text="????????????")
    created_at = factory.Faker("date_time_this_year")

    year = datetime.today().year
    period = factory.LazyAttribute(lambda obj: obj.year * 100 + random.randint(1, 12))

    transport_document_type = CarbureLot.DAE
    transport_document_reference = factory.Faker("lexify", text="????????????")

    # lot details
    volume = factory.Faker("random_int", min=5000, max=10000)
    weight = factory.Faker("random_int", min=5000, max=10000)
    lhv_amount = factory.Faker("random_int", min=5000, max=10000)
    feedstock = factory.Iterator(MatierePremiere.objects.all())
    biofuel = factory.Iterator(Biocarburant.objects.all())
    country_of_origin = factory.Iterator(Pays.objects.all())

    # production data
    carbure_producer = factory.Iterator(Entity.objects.filter(entity_type=Entity.PRODUCER))
    unknown_producer = factory.Faker("company")
    carbure_production_site = factory.Iterator(ProductionSite.objects.all())
    unknown_production_site = factory.Faker("company")
    production_country = factory.Iterator(Pays.objects.all())
    production_site_commissioning_date = factory.Faker("date_this_year")
    production_site_certificate = factory.Faker("lexify", text="????????????")
    production_site_certificate_type = factory.Faker("lexify", text="????????????")
    production_site_double_counting_certificate = factory.Faker("lexify", text="????????????")

    # delivery data
    carbure_supplier = factory.Iterator(Entity.objects.all())
    unknown_supplier = factory.Faker("company")
    supplier_certificate = factory.Faker("lexify", text="????????????")
    supplier_certificate_type = factory.Faker("lexify", text="????????????")

    carbure_vendor = None
    vendor_certificate = None
    vendor_certificate_type = None

    carbure_client = factory.Iterator(Entity.objects.all())
    unknown_client = factory.Faker("company")

    dispatch_date = factory.Faker("date_this_year")
    carbure_dispatch_site = None
    unknown_dispatch_site = None
    dispatch_site_country = None

    delivery_date = factory.Faker("date_this_year")
    carbure_delivery_site = factory.Iterator(Depot.objects.all())
    unknown_delivery_site = factory.Faker("company")
    delivery_site_country = factory.Iterator(Pays.objects.all())

    lot_status = random.choice(
        [
            CarbureLot.DRAFT,
            CarbureLot.DELETED,
            CarbureLot.FROZEN,
            CarbureLot.PENDING,
            CarbureLot.ACCEPTED,
            CarbureLot.REJECTED,
        ]
    )

    correction_status = random.choice(
        [
            CarbureLot.NO_PROBLEMO,
            CarbureLot.IN_CORRECTION,
            CarbureLot.FIXED,
        ]
    )

    delivery_type = random.choice(
        [
            CarbureLot.BLENDING,
            CarbureLot.EXPORT,
            CarbureLot.STOCK,
            CarbureLot.TRADING,
            CarbureLot.PROCESSING,
        ]
    )

    declared_by_supplier = factory.Faker("boolean")
    declared_by_client = factory.Faker("boolean")

    # GHG values
    eec = factory.Faker("random_number", digits=1)
    el = factory.Faker("random_number", digits=1)
    ep = factory.Faker("random_number", digits=1)
    etd = factory.Faker("random_number", digits=1)
    eu = factory.Faker("random_number", digits=1)
    esca = factory.Faker("random_number", digits=1)
    eccs = factory.Faker("random_number", digits=1)
    eccr = factory.Faker("random_number", digits=1)
    eee = factory.Faker("random_number", digits=1)
    ghg_total = factory.Faker("random_number", digits=1)
    ghg_reference = 60
    ghg_reduction = factory.Faker("random_number", digits=2)
    ghg_reference_red_ii = factory.Faker("random_number", digits=1)
    ghg_reduction_red_ii = factory.Faker("random_number", digits=1)

    added_by = factory.Iterator(Entity.objects.all())
    parent_lot = None
    parent_stock = None

    free_field = ""

    highlighted_by_admin = factory.Faker("boolean")
    highlighted_by_auditor = factory.Faker("boolean")
    random_control_requested = factory.Faker("boolean")
    ml_control_requested = factory.Faker("boolean")
    ml_scoring = 0.0

    audit_status = CarbureLot.UNKNOWN

    data_reliability_score = "F"


fields = [
    # lot data
    "feedstock",
    "biofuel",
    "country_of_origin",
    # production data
    "carbure_producer",
    "unknown_producer",
    "carbure_production_site",
    "unknown_production_site",
    "production_country",
    "production_site_commissioning_date",
    "production_site_certificate",
    "production_site_certificate_type",
    "production_site_double_counting_certificate",
    # ghg
    "eec",
    "el",
    "ep",
    "etd",
    "eu",
    "esca",
    "eccs",
    "eccr",
    "eee",
    "ghg_total",
    "ghg_reference",
    "ghg_reduction",
    "ghg_reference_red_ii",
    "ghg_reduction_red_ii",
]
