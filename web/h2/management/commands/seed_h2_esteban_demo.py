from datetime import date
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from core.factories.sample_data import set_user_access, setup_admin_user, setup_regular_user
from core.models import Entity
from h2.factories.sample_data import setup_h2_entity, setup_h2_materials
from traceability.factories import ActionFactory
from traceability.models import Action, Industry
from traceability.models.action_status import ActionStatus

PREFIX = "H2-ESTEBAN-"
RECIPIENT_NAME = "Opérateur redevable démo"
WORKING_DATE = date(2026, 11, 1)


class Command(BaseCommand):
    """Disposable rows for the Volumes H2 and Certificats envoyés screens.

    uv run python web/manage.py seed_h2_esteban_demo
    uv run python web/manage.py seed_h2_esteban_demo --dry-run
    uv run python web/manage.py seed_h2_esteban_demo --delete

    Delete this file once the demo is over. --delete removes the rows it created.
    """

    help = "Create disposable H2 volumes and sent certificates for a demo."

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true", help="Print the rows without saving them.")
        parser.add_argument("--delete", action="store_true", help="Remove the rows created by this command.")

    def handle(self, *args, **options):
        with transaction.atomic():
            if options["delete"]:
                self.delete_demo()
            else:
                self.seed()
            if options["dry_run"]:
                transaction.set_rollback(True)
                self.stdout.write("Simulation : rien n'a été enregistré.")

    def seed(self):
        holder = setup_h2_entity()
        renewable, bio = setup_h2_materials()
        recipient = self.recipient()
        set_user_access(setup_admin_user(), recipient, "RW")
        set_user_access(setup_regular_user(), recipient, "RW")

        intact = self.certificate("INTACT", holder, renewable, Decimal("1000"))
        partial = self.certificate("PARTIAL", holder, bio, Decimal("1000"))
        exhausted = self.certificate("EXHAUSTED", holder, renewable, Decimal("1000"))

        pending = self.transfer("PENDING", partial, recipient, Decimal("400"), ActionStatus.PENDING)
        accepted = self.transfer("ACCEPTED", exhausted, recipient, Decimal("600"), ActionStatus.ACCEPTED)
        rejected = self.transfer("REJECTED", exhausted, recipient, Decimal("400"), ActionStatus.REJECTED)

        self.stdout.write(f"Station : {holder.name} (id {holder.id})")
        self.stdout.write(f"Redevable : {recipient.name} (id {recipient.id})")
        self.stdout.write(f"Volume intact {intact.id} — 1000 kg, statut Disponible")
        self.stdout.write(f"Volume entamé {partial.id} — 1000 kg, cession en attente {pending.id} de 400 kg")
        self.stdout.write(f"Volume épuisé {exhausted.id}")
        self.stdout.write(f"Cession acceptée {accepted.id} de 600 kg, cession refusée {rejected.id} de 400 kg")

    def delete_demo(self):
        consumes = Action.unannotated.filter(pos_id__startswith=PREFIX, type=Action.CONSUME)
        certificates = Action.unannotated.filter(parent__in=consumes, type=Action.VALORIZE)
        transfers = Action.unannotated.filter(parent__in=certificates)
        transfer_count = transfers.count()
        certificate_count = certificates.count()
        consume_count = consumes.count()
        transfers.delete()
        certificates.delete()
        consumes.delete()
        self.stdout.write(
            f"Supprimé : {transfer_count} cessions, {certificate_count} volumes, {consume_count} lots parents."
        )

    def recipient(self) -> Entity:
        recipient, _created = Entity.objects.get_or_create(
            name=RECIPIENT_NAME,
            defaults={"entity_type": Entity.OPERATOR, "is_tiruert_liable": True},
        )
        if not recipient.is_tiruert_liable:
            recipient.is_tiruert_liable = True
            recipient.save(update_fields=["is_tiruert_liable"])
        return recipient

    def certificate(self, key: str, holder: Entity, material, quantity: Decimal) -> Action:
        parent = ActionFactory(
            pos_id=f"{PREFIX}{key}",
            holder=holder,
            industry=Industry.H2,
            type=Action.CONSUME,
            material=material,
            quantity=quantity,
            site=None,
            shipping_date=None,
            shipping_distance=None,
            shipping_method=None,
            working_date=WORKING_DATE,
            ei=Decimal("1.5"),
            status=ActionStatus.ACCEPTED,
        )
        certificate, _created = Action.unannotated.get_or_create(
            parent=parent,
            type=Action.VALORIZE,
            defaults={
                "holder": holder,
                "industry": Industry.H2,
                "quantity": quantity,
                "working_date": WORKING_DATE,
                "material": None,
                "site": None,
                "ei": Decimal("1.5"),
            },
        )
        ActionStatus.objects.get_or_create(action=certificate, status=ActionStatus.CREATED)
        return certificate

    def transfer(self, key: str, parent: Action, recipient: Entity, quantity: Decimal, status: str) -> Action:
        return ActionFactory(
            pos_id=f"{PREFIX}TRANSFER-{key}",
            parent=parent,
            holder=recipient,
            industry=Industry.H2,
            type=Action.TRANSFER,
            material=None,
            quantity=quantity,
            site=None,
            shipping_date=None,
            shipping_distance=None,
            shipping_method=None,
            working_date=WORKING_DATE,
            status=status,
        )
