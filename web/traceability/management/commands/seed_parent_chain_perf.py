"""Local parent-chain timing data.

Each chain is PRODUCE, then zero or more MOVE, then CONSUME, then VALORIZE.

Half the chains have length 10 (seven MOVE). The other half draws a length
from 3 to 9, so the number of MOVE steps varies.
Each PRODUCE takes one of 20 materials, in turn, so a material filter matches a slice of the chains.
One chain in ten belongs entirely to the given entity, about 10% of the actions.
The other chains are spread across one hundred other companies, one company per chain.
A standard user of the given entity therefore sees only those chains. An industry admin sees every row.
Emissions are set on the step that produces them: production, transport, then consumption.
A MOVE also stores a shipping method and a distance. Quantity, month and status vary by chain.
Two hundred sites are spread through the chains, never on the last action. A long chain
gets a second site closer to the leaf, so the nearest site is not always the far one.
The draw uses a fixed seed, so a second run builds the same trees.

Every row uses a ``PERF-`` pos_id. ``--delete`` removes them, children first.
Inserts commit every 5000 actions, with their statuses. A stopped run leaves a partial
forest; ``--delete`` removes it. The default build is 100000 actions.

    uv run python web/manage.py seed_parent_chain_perf --entity-id 9
    uv run python web/manage.py seed_parent_chain_perf --entity-id 9 --dry-run
    uv run python web/manage.py seed_parent_chain_perf --delete
"""

import random
from collections import Counter
from datetime import date
from decimal import Decimal

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from core.models import Entity
from traceability.models import Action, ActionStatus, Material
from transactions.models.site import Site

PREFIX = "PERF-"
ZERO = Decimal("0")
THOUSANDTH = Decimal("0.001")
DEEP_LENGTH = 10
VARIED_MIN_LENGTH = 3
VARIED_MAX_LENGTH = 9
RANDOM_SEED = 0
MATERIAL_COUNT = 20
OTHER_HOLDER_COUNT = 100
OWN_CHAIN_STRIDE = 10
SITE_COUNT = 200
ACTION_COUNT = 100_000
COMMIT_BATCH = 5_000
CHAIN_STATUSES = (
    ActionStatus.CREATED,
    ActionStatus.PENDING,
    ActionStatus.ACCEPTED,
    ActionStatus.REJECTED,
    ActionStatus.BLOCKED,
)
EMISSION_FIELDS = ("eec", "el", "ei", "ep", "etd", "eu", "eccs", "esca", "eccr")


