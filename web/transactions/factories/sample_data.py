from datetime import date

from certificates.models import DoubleCountingRegistration
from core.factories.sample_data import set_user_access, setup_admin_user, setup_france, setup_regular_user
from core.models import Biocarburant, CarbureLot, Entity, MatierePremiere
from entity.factories.entity import EntityFactory
from transactions.factories.carbure_lot import CarbureLotFactory
from transactions.factories.carbure_stock import CarbureStockFactory
from transactions.factories.certificate import EntityCertificateFactory, GenericCertificateFactory
from transactions.factories.depot import DepotFactory
from transactions.factories.production_site import (
    ProductionSiteFactory,
    ProductionSiteInputFactory,
    ProductionSiteOutputFactory,
)
from transactions.models.depot import Depot
from transactions.models.entity_site import EntitySite
from transactions.sanity_checks.sanity_checks import bulk_sanity_checks, bulk_scoring

DEMO_YEAR = 2026


def link_entity_to_sample_users(entity: Entity) -> None:
    admin_user = setup_admin_user()
    regular_user = setup_regular_user()

    set_user_access(admin_user, entity, "ADMIN")
    set_user_access(regular_user, entity, "RW")


def setup_entity_certificate(entity: Entity, certificate_id: str):
    certificate = GenericCertificateFactory(
        certificate_id=certificate_id,
        certificate_holder=entity.name,
        valid_from=date(2025, 1, 1),
        valid_until=date(2030, 12, 31),
    )
    EntityCertificateFactory(entity=entity, certificate=certificate)

    entity.default_certificate = certificate.certificate_id
    entity.save(update_fields=["default_certificate"])

    return certificate


def link_entity_to_site(entity: Entity, site) -> EntitySite:
    entity_site, _ = EntitySite.objects.update_or_create(
        entity=entity,
        site=site,
        defaults={
            "ownership_type": EntitySite.OWN,
            "blending_is_outsourced": False,
            "blender": None,
        },
    )
    return entity_site


def setup_producer_entity():
    france = setup_france()

    biofuel = Biocarburant.objects.order_by("code").first()
    feedstock = MatierePremiere.biofuel.order_by("code").first()

    producer = EntityFactory(
        name="Producteur biofuel",
        entity_type=Entity.PRODUCER,
        has_trading=False,
        registered_country=france,
    )

    link_entity_to_sample_users(producer)
    certificate = setup_entity_certificate(producer, "DEMO-PRODUCER-CERTIFICATE")

    double_counting_reference = f"FR_1000_{DEMO_YEAR}"

    production_site = ProductionSiteFactory(
        name="Site de production biofuel",
        created_by=producer,
        country=france,
        private=False,
        dc_number="1000",
        dc_reference=double_counting_reference,
        date_mise_en_service=date(2020, 1, 1),
    )
    ProductionSiteInputFactory(
        production_site=production_site,
        matiere_premiere=feedstock,
    )
    ProductionSiteOutputFactory(
        production_site=production_site,
        biocarburant=biofuel,
    )

    DoubleCountingRegistration.objects.update_or_create(
        certificate_id=double_counting_reference,
        defaults={
            "certificate_holder": producer.name,
            "production_site": production_site,
            "registered_address": production_site.address,
            "valid_from": date(2025, 1, 1),
            "valid_until": date(2030, 12, 31),
            "application": None,
        },
    )

    return producer, production_site, certificate


def setup_trader_entity():
    france = setup_france()

    trader = EntityFactory(
        name="Trader biofuel",
        entity_type=Entity.TRADER,
        has_trading=True,
        has_stocks=True,
        registered_country=france,
    )

    link_entity_to_sample_users(trader)
    certificate = setup_entity_certificate(trader, "DEMO-TRADER-CERTIFICATE")

    depot = DepotFactory(
        name="Dépôt biofuel 1",
        created_by=trader,
        country=france,
        private=False,
        site_type=Depot.BIOFUELDEPOT,
        customs_id="DEMO-DEPOT-001",
    )
    link_entity_to_site(trader, depot)

    return trader, depot, certificate


def setup_operator_entity():
    france = setup_france()

    operator = EntityFactory(
        name="Opérateur biofuel",
        entity_type=Entity.OPERATOR,
        has_direct_deliveries=True,
        registered_country=france,
    )

    link_entity_to_sample_users(operator)
    certificate = setup_entity_certificate(operator, "DEMO-OPERATOR-CERTIFICATE")

    depot = DepotFactory(
        name="Dépôt biofuel 2",
        created_by=operator,
        country=france,
        private=False,
        site_type=Depot.BIOFUELDEPOT,
        customs_id="DEMO-DEPOT-002",
    )
    link_entity_to_site(operator, depot)

    return operator, depot, certificate


