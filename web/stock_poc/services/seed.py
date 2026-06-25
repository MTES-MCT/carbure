from django.db import transaction

from core.models import Entity
from stock_poc.fixtures.scenarios import (
    ENTITIES,
    SCENARIO_FIXTURES,
    ActionFixture,
    entity_name_for_key,
)
from stock_poc.models import Action
from stock_poc.models.action_status import ActionStatus


def ensure_entities() -> dict[str, Entity]:
    entities: dict[str, Entity] = {}
    for entity_fixture in ENTITIES:
        entity, _ = Entity.objects.get_or_create(
            name=entity_fixture["name"],
            defaults={"entity_type": Entity.UNKNOWN},
        )
        entities[entity_fixture["key"]] = entity
    return entities


def _create_action_tree(
    fixture: ActionFixture,
    *,
    entities: dict[str, Entity],
    default_entity: str,
    parent: Action | None = None,
) -> Action:
    owner_key = fixture.get("owner", default_entity)
    action = Action.objects.create(
        type=fixture["type"],
        quantity=fixture["quantity"],
        owner=entities[owner_key],
        parent=parent,
    )
    status = fixture.get("status")
    if status is not None:
        ActionStatus.objects.create(action=action, status=status)
    for child_fixture in fixture.get("children", []):
        _create_action_tree(
            child_fixture,
            entities=entities,
            default_entity=default_entity,
            parent=action,
        )
    return action


def seed_scenario(scenario_name: str, *, dry_run: bool = False) -> dict[str, Entity]:
    scenario = SCENARIO_FIXTURES.get(scenario_name)
    if scenario is None:
        available = ", ".join(sorted(SCENARIO_FIXTURES))
        raise ValueError(f"Unknown scenario '{scenario_name}'. Available: {available}")

    with transaction.atomic():
        entities = ensure_entities()

        if dry_run:
            transaction.set_rollback(True)

        for root_fixture in scenario["roots"]:
            _create_action_tree(
                root_fixture,
                entities=entities,
                default_entity=scenario["default_entity"],
            )

    return entities


def get_entity_by_key(key: str) -> Entity:
    return Entity.objects.get(name=entity_name_for_key(key))
