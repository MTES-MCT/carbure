"""Sum GES from an action up to the root of its parent chain.

Walkthrough (example + equivalent SQL): ``traceability/docs/total_emissions.md``.

One SQL statement: WITH RECURSIVE (climb + accumulate) then SELECT (keep the
row that reached the root, attach it to the action). Formula on the path sums:

    total = eec + el + ei + ep + etd + eu - eccs - esca - eccr
"""

from django.db.models import F, QuerySet
from django.db.models.functions import JSONObject
from django_cte import CTE, with_cte

from traceability.models.action import Action


def _plain_actions():
    # Recursive CTE: no Meta.ordering, no status subqueries (MySQL rejects both).
    return Action.unannotated.all().order_by()


def _parent_path_cte(queryset: QuerySet[Action]) -> CTE:
    """Climb parent → parent, adding GES at each step. At the root, next_parent_id is NULL."""
    actions = _plain_actions()
    listed = actions.filter(pk__in=queryset)

    def walk(cte):
        start_from_listed = listed.values(
            origin_id=F("id"),
            next_parent_id=F("parent_id"),
            eec_sum=F("eec"),
            el_sum=F("el"),
            ei_sum=F("ei"),
            ep_sum=F("ep"),
            etd_sum=F("etd"),
            eu_sum=F("eu"),
            eccs_sum=F("eccs"),
            esca_sum=F("esca"),
            eccr_sum=F("eccr"),
        )
        climb_to_parent = cte.join(actions, id=cte.col.next_parent_id).values(
            origin_id=cte.col.origin_id,
            next_parent_id=F("parent_id"),
            eec_sum=cte.col.eec_sum + F("eec"),
            el_sum=cte.col.el_sum + F("el"),
            ei_sum=cte.col.ei_sum + F("ei"),
            ep_sum=cte.col.ep_sum + F("ep"),
            etd_sum=cte.col.etd_sum + F("etd"),
            eu_sum=cte.col.eu_sum + F("eu"),
            eccs_sum=cte.col.eccs_sum + F("eccs"),
            esca_sum=cte.col.esca_sum + F("esca"),
            eccr_sum=cte.col.eccr_sum + F("eccr"),
        )
        return start_from_listed.union(climb_to_parent, all=True)

    return CTE.recursive(walk)


def annotate_total_emissions(queryset: QuerySet[Action]) -> QuerySet[Action]:
    cte = _parent_path_cte(queryset)
    at_root = (
        cte.join(queryset, id=cte.col.origin_id)
        .annotate(
            total_emissions=JSONObject(
                eec=cte.col.eec_sum,
                el=cte.col.el_sum,
                ei=cte.col.ei_sum,
                ep=cte.col.ep_sum,
                etd=cte.col.etd_sum,
                eu=cte.col.eu_sum,
                eccs=cte.col.eccs_sum,
                esca=cte.col.esca_sum,
                eccr=cte.col.eccr_sum,
                total=(
                    cte.col.eec_sum
                    + cte.col.el_sum
                    + cte.col.ei_sum
                    + cte.col.ep_sum
                    + cte.col.etd_sum
                    + cte.col.eu_sum
                    - cte.col.eccs_sum
                    - cte.col.esca_sum
                    - cte.col.eccr_sum
                ),
            ),
            _next_parent_id=cte.col.next_parent_id,
        )
        .filter(_next_parent_id__isnull=True)
        .order_by("id")
    )
    return with_cte(cte, select=at_root)
