import json
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils.translation import override

from core.services.model_translation_fields import get_verbose_fields_for_translation


class Command(BaseCommand):
    help = """
    Export static backend field labels to frontend translation files.

    Usage:
        python web/manage.py export_backend_inputs
        python web/manage.py export_backend_inputs --locales=fr,en
        python web/manage.py export_backend_inputs --modules=biomethane,saf
        python web/manage.py export_backend_inputs --locales-dir=/path/to/front/public/locales
    """

    def add_arguments(self, parser):
        parser.add_argument(
            "--locales",
            type=str,
            default="fr,en",
            help="Comma-separated locale list to export (default: fr,en).",
        )
        parser.add_argument(
            "--locales-dir",
            type=str,
            default=None,
            help="Path to frontend locales directory (default: <repo>/front/public/locales).",
        )
        parser.add_argument(
            "--modules",
            type=str,
            default="",
            help="Comma-separated Django app modules to export (default: biomethane).",
        )

    def handle(self, *args, **options):
        locales = [locale.strip() for locale in options["locales"].split(",") if locale.strip()]

        if not locales:
            raise CommandError("No locale provided. Use --locales=fr,en")

        modules = [module.strip() for module in options["modules"].split(",") if module.strip()]

        if not modules:
            raise CommandError("No module provided. Use --modules=biomethane,saf")

        locales_dir = Path(options["locales_dir"]) if options["locales_dir"] else self._default_locales_dir()

        if not locales_dir.exists():
            raise CommandError(f"Locales directory does not exist: {locales_dir}")

        for locale in locales:
            self._export_locale(locales_dir, locale, modules)

        self.stdout.write(self.style.SUCCESS(f"Export completed for locales: {', '.join(locales)}"))

    def _default_locales_dir(self) -> Path:
        return Path(settings.BASE_DIR).parent / "front" / "public" / "locales"

    def _export_locale(self, locales_dir: Path, locale: str, modules: list[str]):
        locale_dir = locales_dir / locale
        if not locale_dir.exists():
            raise CommandError(f"Locale directory does not exist: {locale_dir}")

        # Force the locale to be used for the translation
        with override(locale):
            try:
                backend_inputs = get_verbose_fields_for_translation(module_names=modules)
            except LookupError as exc:
                raise CommandError(str(exc)) from exc

        output_file = locale_dir / "backend_inputs.json"
        sorted_backend_inputs = dict(sorted(backend_inputs.items()))
        output_file.write_text(
            json.dumps(sorted_backend_inputs, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

        self.stdout.write(f"[{locale}] Wrote {len(sorted_backend_inputs)} labels to {output_file}")
