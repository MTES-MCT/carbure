from collections.abc import Callable

from django.db.models import QuerySet

from core.models import Entity
from stock_poc.models import Action
from stock_poc.services.balance import (
    with_available,
)


def available_for_consumption(entity: Entity) -> QuerySet:
    """Actions the entity can still consume (physical stock)."""
    return with_available().filter(type=Action.CONSOMMATION, owner=entity).select_related("owner", "parent")


def available_for_certificates(entity: Entity) -> QuerySet:
    """Accounting stock the entity can still transfer as certificates."""
    return with_available().filter(type=Action.VALORISATION, owner=entity).select_related("owner", "parent")


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
        help="Stock de l'entité marqués comme consommés",
        query=available_for_consumption,
    ),
    "certificates": Scenario(
        help="Stocks qui sont devenus des certificats",
        query=available_for_certificates,
    ),
    "sent": Scenario(
        help="Stocks de l'entité envoyés",
        query=sent_transfers,
    ),
    "received": Scenario(
        help="Stocks reçus",
        query=received_transfers,
    ),
    "all": Scenario(
        help="Toutes les actions du POC (sans filtre entité)",
        query=all_actions,
        requires_entity=False,
    ),
}
