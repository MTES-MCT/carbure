import traceback

from django.http.response import JsonResponse

from certificates.models import ProductionSiteCertificate
from core.decorators import check_user_rights
from core.models import Entity, EntityCertificate
from transactions.models import Site as ProductionSite


@check_user_rights()
def set_production_site_certificates(request, *args, **kwargs):
    context = kwargs["context"]
    entity_id = context["entity_id"]
    certificate_ids = request.POST.getlist("certificate_ids", [])
    production_site_id = request.POST.get("production_site_id", False)
    entity = Entity.objects.get(id=entity_id)
    if not production_site_id:
        return JsonResponse({"status": "error", "message": "Please provide a production_site_id"}, status=400)
    try:
        production_site = ProductionSite.objects.get(entitysite__entity=entity, id=production_site_id)
    except Exception:
        traceback.print_exc()
        return JsonResponse({"status": "error", "message": "Production site not found"}, status=400)

    ProductionSiteCertificate.objects.filter(entity=entity, production_site=production_site).delete()
    for certificate_id in certificate_ids:
        try:
            link = EntityCertificate.objects.get(entity_id=entity_id, certificate__certificate_id=certificate_id)
        except Exception:
            return JsonResponse(
                {"status": "error", "message": "Certificate %s is not associated with your entity" % (certificate_id)},
                status=400,
            )
        ProductionSiteCertificate.objects.update_or_create(entity=entity, production_site=production_site, certificate=link)
    return JsonResponse({"status": "success"})
