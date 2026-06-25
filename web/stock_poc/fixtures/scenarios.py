from typing import TypedDict

from stock_poc.models import Action
from stock_poc.models.action_status import ActionStatus


class EntityFixture(TypedDict):
    key: str
    name: str


class ActionFixture(TypedDict, total=False):
    type: str
    quantity: str | int | float
    owner: str
    status: str | None
    children: list["ActionFixture"]


class ScenarioFixture(TypedDict):
    description: str
    default_entity: str
    roots: list[ActionFixture]


ENTITIES: list[EntityFixture] = [
    {"key": "entity_a", "name": "POC Stock Entity A"},
    {"key": "entity_b", "name": "POC Stock Entity B"},
    {"key": "entity_c", "name": "POC Stock Entity C"},
]

SCENARIO_FIXTURES: dict[str, ScenarioFixture] = {
    "scenario_1": {
        "description": (
            "H2 — 1000 kg créés, 700 + 150 kg consommés et validés en certificats, "
            "transfert 100 kg accepté par B, transfert 150 kg refusé par C."
        ),
        "default_entity": "entity_a",
        "roots": [
            {
                "type": Action.CREATION_H2,
                "quantity": "1000",
                "owner": "entity_a",
                "children": [
                    {
                        "type": Action.CONSOMMATION,
                        "quantity": "700",
                        "status": ActionStatus.ACCEPTED,
                        "children": [
                            {
                                "type": Action.TRANSFERT,
                                "quantity": "100",
                                "owner": "entity_b",
                                "status": ActionStatus.ACCEPTED,
                            },
                        ],
                    },
                    {
                        "type": Action.CONSOMMATION,
                        "quantity": "150",
                        "status": ActionStatus.ACCEPTED,
                        "children": [
                            {
                                "type": Action.TRANSFERT,
                                "quantity": "150",
                                "owner": "entity_c",
                                "status": ActionStatus.REFUSED,
                            },
                        ],
                    },
                ],
            },
        ],
    },
    "scenario_3": {
        "description": "H2 — 500 kg, 490 kg validés en certificat, 10 kg en perte.",
        "default_entity": "entity_a",
        "roots": [
            {
                "type": Action.CREATION_H2,
                "quantity": "500",
                "owner": "entity_a",
                "children": [
                    {"type": Action.CONSOMMATION, "quantity": "490", "status": ActionStatus.ACCEPTED},
                    {"type": Action.PERTE, "quantity": "10"},
                ],
            },
        ],
    },
}


def count_actions(actions: list[ActionFixture]) -> int:
    total = 0
    for action in actions:
        total += 1
        total += count_actions(action.get("children", []))
    return total


def entity_name_for_key(key: str) -> str:
    for entity in ENTITIES:
        if entity["key"] == key:
            return entity["name"]
    raise KeyError(f"Unknown entity key: {key}")
