"""GES columns carried by the shared parent-chain CTE.

The recursive walk itself lives in ``services/parent_chain.py``.
Walkthrough: ``traceability/docs/total_emissions.md``.

    total = eec + el + ei + ep + etd + eu - eccs - esca - eccr
"""

from django.db.models import F, QuerySet
from django.db.models.functions import JSONObject

from traceability.models.action import Action

GES_FIELDS = ("eec", "el", "ei", "ep", "etd", "eu", "eccs", "esca", "eccr")


def emission_start() -> dict:
    return {f"{name}_sum": F(name) for name in GES_FIELDS}


def emission_climb(cte) -> dict:
    return {f"{name}_sum": getattr(cte.col, f"{name}_sum") + F(name) for name in GES_FIELDS}


def emission_annotation(cte) -> dict:
    def value(name):
        return getattr(cte.col, f"{name}_sum")

    total = (
        value("eec")
        + value("el")
        + value("ei")
        + value("ep")
        + value("etd")
        + value("eu")
        - value("eccs")
        - value("esca")
        - value("eccr")
    )
    return {
        "total_emissions": JSONObject(
            eec=value("eec"),
            el=value("el"),
            ei=value("ei"),
            ep=value("ep"),
            etd=value("etd"),
            eu=value("eu"),
            eccs=value("eccs"),
            esca=value("esca"),
            eccr=value("eccr"),
            total=total,
        )
    }


def annotate_total_emissions(queryset: QuerySet[Action]) -> QuerySet[Action]:
    from traceability.services.parent_chain import annotate_parent_chain

    return annotate_parent_chain(queryset, climbers=("emissions",))
