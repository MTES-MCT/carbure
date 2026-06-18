import json
from dataclasses import dataclass

from django.apps import apps
from django.core.exceptions import FieldDoesNotExist
from django.core.management.base import BaseCommand, CommandError
from django.db import models, transaction

from core.models import Entity

MIGRATED_ENTITY_FIELDS = (
    # Core access/config
    ("core", "ExternalAdminRights", "entity"),
    ("core", "SustainabilityDeclaration", "entity"),
    ("core", "EntityCertificate", "entity"),
    ("core", "CarbureNotification", "dest"),
    ("core", "UserPreferences", "default_entity"),
    ("core", "UserRights", "entity"),
    ("core", "UserRightsRequests", "entity"),
    ("entity", "EntityScope", "entity"),
    # Transactions/sites
    ("transactions", "Site", "created_by"),
    ("transactions", "EntitySite", "entity"),
    ("transactions", "EntitySite", "blender"),
    # Biofuel lots/stocks
    ("core", "CarbureLot", "carbure_producer"),
    ("core", "CarbureLot", "carbure_supplier"),
    ("core", "CarbureLot", "carbure_vendor"),
    ("core", "CarbureLot", "carbure_client"),
    ("core", "CarbureLot", "added_by"),
    ("core", "CarbureLotEvent", "entity"),
    ("core", "CarbureLotComment", "entity"),
    ("core", "CarbureStock", "carbure_client"),
    ("core", "CarbureStock", "carbure_supplier"),
    ("core", "CarbureStockEvent", "entity"),
    ("core", "CarbureStockTransformation", "entity"),
    # Certificates/double-counting
    ("certificates", "ProductionSiteCertificate", "entity"),
    ("doublecount", "DoubleCountingApplication", "producer"),
    # Biomethane
    ("biomethane", "BiomethaneContract", "buyer"),
    ("biomethane", "BiomethaneContract", "producer"),
    ("biomethane", "BiomethaneProductionUnit", "producer"),
    ("biomethane", "BiomethaneInjectionSite", "producer"),
    ("biomethane", "BiomethaneAnnualDeclaration", "producer"),
    ("biomethane", "BiomethaneSupplyPlan", "producer"),
    ("biomethane", "BiomethaneEnergy", "producer"),
    ("biomethane", "BiomethaneDigestate", "producer"),
    ("biomethane", "BiomethaneDigestateStorage", "producer"),
    # Elec
    ("elec", "ElecAuditSample", "cpo"),
    ("elec", "ElecAuditSample", "auditor"),
    ("elec", "ElecCertificateReadjustment", "cpo"),
    ("elec", "ElecChargePoint", "cpo"),
    ("elec", "ElecChargePointApplication", "cpo"),
    ("elec", "ElecMeterReading", "cpo"),
    ("elec", "ElecMeterReadingApplication", "cpo"),
    ("elec", "ElecProvisionCertificate", "cpo"),
    ("elec", "ElecProvisionCertificateQualicharge", "cpo"),
    ("elec", "ElecTransferCertificate", "supplier"),
    ("elec", "ElecTransferCertificate", "client"),
    # SAF
    ("saf", "SafTicket", "supplier"),
    ("saf", "SafTicket", "client"),
    ("saf", "SafTicket", "carbure_producer"),
    ("saf", "SafTicketSource", "added_by"),
    ("saf", "SafTicketSource", "carbure_producer"),
    # TIRUERT
    ("tiruert", "MacFossilFuel", "operator"),
    ("tiruert", "ObjectiveSnapshot", "entity"),
    ("tiruert", "Operation", "credited_entity"),
    ("tiruert", "Operation", "debited_entity"),
    ("tiruert", "ElecOperation", "credited_entity"),
    ("tiruert", "ElecOperation", "debited_entity"),
)


class Command(BaseCommand):
    help = """
    Migrate configured Entity references from one Entity to another.

    Command: python web/manage.py migrate_entity_ownership <source_entity> <target_entity> --apply
    """

    def add_arguments(self, parser):
        parser.add_argument("source_entity", type=str)
        parser.add_argument("target_entity", type=str)
        parser.add_argument(
            "--apply",
            action="store_true",
            default=False,
            help="Apply updates. By default, runs in dry-run mode.",
        )

    def handle(self, *args, **options):
        source_name = options["source_entity"]
        target_name = options["target_entity"]
        apply_updates = options["apply"]

        if source_name == target_name:
            raise CommandError("Source and target entities must be different.")

        source = self.get_entity(source_name)
        target = self.get_entity(target_name)
        migrated_fields = validate_migrated_entity_fields()

        report = build_report(source, target, migrated_fields)

        if apply_updates:
            with transaction.atomic():
                report = build_report(source, target, migrated_fields)
                updated_counts = apply_entity_migration(source, target, migrated_fields)
                for field_report in report["fields"]:
                    field_report["updated"] = updated_counts.get(field_report["key"], 0)

        return json.dumps(report, sort_keys=True)

    def get_entity(self, entity_name):
        try:
            return Entity.all_objects.get(name=entity_name)
        except Entity.DoesNotExist as exc:
            raise CommandError(f"Entity {entity_name} does not exist.") from exc


@dataclass(frozen=True)
class MigratedField:
    model: type[models.Model]
    field: models.Field

    @property
    def label(self):
        return self.model._meta.label

    @property
    def key(self):
        return f"{self.label}.{self.field.name}"

    @property
    def manager(self):
        if self.model is Entity:
            return Entity.all_objects
        return self.model._default_manager

    def query(self, entity):
        return self.manager.filter(**{self.field.name: entity})

    def count(self, entity):
        return self.query(entity).count()

    def update(self, source, target):
        return self.query(source).update(**{self.field.name: target})

    def report(self, source, target):
        return {
            "key": self.key,
            "model": self.label,
            "field": self.field.name,
            "source_count": self.count(source),
            "target_count": self.count(target),
            "updated": 0,
        }


def validate_migrated_entity_fields():
    migrated_fields = []

    for app_label, model_name, field_name in MIGRATED_ENTITY_FIELDS:
        try:
            model = apps.get_model(app_label, model_name)
        except LookupError as exc:
            raise CommandError(f"Unknown model in MIGRATED_ENTITY_FIELDS: {app_label}.{model_name}") from exc

        try:
            field = model._meta.get_field(field_name)
        except FieldDoesNotExist as exc:
            raise CommandError(f"Unknown field in MIGRATED_ENTITY_FIELDS: {model._meta.label}.{field_name}") from exc

        if not field.is_relation or field.remote_field.model != Entity:
            raise CommandError(f"Configured field does not point to core.Entity: {model._meta.label}.{field_name}")

        migrated_fields.append(MigratedField(model=model, field=field))

    return migrated_fields


def build_report(source, target, migrated_fields):
    return {
        "source_entity": source.name,
        "target_entity": target.name,
        "fields": [migrated_field.report(source, target) for migrated_field in migrated_fields],
    }


def apply_entity_migration(source, target, migrated_fields):
    updated_counts = {}

    for migrated_field in migrated_fields:
        updated_counts[migrated_field.key] = migrated_field.update(source, target)

    return updated_counts
