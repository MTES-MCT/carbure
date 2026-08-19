from importlib import import_module

import factory.random
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

SEEDS = [
    "core.seeds.geography.setup_countries",
    "core.seeds.users.setup_users",
    "h2.seeds.hrs.setup_hrs_entity",
]


class Command(BaseCommand):
    help = "Run the configured seed functions in order."

    def handle(self, *args, **options):
        seeds = [(seed_name, self._get_seed(seed_name)) for seed_name in SEEDS]

        # reset factory boy random seed to allow predictably generating random instances
        factory.random.reseed_random("carbure-local-seed-v1")

        with transaction.atomic():
            for seed_name, seed in seeds:
                if not callable(seed):
                    raise CommandError(f"Seed '{seed_name}' is not callable.")

                self.stdout.write(f"> Running {seed_name}")
                seed()

        self.stdout.write(self.style.SUCCESS("Seeding completed."))

    def _get_seed(self, seed_name):
        try:
            module_name, function_name = seed_name.rsplit(".", 1)
        except ValueError as exc:
            raise CommandError(f"Invalid seed name '{seed_name}'.") from exc

        module = import_module(module_name)
        return getattr(module, function_name, None)