def setup_transaction_lots(
    producer: Entity,
    trader: Entity,
    operator: Entity,
    producer_certificate,
    trader_certificate,
    france,
    production_site,
    depot_1,
    depot_2,
):
    DEMO_LOT_VOLUME = 10_000
    DEMO_STOCK_VOLUME = 5_000
    DEMO_CHILD_LOT_VOLUME = DEMO_LOT_VOLUME - DEMO_STOCK_VOLUME

    biofuel = Biocarburant.objects.get(code="ETH")
    feedstock = MatierePremiere.biofuel.get(code="ALGUES")

    source_lot = CarbureLotFactory(
        carbure_id="L202609-FR-DEMO-DEPOT-001-1",
        year=DEMO_YEAR,
        period=DEMO_YEAR * 100 + 9,
        volume=DEMO_LOT_VOLUME,
        weight=round(DEMO_LOT_VOLUME * biofuel.masse_volumique, 2),
        lhv_amount=round(DEMO_LOT_VOLUME * biofuel.pci_litre, 2),
        feedstock=feedstock,
        biofuel=biofuel,
        country_of_origin=france,
        carbure_producer=producer,
        unknown_producer=None,
        carbure_production_site=production_site,
        unknown_production_site=None,
        production_country=france,
        production_site_commissioning_date=production_site.date_mise_en_service,
        carbure_supplier=producer,
        unknown_supplier=None,
        supplier_certificate=producer_certificate.certificate_id,
        production_site_double_counting_certificate=production_site.dc_reference,
        carbure_client=trader,
        unknown_client=None,
        dispatch_date=date(DEMO_YEAR, 9, 1),
        carbure_dispatch_site=production_site,
        unknown_dispatch_site=None,
        dispatch_site_country=france,
        delivery_date=date(DEMO_YEAR, 9, 3),
        carbure_delivery_site=depot_1,
        unknown_delivery_site=None,
        delivery_site_country=france,
        ghg_reduction=80,
        ghg_reduction_red_ii=80,
        # The trader accepts this leg into stock, so the source lot is a STOCK lot.
        delivery_type=CarbureLot.STOCK,
        lot_status=CarbureLot.ACCEPTED,
        correction_status=CarbureLot.NO_PROBLEMO,
        added_by=producer,
        parent_lot=None,
        parent_stock=None,
    )

    stock = CarbureStockFactory(
        carbure_id="S202609-FR-DEMO-DEPOT-001-1",
        parent_lot=source_lot,
        depot=depot_1,
        carbure_client=trader,
        remaining_volume=DEMO_STOCK_VOLUME,
        remaining_weight=round(DEMO_STOCK_VOLUME * biofuel.masse_volumique, 2),
        remaining_lhv_amount=round(DEMO_STOCK_VOLUME * biofuel.pci_litre, 2),
        feedstock=feedstock,
        biofuel=biofuel,
        country_of_origin=france,
        carbure_production_site=production_site,
        unknown_production_site=None,
        production_country=france,
        carbure_supplier=producer,
        unknown_supplier=None,
        ghg_reduction=80,
        ghg_reduction_red_ii=80,
    )

    trader_lot = CarbureLotFactory(
        carbure_id="L202609-FR-DEMO-DEPOT-002-2",
        year=DEMO_YEAR,
        period=DEMO_YEAR * 100 + 9,
        volume=DEMO_CHILD_LOT_VOLUME,
        weight=round(DEMO_CHILD_LOT_VOLUME * biofuel.masse_volumique, 2),
        lhv_amount=round(DEMO_CHILD_LOT_VOLUME * biofuel.pci_litre, 2),
        feedstock=feedstock,
        biofuel=biofuel,
        country_of_origin=france,
        carbure_producer=producer,
        unknown_producer=None,
        carbure_production_site=production_site,
        unknown_production_site=None,
        production_country=france,
        production_site_commissioning_date=production_site.date_mise_en_service,
        carbure_supplier=trader,
        unknown_supplier=None,
        supplier_certificate=trader_certificate.certificate_id,
        production_site_double_counting_certificate=production_site.dc_reference,
        carbure_client=operator,
        unknown_client=None,
        dispatch_date=date(DEMO_YEAR, 9, 4),
        carbure_dispatch_site=depot_1,
        unknown_dispatch_site=None,
        dispatch_site_country=france,
        delivery_date=date(DEMO_YEAR, 9, 6),
        carbure_delivery_site=depot_2,
        unknown_delivery_site=None,
        delivery_site_country=france,
        ghg_reduction=80,
        ghg_reduction_red_ii=80,
        delivery_type=CarbureLot.TRADING,
        lot_status=CarbureLot.ACCEPTED,
        correction_status=CarbureLot.NO_PROBLEMO,
        added_by=trader,
        parent_lot=None,
        parent_stock=stock,
    )

    created_lots = CarbureLot.objects.filter(id__in=[source_lot.id, trader_lot.id])
    bulk_sanity_checks(created_lots)
    bulk_scoring(created_lots)

    return source_lot, stock, trader_lot


def create_sample_data():
    producer, production_site, producer_certificate = setup_producer_entity()
    trader, depot_1, trader_certificate = setup_trader_entity()
    operator, depot_2, _operator_certificate = setup_operator_entity()
    setup_transaction_lots(
        producer,
        trader,
        operator,
        producer_certificate,
        trader_certificate,
        production_site.country,
        production_site,
        depot_1,
        depot_2,
    )
