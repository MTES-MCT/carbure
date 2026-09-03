from django.db.models import F, QuerySet
from django.db.models.functions import JSONObject
from django_cte import CTE, with_cte

from traceability.models.action import Action


def _emissions_cte(queryset: QuerySet[Action]) -> CTE:
    table = Action.objects.unannotated().order_by()
    origins = table.filter(pk__in=queryset.values("pk"))

    def make_cte(cte):
        return origins.values(
            origin_id=F("id"),
            ancestor_id=F("id"),
            next_parent_id=F("parent_id"),
            ei_sum=F("ei"),
            ep_sum=F("ep"),
            etd_sum=F("etd"),
            eu_sum=F("eu"),
            eccs_sum=F("eccs"),
        ).union(
            cte.join(table, id=cte.col.next_parent_id).values(
                origin_id=cte.col.origin_id,
                ancestor_id=F("id"),
                next_parent_id=F("parent_id"),
                ei_sum=cte.col.ei_sum + F("ei"),
                ep_sum=cte.col.ep_sum + F("ep"),
                etd_sum=cte.col.etd_sum + F("etd"),
                eu_sum=cte.col.eu_sum + F("eu"),
                eccs_sum=cte.col.eccs_sum + F("eccs"),
            ),
            all=True,
        )

    return CTE.recursive(make_cte)


def parent_chain(queryset: QuerySet[Action]) -> QuerySet:
    """Walk from each action up to the root, one CTE row per ancestor.

    `origin_id` is the action we started from; `ancestor_id` is the node on the
    path (including the origin). GES are accumulated along the climb.
    """
    cte = _emissions_cte(queryset)
    return with_cte(cte, select=cte).order_by()


def annotate_total_emissions(queryset: QuerySet[Action]) -> QuerySet[Action]:
    """Annotate each action with total_emissions accumulated along the parent chain."""
    cte = _emissions_cte(queryset)
    # Join onto the default manager so select_related and status annotations
    # are kept (the CTE body itself must stay unannotated).
    origins = Action.objects.filter(pk__in=queryset).order_by()

    select = (
        cte.join(origins, id=cte.col.origin_id)
        .annotate(
            ei_sum=cte.col.ei_sum,
            ep_sum=cte.col.ep_sum,
            etd_sum=cte.col.etd_sum,
            eu_sum=cte.col.eu_sum,
            eccs_sum=cte.col.eccs_sum,
            cte_next_parent_id=cte.col.next_parent_id,
            total_emissions=JSONObject(
                ei=cte.col.ei_sum,
                ep=cte.col.ep_sum,
                etd=cte.col.etd_sum,
                eu=cte.col.eu_sum,
                eccs=cte.col.eccs_sum,
                total=(cte.col.ei_sum + cte.col.ep_sum + cte.col.etd_sum + cte.col.eu_sum - cte.col.eccs_sum),
            ),
        )
        .filter(cte_next_parent_id__isnull=True)
        .order_by("id")
    )
    return with_cte(cte, select=select)
