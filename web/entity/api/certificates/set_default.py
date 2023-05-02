import traceback

from core.decorators import check_user_rights
from core.models import Entity, EntityCertificate
from django.http.response import JsonResponse


@check_user_rights()
def set_default_certificate(request, *args, **kwargs):
    context = kwargs["context"]
    entity_id = context["entity_id"]
    certificate_id = request.POST.get("certificate_id", False)
    if not certificate_id:
        return JsonResponse({"status": "error", "message": "Please provide a certificate_id"}, status=400)
    try:
        link = EntityCertificate.objects.get(entity_id=entity_id, certificate__certificate_id=certificate_id)
    except:
        traceback.print_exc()
        return JsonResponse(
            {"status": "error", "message": "Could not find certificate_id associated with your entity"}, status=400
        )

    entity = Entity.objects.get(id=entity_id)
    entity.default_certificate = link.certificate.certificate_id
    entity.save()
    return JsonResponse({"status": "success"})
