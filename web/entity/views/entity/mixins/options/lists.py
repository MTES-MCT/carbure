from django.db.models import Count, Q, Value
from drf_spectacular.utils import OpenApiParameter, OpenApiTypes, extend_schema
from rest_framework.response import Response

from core.models import Entity, ExternalAdminRights
from doublecount.models import DoubleCountingApplication
from elec.models import ElecChargePointApplication, ElecMeterReadingApplication
from entity.serializers import EntityMetricsSerializer
from transactions.models import Depot, ProductionSite


class EntityListActionMixin:
    @extend_schema(
        parameters=[
            OpenApiParameter(
                "entity_id",
                OpenApiTypes.INT,
                OpenApiParameter.QUERY,
                description="Entity ID",
                required=True,
            ),
            OpenApiParameter(
                "q",
                OpenApiTypes.STR,
                OpenApiParameter.QUERY,
                description="Search query",
                required=False,
            ),
            OpenApiParameter(
                "has_requests",
                OpenApiTypes.BOOL,
                OpenApiParameter.QUERY,
                description="Has requests",
                required=False,
            ),
        ],
        responses=EntityMetricsSerializer(many=True),
    )
    def list(self, request):
        entity_id = self.request.query_params.get("entity_id")
        entity = Entity.objects.get(id=entity_id)
        q = request.query_params.get("q", None)
        has_requests = request.query_params.get("has_requests", None)
        entities = Entity.objects.all().order_by("name")

        # limit entities for DGAC
        if entity.has_external_admin_right("AIRLINE"):
            entities = entities.filter(entity_type=Entity.AIRLINE)

        # limit entities for Elec stuff
        if entity.has_external_admin_right("ELEC"):
            entities = entities.filter(Q(entity_type=Entity.CPO) | Q(entity_type=Entity.OPERATOR, has_elec=True))

        # limit entities related to double counting
        if entity.has_external_admin_right(ExternalAdminRights.DOUBLE_COUNTING):
            entities = entities.filter(entity_type=Entity.PRODUCER)

        # initialize counters for all expected values
        entities = entities.annotate(
            users=Value(0),
            requests=Value(0),
            depots=Value(0),
            production_sites=Value(0),
            certificates=Value(0),
            certificates_pending=Value(0),
            double_counting=Value(0),
            double_counting_requests=Value(0),
            charge_points_accepted=Value(0),
            charge_points_pending=Value(0),
            meter_readings_accepted=Value(0),
            meter_readings_pending=Value(0),
        )
        # count users and requests for available entities
        entities = entities.prefetch_related("userrights_set", "userrightsrequests_set").annotate(
            users=Count("userrights", distinct=True),
            requests=Count(
                "userrightsrequests",
                filter=Q(userrightsrequests__status="PENDING"),
                distinct=True,
            ),
        )

        # add info for elec stuff
        if entity.entity_type == Entity.ADMIN or entity.has_external_admin_right("ELEC"):
            entities = entities.annotate(
                charge_points_accepted=Count(
                    "elec_charge_point_applications",
                    filter=Q(elec_charge_point_applications__status=ElecChargePointApplication.ACCEPTED),
                    distinct=True,
                ),
                charge_points_pending=Count(
                    "elec_charge_point_applications",
                    filter=Q(elec_charge_point_applications__status=ElecChargePointApplication.PENDING),
                    distinct=True,
                ),
                meter_readings_accepted=Count(
                    "elec_meter_reading_applications",
                    filter=Q(elec_meter_reading_applications__status=ElecMeterReadingApplication.ACCEPTED),
                    distinct=True,
                ),
                meter_readings_pending=Count(
                    "elec_meter_reading_applications",
                    filter=Q(elec_meter_reading_applications__status=ElecMeterReadingApplication.PENDING),
                    distinct=True,
                ),
            )

        # add info only visible by full admins
        if entity.entity_type == Entity.ADMIN:
            entities = entities.prefetch_related("entitysite_set").annotate(
                depots=Count(
                    "entitysite",
                    filter=Q(entitysite__site__in=Depot.objects.all()),
                    distinct=True,
                ),
                production_sites=Count(
                    "entitysite",
                    filter=Q(entitysite__site__in=ProductionSite.objects.all()),
                    distinct=True,
                ),
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

        # Filter based on query params
        if q:
            entities = entities.filter(name__icontains=q)
        if has_requests == "true":
            entities = entities.filter(requests__gt=0)

        # Prepare response data
        entities_data = [
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
                "charge_points_accepted": e.charge_points_accepted,
                "charge_points_pending": e.charge_points_pending,
                "meter_readings_accepted": e.meter_readings_accepted,
                "meter_readings_pending": e.meter_readings_pending,
            }
            for e in entities
        ]

        return Response(entities_data)
