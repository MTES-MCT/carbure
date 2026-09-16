from csv import DictReader
from decimal import Decimal, InvalidOperation
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from traceability.models import Material

DEFAULT_CSV = Path(__file__).resolve().parents[2] / "fixtures" / "materials.csv"


class Command(BaseCommand):
    # uv run python web/manage.py import_materials
    help = "Import the materials catalogue from CSV (update_or_create by code)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--file",
            type=Path,
            default=DEFAULT_CSV,
            help="CSV path (default: traceability/fixtures/materials.csv)",
        )
        parser.add_argument(
            "--dry-run",
            choices=["true", "false"],
            default="true",
            help="Simulate changes without saving (default: true)",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"] == "true"
        filepath: Path = options["file"]
        if not filepath.is_file():
            raise CommandError(f"File not found: {filepath}")

        created = updated = 0
        with transaction.atomic():
            for row in _read_rows(filepath):
                material = (
                    Material.objects.filter(code=row["code"]).first() or Material.objects.filter(name=row["name"]).first()
                )
                if material is None:
                    Material.objects.create(**row)
                    created += 1
                    verb = "create"
                else:
                    material.code = row["code"]
                    material.name = row["name"]
                    material.lhv = row["lhv"]
                    material.density = row["density"]
                    material.save(update_fields=["code", "name", "lhv", "density"])
                    updated += 1
                    verb = "update"
                self.stdout.write(f"  {verb} {row['code']} ({row['name']}) lhv={row['lhv']} density={row['density']}")

            if dry_run:
                transaction.set_rollback(True)
                self.stdout.write(self.style.WARNING("Dry run: nothing saved."))

        self.stdout.write(self.style.SUCCESS(f"{created} created, {updated} updated."))


def _read_rows(filepath: Path):
    with filepath.open(newline="", encoding="utf-8-sig") as csvfile:
        reader = DictReader(csvfile)
        missing = {"code", "name", "lhv", "density"} - set(reader.fieldnames or [])
        if missing:
            raise CommandError(f"Missing CSV columns: {', '.join(sorted(missing))}")
        for line, row in enumerate(reader, start=2):
            code = (row.get("code") or "").strip()
            name = (row.get("name") or "").strip()
            if not code or not name:
                raise CommandError(f"Line {line}: code and name are required")
            yield {
                "code": code,
                "name": name,
                "lhv": _decimal_or_none(row.get("lhv"), line, "lhv"),
                "density": _decimal_or_none(row.get("density"), line, "density"),
            }


def _decimal_or_none(value: str | None, line: int, field: str) -> Decimal | None:
    stripped = (value or "").strip()
    if not stripped:
        return None
    try:
        parsed = Decimal(stripped)
    except InvalidOperation as exc:
        raise CommandError(f"Line {line}: invalid {field} {stripped!r}") from exc
    if parsed <= 0:
        raise CommandError(f"Line {line}: {field} must be empty or > 0")
    return parsed
