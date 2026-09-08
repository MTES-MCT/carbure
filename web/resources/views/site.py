from django.db.models import Q
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from core.permissions import IsVerified
from traceability.serializers.site import ActionSiteSerializer
from transactions.models import Site


@extend_schema(
    parameters=[
        OpenApiParameter(
            name="query",
            description="Search within the fields `name`, `site_siret` and `city`",
            required=False,
            type=str,
        ),
        OpenApiParameter(
            name="site_type",
            description="Only keep specific site types",
            required=False,
            type=str,
            many=True,
        ),
    ],
    responses=ActionSiteSerializer(many=True),
)
@api_view(["GET"])
@permission_classes([IsVerified])
def get_sites(request, *args, **kwargs):
    query = request.query_params.get("query")
    site_types = request.query_params.getlist("site_type")
    sites = Site.objects.filter(private=False).order_by("name")

    if query:
        sites = sites.filter(Q(name__icontains=query) | Q(site_siret__icontains=query) | Q(city__icontains=query))
    if site_types:
        sites = sites.filter(site_type__in=site_types)

    return Response(ActionSiteSerializer(sites, many=True).data)
