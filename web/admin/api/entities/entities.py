from django.http import JsonResponse
from core.decorators import check_admin_rights
from core.models import Entity, ExternalAdminRights
from django.db.models import Q, Count, Value


from doublecount.models import DoubleCountingAgreement
from core.helpers import filter_lots


@check_admin_rights(allow_external=[ExternalAdminRights.AIRLINE])
def get_entities(request):
    q = request.GET.get("q", False)
    entity_id = request.GET.get("entity_id", None)
    has_requests = request.GET.get("has_requests", None)

    entity = Entity.objects.get(id=entity_id)

    if entity.entity_type == entity.ADMIN:
        entities = (
            Entity.objects.all()
            .order_by("name")
            .prefetch_related(
                "userrights_set",
                "userrightsrequests_set",
                "entitydepot_set",
                "productionsite_set",
            )
            .annotate(
                users=Count("userrights", distinct=True),
                requests=Count(
                    "userrightsrequests",
                    filter=Q(userrightsrequests__status="PENDING"),
                    distinct=True,
                ),
                depots=Count("entitydepot", distinct=True),
                production_sites=Count("productionsite", distinct=True),
                certificates=Count("entitycertificate", distinct=True),
                double_counting=Count(
                    "doublecountingagreement",
                    filter=Q(
                        doublecountingagreement__status=DoubleCountingAgreement.ACCEPTED
                    ),
                    distinct=True,
                ),
                double_counting_requests=Count(
                    "doublecountingagreement",
                    filter=Q(
                        doublecountingagreement__status=DoubleCountingAgreement.PENDING
                    ),
                    distinct=True,
                ),
            )
        )
    elif entity.has_external_admin_right("AIRLINE"):
        entities = (
            Entity.objects.all()
            .order_by("name")
            .filter(entity_type=Entity.AIRLINE)
            .prefetch_related("userrights_set", "userrightsrequests_set")
            .annotate(
                users=Count("userrights", distinct=True),
                requests=Count(
                    "userrightsrequests",
                    filter=Q(userrightsrequests__status="PENDING"),
                    distinct=True,
                ),
                depots=Value(0),
                production_sites=Value(0),
                certificates=Value(0),
                double_counting=Value(0),
                double_counting_requests=Value(0),
            )
        )

    if q:
        entities = entities.filter(name__icontains=q)
    if has_requests == "true":
        entities = entities.filter(requests__gt=0)

    entities_sez = []
    for e in entities.iterator():
        entities_sez.append(
            {
                "entity": e.natural_key(),
                "users": e.users,
                "requests": e.requests,
                "depots": e.depots,
                "production_sites": e.production_sites,
                "certificates": e.certificates,
                "double_counting": e.double_counting,
                "double_counting_requests": e.double_counting_requests,
            }
        )
    return JsonResponse({"status": "success", "data": entities_sez})