"""
Seed coherent TIRUERT test data: 3 TIRUERT-liable entities (2 operators, 1 producer)
plus credit and debit operations spread across the requested declaration years.

Usage:
    python web/manage.py seed_test_data \
        --years 2024,2025,2026 \
        --operations-per-year 5

    # Wipe previously seeded data first:
    python web/manage.py seed_test_data --reset

Business rules enforced:
  * Operators: INCORPORATION ops only, biofuel/feedstock picked among
    (EMAG, CONV), (ETH, CONV), (ETH, ANN-IX-A), (HOG, ANN-IX-B).
  * Producer: MAC_BIO ops only, always B100 / CONV.
  * TRANSFERT: producers can transfer to producers or operators.
    Operators can transfer to other operators only (never to a producer).
    * TENEUR, TRANSFERT and EXPORTATION only consume volumes the debited entity actually owns
    (received via INCORPORATION/MAC_BIO or via incoming TRANSFERT).
"""

import random
from collections import defaultdict

from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Q

from core.models import Biocarburant, CarbureLot, Entity, MatierePremiere
from tiruert.models import Operation, OperationDetail
from transactions.factories import CarbureLotFactory

TAG = "tiruert-test-data-seed"
ENTITY_NAME_PREFIX = "IRICC_SWITCH_YEAR Test"

ENTITY_DEFINITIONS = [
    {"label": "Operator", "type": Entity.OPERATOR},
    {"label": "Operator", "type": Entity.OPERATOR},
    {"label": "Producer", "type": Entity.PRODUCER},
]

# Operator INCORPORATION pool.
OPERATOR_BIOFUEL_FEEDSTOCK_PAIRS = [
    ("EMAG", MatierePremiere.CONV),
    ("ETH", MatierePremiere.CONV),
    ("ETH", MatierePremiere.IXA),
    ("HOG", MatierePremiere.IXB),
]

# Producer MAC_BIO pool (and teneur pool).
PRODUCER_BIOFUEL_FEEDSTOCK_PAIRS = [
    ("B100", MatierePremiere.CONV),
]

TENEUR_STATUSES = [Operation.DECLARED, Operation.PENDING]
TRANSFERT_STATUSES = [Operation.ACCEPTED, Operation.PENDING]
EXPORTATION_STATUS = Operation.DRAFT

TENEURS_PER_YEAR_PER_ENTITY = 3
TRANSFERTS_PER_YEAR_PER_PRODUCER = 3

LOTS_MIN = 10
LOTS_MAX = 20
VOLUME_MIN = 10_000
VOLUME_MAX = 100_000


