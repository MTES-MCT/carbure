from drf_spectacular.utils import OpenApiParameter, OpenApiTypes, extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from core.models import Entity, ExternalAdminRights, UserRights
from core.serializers import GenericCertificateSerializer
from entity.serializers import EntityProductionSiteSerializer
from saf.permissions import HasUserRights
from saf.permissions.user_rights import HasAdminRights, OrPermission
from transactions.models import ProductionSite

from .mixins import ActionMixin


class ProductionSiteViewSet(ViewSet, ActionMixin):
    queryset = ProductionSite.objects.all()
    serializer_class = None
    lookup_field = "id"
    permission_classes = []

    def get_permissions(self):
        # TODO fix permissions if needed
        if self.action in [
            "create",
            "set_biofuels",
            "set_certificates",
            "set_feedstocks",
            "partial_update",
        ]:
            return [HasUserRights([UserRights.ADMIN, UserRights.RW], [Entity.PRODUCER])]
        if self.action in ["destroy"]:
            return [HasUserRights([UserRights.ADMIN], [Entity.PRODUCER])]

        if self.action in ["set_certificates"]:
            return [HasUserRights(None, [Entity.PRODUCER])]

        return [
            OrPermission(
                lambda: HasUserRights(None, [Entity.PRODUCER]),
                lambda: HasAdminRights(allow_external=[ExternalAdminRights.DOUBLE_COUNTING]),
            )
        ]

    def get_queryset(self):
        return ProductionSite.objects.all()

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
                "company_id",
                OpenApiTypes.INT,
                OpenApiParameter.QUERY,
                description="Compay ID, Admin only",
                required=False,
            ),
        ],
        responses=EntityProductionSiteSerializer,
    )
    def list(self, request):
        entity_id = self.request.query_params.get("entity_id")
        company_id = request.query_params.get("company_id", False)

        entity = Entity.objects.get(pk=entity_id)
        data = []
        if entity.entity_type == Entity.ADMIN:
            try:
                psites = self.get_queryset().filter(created_by_id=company_id)
                psitesbyid = {p.id: p for p in psites}
                for _k, v in psitesbyid.items():
                    v.inputs = []
                    v.outputs = []

                for ps in psites:
                    psite_data = ps.natural_key()
                    psite_data["inputs"] = [i.natural_key() for i in ps.productionsiteinput_set.all()]
                    psite_data["outputs"] = [o.natural_key() for o in ps.productionsiteoutput_set.all()]
                    certificates = []
                    for pc in ps.productionsitecertificate_set.all():
                        certificates.append(pc.natural_key())
                    psite_data["certificates"] = certificates
                    data.append(psite_data)
            except Exception:
                return Response(
                    {"message": "Could not find production sites"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            psites = self.get_queryset().filter(created_by=entity)
            psitesbyid = {p.id: p for p in psites}
            for _k, v in psitesbyid.items():
                v.inputs = []
                v.outputs = []

            for ps in psites:
                psite_data = ps.natural_key()
                psite_data["inputs"] = [i.natural_key() for i in ps.productionsiteinput_set.all()]
                psite_data["outputs"] = [o.natural_key() for o in ps.productionsiteoutput_set.all()]
                psite_data["certificates"] = GenericCertificateSerializer(
                    [p.certificate.certificate for p in ps.productionsitecertificate_set.all()],
                    many=True,
                ).data
                data.append(psite_data)

        return Response(data)
