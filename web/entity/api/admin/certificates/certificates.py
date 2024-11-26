from django.http import JsonResponse

from core.decorators import check_admin_rights
from core.models import Entity, EntityCertificate, ExternalAdminRights
from core.serializers import EntityCertificateSerializer


@check_admin_rights(allow_external=[ExternalAdminRights.DOUBLE_COUNTING])
def get_entity_certificates(request, entity):
    company_id = request.GET.get("company_id", False)

    ec = EntityCertificate.objects.order_by("-added_dt", "checked_by_admin").select_related("entity", "certificate")

    if company_id:
        ec = ec.filter(entity_id=company_id)
    if entity.has_external_admin_right(ExternalAdminRights.DOUBLE_COUNTING):
        ec = ec.filter(entity__entity_type=Entity.PRODUCER)

    serializer = EntityCertificateSerializer(ec, many=True)
    return JsonResponse({"status": "success", "data": serializer.data})
