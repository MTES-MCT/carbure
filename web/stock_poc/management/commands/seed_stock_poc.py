from django.core.management.base import BaseCommand, CommandError

from stock_poc.fixtures.scenarios import SCENARIO_FIXTURES, count_actions
from stock_poc.services.seed import seed_scenario


class Command(BaseCommand):
    """
    Seed POC entities and actions for a named scenario (final state).

    Examples:
        uv run python web/manage.py seed_stock_poc --list
        uv run python web/manage.py seed_stock_poc --scenario scenario_1
        uv run python web/manage.py seed_stock_poc --scenario scenario_3 --dry-run
    """

    help = "Seed stock POC test entities and scenario data"

    def add_arguments(self, parser):
        parser.add_argument(
            "--scenario",
            type=str,
            help="Scenario name (use --list to see available scenarios)",
        )
        parser.add_argument(
            "--list",
            action="store_true",
            help="List available scenario fixtures and exit",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Simulate seeding without persisting changes",
        )

    def handle(self, *args, **options):
        if options["list"]:
            self._print_scenarios()
            return

        scenario_name = options.get("scenario")
        if not scenario_name:
            raise CommandError("Provide --scenario or use --list.")

        dry_run = options["dry_run"]
        if dry_run:
            self.stdout.write(self.style.WARNING("Dry run: no changes will be persisted.\n"))

        try:
            entities = seed_scenario(scenario_name, dry_run=dry_run)
        except ValueError as exc:
            raise CommandError(str(exc)) from exc

        scenario = SCENARIO_FIXTURES[scenario_name]
        self.stdout.write(self.style.SUCCESS(f"Scenario '{scenario_name}' seeded."))
        self.stdout.write(scenario["description"])
        self.stdout.write(f"Actions created: {count_actions(scenario['roots'])}")
        self.stdout.write("Entities:")
        for key, entity in sorted(entities.items()):
            self.stdout.write(f"  {key}: #{entity.id} {entity.name}")

    def _print_scenarios(self):
        self.stdout.write("Available scenario fixtures:\n")
        for name, scenario in sorted(SCENARIO_FIXTURES.items()):
            self.stdout.write(f"  {name}")
            self.stdout.write(f"    {scenario['description']}")
            self.stdout.write(f"    actions={count_actions(scenario['roots'])}")
