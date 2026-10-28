"""Local parent-chain timing data.

Half the VALORIZE actions sit on a chain of 10:

    INIT (material) → TEST1 → TEST2 → TEST3 → TEST1 → TEST2 → TEST3 → TEST1 → TEST2 → VALORIZE

The other half draws a chain length from 2 to 9. The first action is still INIT,
the last is VALORIZE, and the steps between cycle TEST1, TEST2, TEST3.
Each INIT takes one of 20 materials, in turn, so a material filter matches a slice of the chains.
The root holder cycles through the given entity and 99 other producers.
Actions below the root keep the given entity, so that entity still sees the list.
Two hundred sites are spread through the chains, never on the last action. A long chain
gets a second site closer to the leaf, so the nearest site is not always the far one.
The draw uses a fixed seed, so a second run builds the same trees.

Every row uses a ``PERF-`` pos_id. ``--delete`` removes them, children first.
The default build is 100000 actions.

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
WORKING_DATE = date(2026, 6, 1)
QUANTITY = Decimal("1000.000")
ZERO = Decimal("0")
DEEP_LENGTH = 10
VARIED_MIN_LENGTH = 2
VARIED_MAX_LENGTH = 9
MIDDLE_TYPES = (Action.TEST1, Action.TEST2, Action.TEST3)
RANDOM_SEED = 0
MATERIAL_COUNT = 20
HOLDER_COUNT = 100
SITE_COUNT = 200
ACTION_COUNT = 100_000


class Command(BaseCommand):
    help = "Create or delete local parent-chain timing actions (pos_id prefix PERF-)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--entity-id",
            type=int,
            help="Holder of the actions below the root. Roots also cycle through other PERF producers.",
        )
        parser.add_argument(
            "--material-code",
            type=str,
            help="Store this single material on every INIT. By default, INIT actions cycle through 20 materials.",
        )
        parser.add_argument(
            "--action-count",
            type=int,
            default=ACTION_COUNT,
            help="Number of actions. Half the chains have length 10, half have length 2-9. Default: 100000.",
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
        # Same shape as the valorize build: one half of the chains has length 10,
        # the other half stays between 2 and 9. The base length is the fixed draw.
        base = random.Random(RANDOM_SEED).randint(VARIED_MIN_LENGTH, VARIED_MAX_LENGTH)
        half = action_count // (DEEP_LENGTH + base)
        if half < 1:
            raise CommandError("--action-count is too small for this chain shape.")
        varied_lengths = [base] * half
        delta = action_count - half * DEEP_LENGTH - base * half
        step = 1 if delta > 0 else -1
        index = 0
        while delta != 0:
            current = varied_lengths[index % half]
            nxt = current + step
            if VARIED_MIN_LENGTH <= nxt <= VARIED_MAX_LENGTH:
                varied_lengths[index % half] = nxt
                delta -= step
            index += 1
            if index > half * (VARIED_MAX_LENGTH - VARIED_MIN_LENGTH + 1):
                raise CommandError("--action-count cannot be split into chains of length 10 and 2-9.")
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
        self.stdout.write(
            f"{valorize_count} VALORIZE actions for entity {entity_id}, materials {codes}: "
            f"{half} chains of {DEEP_LENGTH} ({deep_rows} rows) and "
            f"{len(varied_lengths)} chains of length {VARIED_MIN_LENGTH}-{VARIED_MAX_LENGTH} "
            f"({varied_rows} rows, {counts}). "
            f"Total {deep_rows + varied_rows} actions. "
            f"Roots cycle through {HOLDER_COUNT} holders. "
            f"{SITE_COUNT} sites are spread above the last action."
        )
        if dry_run:
            self.stdout.write("Dry run: nothing was written.")
            return

        material_ids = [material.pk for material in materials]
        producer_ids = self.producers(entity_id)
        site_ids = self.sites()
        with transaction.atomic():
            self.chains("D", deep_lengths, entity_id, material_ids, producer_ids, site_ids)
            self.chains("S", varied_lengths, entity_id, material_ids, producer_ids, site_ids)
        self.stdout.write(self.style.SUCCESS(f"Created {deep_rows + varied_rows} actions."))

    def chains(self, kind, lengths, entity_id, material_ids, producer_ids, site_ids):
        parents = [None] * len(lengths)
        for level in range(max(lengths)):
            selected = [index for index, length in enumerate(lengths) if level < length]
            actions = [
                self.action(
                    pos_id=f"{PREFIX}{kind}{index:05d}-{level:02d}",
                    entity_id=self.holder_id(level, index, entity_id, producer_ids),
                    action_type=self.level_type(level, lengths[index]),
                    parent_id=parents[index],
                    material_id=material_ids[index % len(material_ids)] if level == 0 else None,
                    site_id=self.site_id(level, index, lengths[index], site_ids),
                )
                for index in selected
            ]
            self.insert(actions)
            for index, action in zip(selected, actions):
                parents[index] = action.pk
            self.stdout.write(f"  {kind} level {level}: {len(actions)}")

    def holder_id(self, level, index, entity_id, producer_ids):
        if level == 0:
            return producer_ids[index % len(producer_ids)]
        return entity_id

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
            return Action.INIT
        if level == length - 1:
            return Action.VALORIZE
        return MIDDLE_TYPES[(level - 1) % len(MIDDLE_TYPES)]

    def action(self, *, pos_id, entity_id, action_type, parent_id, material_id, site_id):
        action = Action(
            pos_id=pos_id,
            holder_id=entity_id,
            industry=Action.H2,
            type=action_type,
            parent_id=parent_id,
            material_id=material_id,
            site_id=site_id,
            quantity=QUANTITY,
            working_date=WORKING_DATE,
        )
        for name in ("eec", "el", "ei", "ep", "etd", "eu", "eccs", "esca", "eccr"):
            setattr(action, name, ZERO)
        return action

    def insert(self, actions):
        Action.unannotated.bulk_create(actions, batch_size=1000)
        if actions[0].pk is None:
            by_pos_id = {action.pos_id: action for action in actions}
            for row in Action.unannotated.filter(pos_id__in=by_pos_id).only("id", "pos_id"):
                by_pos_id[row.pos_id].pk = row.id
        ActionStatus.objects.bulk_create(
            [ActionStatus(action_id=action.pk, status=ActionStatus.PENDING) for action in actions],
            batch_size=1000,
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

    def producers(self, entity_id):
        """The given entity, then PERF producers, one hundred holders in total."""
        ids = [entity_id]
        for index in range(2, HOLDER_COUNT + 1):
            producer, _created = Entity.objects.get_or_create(
                name=f"PERF Producteur {index:02d}",
                defaults={"entity_type": Entity.PRODUCER},
            )
            ids.append(producer.pk)
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

    def assign_existing_materials(self):
        """Point each existing PERF INIT at one of the 20 materials, in chain order."""
        material_ids = [material.pk for material in self.materials(None)]
        actions = list(Action.unannotated.filter(pos_id__startswith=PREFIX, type=Action.INIT).only("id", "pos_id"))
        for action in actions:
            index = int(action.pos_id[len(PREFIX) + 1 : len(PREFIX) + 6])
            action.material_id = material_ids[index % len(material_ids)]
        Action.unannotated.bulk_update(actions, ["material_id"], batch_size=1000)
        return len(actions), len(material_ids)

    def delete(self, dry_run):
        queryset = Action.unannotated.filter(pos_id__startswith=PREFIX)
        total = queryset.count()
        self.stdout.write(f"{total} PERF- actions to delete.")
        if dry_run or total == 0:
            return

        deleted = 0
        while True:
            parent_ids = set(queryset.exclude(parent_id=None).values_list("parent_id", flat=True))
            leaf_ids = list(queryset.exclude(pk__in=parent_ids).values_list("pk", flat=True)[:5000])
            if not leaf_ids:
                break
            count, _ = Action.unannotated.filter(pk__in=leaf_ids).delete()
            deleted += count
        remaining = queryset.count()
        if remaining:
            raise CommandError(f"{remaining} PERF- actions are still there. Their parent links form a cycle.")
        self.stdout.write(self.style.SUCCESS(f"Deleted {deleted} rows, statuses included."))