class Command(BaseCommand):
    help = "Create or delete local parent-chain timing actions (pos_id prefix PERF-)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--entity-id",
            type=int,
            help="Company that owns one chain in ten. The other chains are spread across 100 PERF companies.",
        )
        parser.add_argument(
            "--material-code",
            type=str,
            help="Store this single material on every PRODUCE. By default, PRODUCE actions cycle through 20 materials.",
        )
        parser.add_argument(
            "--action-count",
            type=int,
            default=ACTION_COUNT,
            help="Number of actions. Half the chains have length 10, half have length 3-9. Default: 100000.",
        )
        parser.add_argument(
            "--valorize-count",
            type=int,
            help="Build this many VALORIZE actions instead of --action-count. Must be even and at least 2.",
        )
        parser.add_argument("--dry-run", action="store_true", help="Print the plan and write nothing.")
        parser.add_argument("--delete", action="store_true", help="Delete every action whose pos_id starts with PERF-.")

    def handle(self, *args, **options):
        if options["delete"]:
            self.delete(options["dry_run"])
            return
        if not options["entity_id"]:
            raise CommandError("--entity-id is required to create actions.")
        if options["valorize_count"] is not None and options["action_count"] != ACTION_COUNT:
            raise CommandError("Pass either --action-count or --valorize-count.")
        if options["valorize_count"] is not None:
            deep_lengths, varied_lengths = self.lengths_from_valorize_count(options["valorize_count"])
        else:
            deep_lengths, varied_lengths = self.lengths_from_action_count(options["action_count"])
        self.create(options["entity_id"], options["material_code"], deep_lengths, varied_lengths, options["dry_run"])

    def lengths_from_valorize_count(self, valorize_count):
        if valorize_count < 2 or valorize_count % 2:
            raise CommandError("--valorize-count must be an even number of at least 2.")
        half = valorize_count // 2
        deep_lengths = [DEEP_LENGTH] * half
        varied_lengths = [random.Random(RANDOM_SEED).randint(VARIED_MIN_LENGTH, VARIED_MAX_LENGTH) for _ in range(half)]
        return deep_lengths, varied_lengths

    def lengths_from_action_count(self, action_count):
        # One half of the chains has length 10. The other half stays between 3 and 9.
        # The shortest half that can still reach the requested total is used, then the
        # short chains grow until the row count matches.
        if action_count < DEEP_LENGTH + VARIED_MIN_LENGTH:
            raise CommandError("--action-count is too small for this chain shape.")
        span = VARIED_MAX_LENGTH - VARIED_MIN_LENGTH
        half = -(-action_count // (DEEP_LENGTH + VARIED_MAX_LENGTH))
        budget = action_count - half * (DEEP_LENGTH + VARIED_MIN_LENGTH)
        while budget < 0 and half > 1:
            half -= 1
            budget = action_count - half * (DEEP_LENGTH + VARIED_MIN_LENGTH)
        if half < 1 or budget < 0 or budget > half * span:
            raise CommandError("--action-count cannot be split into chains of length 10 and 3-9.")
        extra, remainder = divmod(budget, half)
        varied_lengths = [VARIED_MIN_LENGTH + extra + (1 if index < remainder else 0) for index in range(half)]
        return [DEEP_LENGTH] * half, varied_lengths

    def create(self, entity_id, material_code, deep_lengths, varied_lengths, dry_run):
        if not Entity.objects.filter(pk=entity_id).exists():
            raise CommandError(f"Entity {entity_id} does not exist.")
        materials = self.materials(material_code)
        if Action.unannotated.filter(pos_id__startswith=PREFIX).exists():
            raise CommandError("PERF- actions already exist. Run this command with --delete first.")

        half = len(deep_lengths)
        varied_rows = sum(varied_lengths)
        deep_rows = half * DEEP_LENGTH
        counts = ", ".join(f"{length}:{count}" for length, count in sorted(Counter(varied_lengths).items()))
        codes = ", ".join(material.code for material in materials)
        valorize_count = len(deep_lengths) + len(varied_lengths)
        total = deep_rows + varied_rows
        own_actions = self.owned_action_count(deep_lengths) + self.owned_action_count(varied_lengths)
        self.stdout.write(
            f"{valorize_count} VALORIZE actions, materials {codes}: "
            f"{half} chains of {DEEP_LENGTH} ({deep_rows} rows) and "
            f"{len(varied_lengths)} chains of length {VARIED_MIN_LENGTH}-{VARIED_MAX_LENGTH} "
            f"({varied_rows} rows, {counts}). "
            f"Total {total} actions. "
            f"Entity {entity_id} holds {own_actions} of them, one chain in {OWN_CHAIN_STRIDE}. "
            f"{OTHER_HOLDER_COUNT} other companies share the rest. "
            f"{SITE_COUNT} sites are spread above the last action."
        )
        if dry_run:
            self.stdout.write("Dry run: nothing was written.")
            return

        material_ids = [material.pk for material in materials]
        other_holder_ids = self.other_holders()
        site_ids = self.sites()
        self.chains("D", deep_lengths, entity_id, material_ids, other_holder_ids, site_ids)
        self.chains("S", varied_lengths, entity_id, material_ids, other_holder_ids, site_ids)
        self.stdout.write(self.style.SUCCESS(f"Created {deep_rows + varied_rows} actions."))

    def chains(self, kind, lengths, entity_id, material_ids, producer_ids, site_ids):
        parents = [None] * len(lengths)
        for level in range(max(lengths)):
            selected = [index for index, length in enumerate(lengths) if level < length]
            actions = [
                self.action(
                    pos_id=f"{PREFIX}{kind}{index:05d}-{level:02d}",
                    entity_id=self.holder_id(index, entity_id, producer_ids),
                    action_type=self.level_type(level, lengths[index]),
                    parent_id=parents[index],
                    material_id=material_ids[index % len(material_ids)] if level == 0 else None,
                    site_id=self.site_id(level, index, lengths[index], site_ids),
                    chain_index=index,
                    level=level,
                )
                for index in selected
            ]
            self.insert(actions)
            for index, action in zip(selected, actions):
                parents[index] = action.pk
            self.stdout.write(f"  {kind} level {level}: {len(actions)}")

    def owned_action_count(self, lengths):
        return sum(length for index, length in enumerate(lengths) if index % OWN_CHAIN_STRIDE == 0)

    def holder_id(self, index, entity_id, other_holder_ids):
        """The given entity owns every tenth chain. The others rotate through the rest."""
        if index % OWN_CHAIN_STRIDE == 0:
            return entity_id
        return other_holder_ids[index % len(other_holder_ids)]

    def site_id(self, level, index, length, site_ids):
        """Site stored on this step, or None.

        The last action of a chain has none, so a list of those actions looks upward.
        One site sits on a level that changes with the chain. A chain of 6 or more
        also gets a closer site, which is the one the upward walk keeps.
        """
        if level == length - 1:
            return None
        far_level = index % (length - 1)
        chosen = {far_level: site_ids[index % len(site_ids)]}
        if length >= 6:
            near_level = length - 2 - (index % 2)
            if near_level != far_level:
                chosen[near_level] = site_ids[(index + 3) % len(site_ids)]
        return chosen.get(level)

    def level_type(self, level, length):
        if level == 0:
            return Action.PRODUCE
        if level == length - 1:
            return Action.VALORIZE
        if level == length - 2:
            return Action.CONSUME
        return Action.MOVE

    def action(self, *, pos_id, entity_id, action_type, parent_id, material_id, site_id, chain_index, level):
        working_date = date(2026, (chain_index % 12) + 1, 15)
        quantity = Decimal(500 + (chain_index % 40) * 25)
        shipping_method = None
        shipping_distance = None
        shipping_date = None
        if action_type == Action.MOVE:
            shipping_method = Action.SHIPPING_METHODS[chain_index % len(Action.SHIPPING_METHODS)][0]
            shipping_distance = 40 + (chain_index % 25) * 20
            shipping_date = working_date
        action = Action(
            pos_id=pos_id,
            holder_id=entity_id,
            industry=Action.H2,
            type=action_type,
            parent_id=parent_id,
            material_id=material_id,
            site_id=site_id,
            quantity=quantity,
            working_date=working_date,
            shipping_method=shipping_method,
            shipping_distance=shipping_distance,
            shipping_date=shipping_date,
        )
        for name, value in self.emissions(chain_index, level, action_type).items():
            setattr(action, name, value)
        action._perf_status = CHAIN_STATUSES[chain_index % len(CHAIN_STATUSES)]
        return action

    def emissions(self, chain_index, level, action_type):
        """gCO2eq/MJ on the step that produces them. The same chain always gets the same draw."""
        values = {name: ZERO for name in EMISSION_FIELDS}
        wobble = Decimal((chain_index % 5) + 1) / Decimal(2)
        if action_type == Action.PRODUCE:
            values["eec"] = self.grams(Decimal("0.4") * wobble)
            values["el"] = self.grams(Decimal("0.2") * wobble)
            values["ei"] = self.grams(Decimal("3") + wobble)
            values["ep"] = self.grams(Decimal("1.2") * wobble)
        elif action_type == Action.MOVE:
            values["etd"] = self.grams(Decimal("0.3") * (level + 1) * wobble)
        elif action_type == Action.CONSUME:
            values["eu"] = self.grams(Decimal("0.8") * wobble)
            values["eccs"] = self.grams(Decimal("0.15") * wobble)
        return values

    def grams(self, value):
        return value.quantize(THOUSANDTH)

    def insert(self, actions):
        # One commit per batch. Holding the whole forest open exhausts the undo log
        # of a small MySQL when that single transaction commits.
        for start in range(0, len(actions), COMMIT_BATCH):
            chunk = actions[start : start + COMMIT_BATCH]
            with transaction.atomic():
                Action.unannotated.bulk_create(chunk, batch_size=COMMIT_BATCH)
                if chunk[0].pk is None:
                    by_pos_id = {action.pos_id: action for action in chunk}
                    for row in Action.unannotated.filter(pos_id__in=by_pos_id).only("id", "pos_id"):
                        by_pos_id[row.pos_id].pk = row.id
                ActionStatus.objects.bulk_create(
                    [ActionStatus(action_id=action.pk, status=action._perf_status) for action in chunk],
                    batch_size=COMMIT_BATCH,
                )

    def materials(self, code):
        if code:
            try:
                return [Material.objects.get(code=code)]
            except Material.DoesNotExist as exc:
                raise CommandError(f"Material {code} does not exist.") from exc

        source = Material.objects.order_by("code").first()
        rows = []
        for index in range(1, MATERIAL_COUNT + 1):
            material, _created = Material.objects.get_or_create(
                code=f"PERF-{index:02d}",
                defaults={
                    "name": f"Matière perf {index:02d}",
                    "unit": source.unit if source else Material.KG,
                    "lhv": source.lhv if source else None,
                    "density": source.density if source else None,
                },
            )
            rows.append(material)
        return rows

    def other_holders(self):
        """One hundred companies that share the chains not owned by the given entity."""
        ids = []
        for index in range(1, OTHER_HOLDER_COUNT + 1):
            company, _created = Entity.objects.get_or_create(
                name=f"PERF Société {index:03d}",
                defaults={"entity_type": Entity.PRODUCER},
            )
            ids.append(company.pk)
        return ids

    def sites(self):
        ids = []
        for index in range(1, SITE_COUNT + 1):
            site, _created = Site.objects.get_or_create(
                name=f"PERF Site {index:02d}",
                defaults={"site_type": Site.H2_REFUELING_STATION},
            )
            ids.append(site.pk)
        return ids

    def delete(self, dry_run):
        queryset = Action.unannotated.filter(pos_id__startswith=PREFIX)
        total = queryset.count()
        self.stdout.write(f"{total} PERF- actions to delete.")
        if dry_run or total == 0:
            return

        deleted = 0
        while True:
            parent_ids = set(queryset.exclude(parent_id=None).values_list("parent_id", flat=True))
            leaf_ids = list(queryset.exclude(pk__in=parent_ids).values_list("pk", flat=True)[:COMMIT_BATCH])
            if not leaf_ids:
                break
            count, _ = Action.unannotated.filter(pk__in=leaf_ids).delete()
            deleted += count
        remaining = queryset.count()
        if remaining:
            raise CommandError(f"{remaining} PERF- actions are still there. Their parent links form a cycle.")
        self.stdout.write(self.style.SUCCESS(f"Deleted {deleted} rows, statuses included."))
