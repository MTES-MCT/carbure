from django.core.management.base import BaseCommand, CommandError

from core.models import Entity
from stock_poc.services.queries import SCENARIOS

HEADERS = ["id", "type", "status", "quantity", "available", "owner", "parent"]


class Command(BaseCommand):
    """
    Run a stock POC query scenario and print results in the terminal.

    Examples:
        uv run python web/manage.py query_stock_poc --list
        uv run python web/manage.py query_stock_poc --scenario consumption --entity-id 1
        uv run python web/manage.py query_stock_poc --scenario all
    """

    help = "Run a stock POC query scenario and print matching actions"

    def add_arguments(self, parser):
        parser.add_argument(
            "--scenario",
            type=str,
            help="Scenario name (use --list to see available scenarios)",
        )
        parser.add_argument(
            "--entity-id",
            type=int,
            help="Entity ID (required for entity-scoped scenarios)",
        )
        parser.add_argument(
            "--list",
            action="store_true",
            help="List available scenarios and exit",
        )

    def handle(self, *args, **options):
        if options["list"]:
            self._print_scenarios()
            return

        scenario_name = options.get("scenario")
        if not scenario_name:
            raise CommandError("Provide --scenario or use --list.")

        scenario = SCENARIOS.get(scenario_name)
        if scenario is None:
            available = ", ".join(sorted(SCENARIOS))
            raise CommandError(f"Unknown scenario '{scenario_name}'. Available: {available}")

        entity = None
        if scenario.requires_entity:
            entity_id = options.get("entity_id")
            if entity_id is None:
                raise CommandError(f"Scenario '{scenario_name}' requires --entity-id.")
            try:
                entity = Entity.objects.get(pk=entity_id)
            except Entity.DoesNotExist as exc:
                raise CommandError(f"Entity #{entity_id} not found.") from exc

        queryset = scenario.query(entity) if scenario.requires_entity else scenario.query()
        actions = list(queryset)

        self.stdout.write(f"> Scenario: {scenario_name}")
        self.stdout.write(f"> {scenario.help}")
        if entity:
            self.stdout.write(f"> Entity: #{entity.id} {entity.name}")
        self.stdout.write(f"> Results: {len(actions)}\n")

        if not actions:
            self.stdout.write("No actions matched.")
            return

        rows = [self._format_row(action) for action in actions]
        self._print_table(HEADERS, rows)

    def _print_scenarios(self):
        self.stdout.write("Available scenarios:\n")
        for name, scenario in sorted(SCENARIOS.items()):
            entity_hint = "requires --entity-id" if scenario.requires_entity else "no entity"
            self.stdout.write(f"  {name:14} [{entity_hint}]")
            self.stdout.write(f"    {scenario.help}")

    def _format_row(self, action) -> list[str]:
        return [
            str(action.id),
            action.type,
            action.status or "—",
            str(action.quantity),
            str(action.available),
            action.owner.name,
            str(action.parent_id) if action.parent_id else "—",
        ]

    def _print_table(self, headers: list[str], rows: list[list[str]]):
        widths = [len(header) for header in headers]
        for row in rows:
            for index, cell in enumerate(row):
                widths[index] = max(widths[index], len(cell))

        header_line = "  ".join(header.ljust(widths[index]) for index, header in enumerate(headers))
        self.stdout.write(header_line)
        self.stdout.write("-" * len(header_line))

        for row in rows:
            self.stdout.write("  ".join(cell.ljust(widths[index]) for index, cell in enumerate(row)))
