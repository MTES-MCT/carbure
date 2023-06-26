from django.http import JsonResponse
from core.decorators import check_admin_rights
from core.models import Entity, EntityCertificate, ExternalAdminRights
from django.db.models import Q, Count, Value


from doublecount.models import DoubleCountingApplication


@check_admin_rights(allow_external=[ExternalAdminRights.AIRLINE, ExternalAdminRights.ELEC])
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
                certificates_pending=Count(
                    "entitycertificate",
                    filter=Q(entitycertificate__checked_by_admin=False),
                    distinct=True,
                ),
                double_counting=Count(
                    "doublecountingapplication",
                    filter=Q(doublecountingapplication__status=DoubleCountingApplication.ACCEPTED),
                    distinct=True,
                ),
                double_counting_requests=Count(
                    "doublecountingapplication",
                    filter=Q(doublecountingapplication__status=DoubleCountingApplication.PENDING),
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
                certificates_pending=Value(0),
            )
        )
    elif entity.has_external_admin_right("ELEC"):
        entities = (
            Entity.objects.all()
            .order_by("name")
            .filter(Q(entity_type=Entity.CPO) | Q(entity_type=Entity.OPERATOR, has_elec=True))
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
                "certificates_pending": e.certificates_pending,
            }
        )
    return JsonResponse({"status": "success", "data": entities_sez})
