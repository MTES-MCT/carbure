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


QUERY_ORDER = ["consumption", "certificates", "sent", "received"]


SCENARIOS: dict[str, Scenario] = {
    "consumption": Scenario(
        help="En stock",
        query=in_physical_stock_actions,
    ),
    "certificates": Scenario(
        help="Certificats disponibles",
        query=available_for_certificates,
    ),
    "sent": Scenario(
        help="Certificats envoyés",
        query=sent_transfers,
    ),
    "received": Scenario(
        help="Certificats reçus (actuellement tous les transferts, pas de diff entre physique et comptable)",
        query=received_transfers,
    ),
}


def run_scenarios(*, entity: Entity | None = None) -> list[dict]:
    """Run all registered query scenarios (shared by CLI and API)."""
    results = []
    for name in QUERY_ORDER:
        scenario = SCENARIOS[name]
        if scenario.requires_entity:
            if entity is None:
                raise ValueError(f"Scenario '{name}' requires an entity.")
            queryset = scenario.query(entity)
            entity_id = entity.pk
        else:
            queryset = scenario.query()
            entity_id = None

        results.append(
            {
                "name": name,
                "help": scenario.help,
                "requires_entity": scenario.requires_entity,
                "entity_id": entity_id,
                "results": queryset,
            }
        )
    return results
