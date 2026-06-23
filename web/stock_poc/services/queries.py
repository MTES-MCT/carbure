from collections.abc import Callable

from django.db.models import QuerySet

from core.models import Entity
from stock_poc.models import Action
from stock_poc.services.balance import (
    with_available,
)


def in_physical_stock_actions(entity: Entity) -> QuerySet:
    """All actions with available balance."""
    return (
        with_available()
        .filter(type=Action.CREATION_H2, owner=entity)
        .filter(available__gt=0)
        .select_related("owner", "parent")
    )


def available_for_certificates(entity: Entity) -> QuerySet:
    """Validated consumptions that act as transferable certificates."""
    return with_available().filter(type=Action.CONSOMMATION, status=Action.ACCEPTED, owner=entity).filter(available__gt=0)


def owned_actions(entity: Entity) -> QuerySet:
    """All actions owned by the entity, with available balance."""
    return with_available(Action.objects.filter(owner=entity)).select_related("owner", "parent")


def sent_transfers(entity: Entity) -> QuerySet:
    """TRANSFERT actions emitted by the entity (parent owned by entity)."""
    return (
        with_available()
        .filter(type=Action.TRANSFERT, parent__owner=entity)
        .select_related("owner", "parent", "parent__owner")
    )


def received_transfers(entity: Entity) -> QuerySet:
    """TRANSFERT actions received by the entity (owner = entity)."""
    return with_available().filter(type=Action.TRANSFERT, owner=entity).select_related("owner", "parent", "parent__owner")


def all_actions() -> QuerySet:
    """All POC actions (global debug view)."""
    return with_available(Action.objects.all()).select_related("owner", "parent")


class Scenario:
    def __init__(self, help: str, query: Callable[..., QuerySet], requires_entity: bool = True):
        self.help = help
        self.query = query
        self.requires_entity = requires_entity


SCENARIOS: dict[str, Scenario] = {
    "consumption": Scenario(
        help="Stock physique consommable (CREATION_H2 avec solde > 0)",
        query=in_physical_stock_actions,
    ),
    "certificates": Scenario(
        help="Certificats (CONSOMMATION ACCEPTED avec solde > 0)",
        query=available_for_certificates,
    ),
    "owned": Scenario(
        help="Toutes les actions dont l'entité est propriétaire",
        query=owned_actions,
    ),
    "sent": Scenario(
        help="Transferts émis (TRANSFERT dont le parent appartient à l'entité)",
        query=sent_transfers,
    ),
    "received": Scenario(
        help="Transferts reçus (TRANSFERT dont l'entité est propriétaire)",
        query=received_transfers,
    ),
    "all": Scenario(
        help="Toutes les actions du POC (sans filtre entité)",
        query=all_actions,
        requires_entity=False,
    ),
}
