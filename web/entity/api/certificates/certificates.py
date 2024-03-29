from certificates.models import ProductionSiteCertificate
from core.decorators import check_user_rights
from core.models import Entity, EntityCertificate
from core.serializers import EntityCertificateSerializer
from django.http.response import JsonResponse


@check_user_rights()
def get_my_certificates(request, *args, **kwargs):
    context = kwargs["context"]
    entity_id = context["entity_id"]
    production_site_id = request.GET.get("production_site_id", False)
    entity = Entity.objects.get(id=entity_id)
    links = EntityCertificate.objects.filter(entity=entity)
    certificates = [l for l in links]
    if production_site_id:
        links = ProductionSiteCertificate.objects.filter(entity=entity, production_site_id=production_site_id)
        certificates = [l.certificate for l in links]
    serializer = EntityCertificateSerializer(certificates, many=True)
    return JsonResponse({"status": "success", "data": serializer.data})
