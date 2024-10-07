from django.http import JsonResponse

from core.decorators import check_admin_rights
from core.models import EntityCertificate
from core.serializers import EntityCertificateSerializer


@check_admin_rights()
def get_entity_certificates(request):
    company_id = request.GET.get("company_id", False)
    ec = EntityCertificate.objects.order_by("-added_dt", "checked_by_admin").select_related("entity", "certificate")
    if company_id:
        ec = ec.filter(entity_id=company_id)

    serializer = EntityCertificateSerializer(ec, many=True)
    return JsonResponse({"status": "success", "data": serializer.data})
