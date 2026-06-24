from django.core.management.base import BaseCommand, CommandError

from core.models import Entity
from stock_poc.fixtures.scenarios import ENTITIES
from stock_poc.models import Action
from stock_poc.services.queries import QUERY_ORDER, SCENARIOS

HEADERS = ["id", "type", "status", "quantity", "available", "owner", "parent"]


class Command(BaseCommand):
    """
    Run stock POC query scenarios and print results in the terminal.

    Examples:
        uv run python web/manage.py query_stock_poc
        uv run python web/manage.py query_stock_poc --list
        uv run python web/manage.py query_stock_poc --scenario consumption --entity-id 1
    """

    help = "Run stock POC query scenarios and print matching actions"

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
            self._print_all()
            return

        self._run_single(scenario_name, options.get("entity_id"))

    def _print_all(self):
        if not Action.objects.exists():
            self.stdout.write("Aucune action en base.")
            self.stdout.write("Lancez d'abord : uv run python web/manage.py seed_stock_poc --scenario <name>")
            return

        entities = self._get_poc_entities()
        self.stdout.write("")
        self.stdout.write(self.style.HTTP_INFO(" Stock POC — requêtes "))
        self.stdout.write(f" {Action.objects.count()} action(s) en base")
        self.stdout.write("")

        for name in QUERY_ORDER:
            scenario = SCENARIOS[name]
            if scenario.requires_entity:
                for entity in entities:
                    self._print_block(name, scenario, entity)
            else:
                self._print_block(name, scenario, None)

    def _run_single(self, scenario_name: str, entity_id: int | None):
        scenario = SCENARIOS.get(scenario_name)
        if scenario is None:
            available = ", ".join(sorted(SCENARIOS))
            raise CommandError(f"Unknown scenario '{scenario_name}'. Available: {available}")

        entity = None
        if scenario.requires_entity:
            if entity_id is None:
                raise CommandError(f"Scenario '{scenario_name}' requires --entity-id.")
            try:
                entity = Entity.objects.get(pk=entity_id)
            except Entity.DoesNotExist as exc:
                raise CommandError(f"Entity #{entity_id} not found.") from exc

        self._print_block(scenario_name, scenario, entity)

    def _print_block(self, name: str, scenario, entity: Entity | None):
        queryset = scenario.query(entity) if scenario.requires_entity else scenario.query()
        actions = list(queryset)

        title = name
        if entity:
            title += f" · {entity.name} (#{entity.id})"

        self.stdout.write("─" * 72)
        self.stdout.write(self.style.MIGRATE_HEADING(title))
        self.stdout.write(scenario.help)

        if not actions:
            self.stdout.write(self.style.WARNING("  (aucun résultat)"))
            self.stdout.write("")
            return

        self.stdout.write(f"  {len(actions)} résultat(s)")
        rows = [self._format_row(action) for action in actions]
        self._print_table(HEADERS, rows)
        self.stdout.write("")

    def _print_scenarios(self):
        self.stdout.write("Scénarios disponibles :\n")
        for name in QUERY_ORDER:
            scenario = SCENARIOS[name]
            entity_hint = "nécessite --entity-id" if scenario.requires_entity else "global"
            self.stdout.write(f"  {name:14} [{entity_hint}]")
            self.stdout.write(f"    {scenario.help}")
        self.stdout.write("")
        self.stdout.write("Sans argument : exécute tous les scénarios pour les entités POC.")

    def _get_poc_entities(self) -> list[Entity]:
        names = [entity["name"] for entity in ENTITIES]
        return list(Entity.objects.filter(name__in=names).order_by("name"))

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
        self.stdout.write("  " + header_line)
        self.stdout.write("  " + "─" * len(header_line))

        for row in rows:
            self.stdout.write("  " + "  ".join(cell.ljust(widths[index]) for index, cell in enumerate(row)))