class Command(BaseCommand):
    help = "Seed coherent TIRUERT test data (entities + operations across given years)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--years",
            type=str,
            default="2024,2025,2026",
            help="Comma-separated declaration years to seed (e.g. '2024,2025,2026').",
        )
        parser.add_argument(
            "--operations-per-year",
            type=int,
            default=5,
            help="Number of credit operations per type and per entity per year.",
        )
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Wipe previously seeded data (operations + lots tagged with TAG) before seeding.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        years = [int(y.strip()) for y in options["years"].split(",") if y.strip()]
        ops_per_year = options["operations_per_year"]

        if options["reset"]:
            self._cleanup()
            self._cleanup_entities()
            self.stdout.write(self.style.WARNING("Previous test data and tagged entities wiped."))
            return

        entities = self._create_new_tagged_entities()
        operator_pool = self._resolve_pairs(OPERATOR_BIOFUEL_FEEDSTOCK_PAIRS)
        producer_pool = self._resolve_pairs(PRODUCER_BIOFUEL_FEEDSTOCK_PAIRS)

        operators = [e for e in entities if e.entity_type == Entity.OPERATOR]
        producers = [e for e in entities if e.entity_type == Entity.PRODUCER]

        # Per-entity inventory: {entity_id: [ [lot, remaining_volume], ... ]}.
        # A debit op (teneur/transfert) consumes from one of these entries; a transfert
        # received by an entity adds a new entry to its inventory.
        inventory = defaultdict(list)

        for year in years:
            self.stdout.write(f"--- year {year} ---")

            # 1. Credit operations (build inventory).
            for operator in operators:
                for _ in range(ops_per_year):
                    self._create_credit_op(operator, Operation.INCORPORATION, year, operator_pool, inventory)
                self.stdout.write(f"  [{operator.entity_type}] {operator.name}: {ops_per_year} INCORPORATION ops")

            for producer in producers:
                for _ in range(ops_per_year):
                    self._create_credit_op(producer, Operation.MAC_BIO, year, producer_pool, inventory)
                self.stdout.write(f"  [{producer.entity_type}] {producer.name}: {ops_per_year} MAC_BIO ops")

            # 2. Transferts.
            # Rule: operators cannot transfer to a producer. Producers can transfer to anyone.
            for source in producers + operators:
                if source.entity_type == Entity.PRODUCER:
                    targets = [e for e in producers + operators if e.id != source.id]
                else:
                    targets = [e for e in operators if e.id != source.id]
                created = 0
                for _ in range(TRANSFERTS_PER_YEAR_PER_PRODUCER):
                    if not targets:
                        break
                    target = random.choice(targets)
                    if self._create_transfert(source, target, year, inventory):
                        created += 1
                self.stdout.write(f"  [{source.entity_type}] {source.name}: {created} transferts")

            # 3. Teneurs for every entity, restricted to its own inventory.
            for entity in entities:
                created = 0
                for _ in range(TENEURS_PER_YEAR_PER_ENTITY):
                    if self._create_teneur(entity, year, inventory):
                        created += 1
                self.stdout.write(f"  [{entity.entity_type}] {entity.name}: {created} teneurs")

            # 4. One DRAFT exportation per entity and per year.
            for entity in entities:
                created = 1 if self._create_exportation(entity, year, inventory) else 0
                self.stdout.write(f"  [{entity.entity_type}] {entity.name}: {created} exportation DRAFT")

        total_ops = Operation.objects.filter(export_recipient=TAG).count()
        self.stdout.write(self.style.SUCCESS(f"Done. {total_ops} operations created."))

    # ------------------------------------------------------------------ helpers

    def _create_new_tagged_entities(self):
        """
        Create entities tagged with TAG in activity_description, named per spec.
        """
        entities = []
        for definition in ENTITY_DEFINITIONS:
            entity = Entity.objects.create(
                name=f"{ENTITY_NAME_PREFIX} {definition['label']} {random.randint(100, 10000)}",
                entity_type=definition["type"],
                is_tiruert_liable=True,
                is_enabled=True,
                has_mac=True,
                has_trading=True,
                accise_number="1",
                activity_description=TAG,
            )
            entities.append(entity)
        return entities

    def _resolve_pairs(self, pairs):
        """
        Resolve (biofuel_code, feedstock_category) into concrete (Biocarburant, MatierePremiere) pairs.
        """
        resolved = []
        for biofuel_code, category in pairs:
            biofuel = Biocarburant.objects.filter(code=biofuel_code).first()
            feedstock = MatierePremiere.objects.filter(category=category).first()
            if biofuel and feedstock:
                resolved.append((biofuel, feedstock))
            else:
                self.stdout.write(self.style.WARNING(f"Skipping pair ({biofuel_code}, {category}): missing reference data."))
        if not resolved:
            raise RuntimeError("No valid (biofuel, feedstock) pair found in reference data.")
        return resolved

    def _cleanup_entities(self):
        """
        Delete all entities tagged with TAG; cascades to their operations.
        """
        Entity.objects.filter(activity_description=TAG).delete()

    def _create_credit_op(self, entity, op_type, year, pool, inventory):
        period_str = f"{year}{random.randint(1, 12):02d}"
        biofuel, feedstock = random.choice(pool)
        op = Operation.objects.create(
            type=op_type,
            status=Operation.VALIDATED,
            customs_category=feedstock.category,
            biofuel=biofuel,
            credited_entity=entity,
            debited_entity=None,
            renewable_energy_share=1.0,
            durability_period=period_str,
            export_recipient=TAG,
        )

        num_lots = random.randint(LOTS_MIN, LOTS_MAX)
        for _ in range(num_lots):
            volume = random.randint(VOLUME_MIN, VOLUME_MAX)
            lot = CarbureLotFactory.create(
                year=year,
                period=int(period_str),
                volume=volume,
                biofuel=biofuel,
                feedstock=feedstock,
                carbure_client=entity,
                lot_status="ACCEPTED",
                ghg_reduction_red_ii=round(random.uniform(50.0, 95.0), 2),
            )
            OperationDetail.objects.create(
                operation=op,
                lot=lot,
                volume=volume,
                emission_rate_per_mj=round(random.uniform(5.0, 40.0), 2),
            )
            # Mark this volume as owned by the credited entity for later debits.
            inventory[entity.id].append([lot, volume])

    def _pick_inventory_entry(self, entity, inventory, biofuel_feedstock_filter=None):
        """
        Return an inventory entry [lot, remaining_volume] the entity can still debit,
        optionally filtered by (biofuel_id, feedstock_id). The entry is mutable so the
        caller decrements remaining_volume in place after using it.
        """
        entries = [
            entry
            for entry in inventory.get(entity.id, [])
            if entry[1] >= VOLUME_MIN
            and (
                biofuel_feedstock_filter is None or (entry[0].biofuel_id, entry[0].feedstock_id) == biofuel_feedstock_filter
            )
        ]
        if not entries:
            return None
        return random.choice(entries)

    def _create_teneur(self, entity, year, inventory):
        # Producer teneurs are restricted to B100/CONV; operators use any of their inventory.
        filt = None
        if entity.entity_type == Entity.PRODUCER:
            b100 = Biocarburant.objects.filter(code="B100").first()
            conv = MatierePremiere.objects.filter(category=MatierePremiere.CONV).first()
            if not (b100 and conv):
                return False
            filt = (b100.id, conv.id)

        entry = self._pick_inventory_entry(entity, inventory, filt)
        if entry is None:
            return False

        lot, remaining = entry
        volume = random.randint(VOLUME_MIN, min(VOLUME_MAX, remaining))

        op = Operation.objects.create(
            type=Operation.TENEUR,
            status=random.choice(TENEUR_STATUSES),
            customs_category=lot.feedstock.category,
            biofuel=lot.biofuel,
            credited_entity=None,
            debited_entity=entity,
            renewable_energy_share=1.0,
            durability_period=None,
            declaration_year=year,
            export_recipient=TAG,
        )
        OperationDetail.objects.create(
            operation=op,
            lot=lot,
            volume=volume,
            emission_rate_per_mj=round(random.uniform(5.0, 40.0), 2),
        )
        entry[1] -= volume
        return True

    def _create_transfert(self, debited, credited, year, inventory):
        entry = self._pick_inventory_entry(debited, inventory)
        if entry is None:
            return False

        lot, remaining = entry
        volume = random.randint(VOLUME_MIN, min(VOLUME_MAX, remaining))

        op = Operation.objects.create(
            type=Operation.TRANSFERT,
            status=random.choice(TRANSFERT_STATUSES),
            customs_category=lot.feedstock.category,
            biofuel=lot.biofuel,
            debited_entity=debited,
            credited_entity=credited,
            renewable_energy_share=1.0,
            durability_period=None,
            declaration_year=year,
            export_recipient=TAG,
        )
        OperationDetail.objects.create(
            operation=op,
            lot=lot,
            volume=volume,
            emission_rate_per_mj=round(random.uniform(5.0, 40.0), 2),
        )
        # Move the transferred volume from debited to credited inventory.
        entry[1] -= volume
        inventory[credited.id].append([lot, volume])
        return True

    def _create_exportation(self, entity, year, inventory):
        entry = self._pick_inventory_entry(entity, inventory)
        if entry is None:
            return False

        lot, remaining = entry
        volume = random.randint(VOLUME_MIN, min(VOLUME_MAX, remaining))

        op = Operation.objects.create(
            type=Operation.EXPORTATION,
            status=EXPORTATION_STATUS,
            customs_category=lot.feedstock.category,
            biofuel=lot.biofuel,
            debited_entity=entity,
            credited_entity=None,
            renewable_energy_share=1.0,
            durability_period=None,
            declaration_year=year,
            export_recipient=TAG,
        )
        OperationDetail.objects.create(
            operation=op,
            lot=lot,
            volume=volume,
            emission_rate_per_mj=round(random.uniform(5.0, 40.0), 2),
        )
        entry[1] -= volume
        return True

    def _cleanup(self):
        tagged_entities = Entity.objects.filter(activity_description=TAG)
        operations_to_delete = Operation.objects.filter(
            Q(export_recipient=TAG) | Q(credited_entity__in=tagged_entities) | Q(debited_entity__in=tagged_entities)
        )
        lot_ids = list(
            OperationDetail.objects.filter(operation__in=operations_to_delete).values_list("lot_id", flat=True).distinct()
        )
        operations_to_delete.delete()
        if lot_ids:
            CarbureLot.objects.filter(id__in=lot_ids, carbure_client__in=tagged_entities).delete()
