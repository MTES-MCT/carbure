from certificates.models import ProductionSiteCertificate
from core.decorators import check_user_rights
from core.models import Entity, EntityCertificate, GenericCertificate, UserRights
from django.http.response import JsonResponse


@check_user_rights(role=[UserRights.ADMIN, UserRights.RW])
def update_certificate(request, *args, **kwargs):
    context = kwargs["context"]
    entity_id = context["entity_id"]
    old_certificate_id = request.POST.get("old_certificate_id", False)
    old_certificate_type = request.POST.get("old_certificate_type", False)
    new_certificate_id = request.POST.get("new_certificate_id", False)
    new_certificate_type = request.POST.get("new_certificate_type", False)

    if not old_certificate_id:
        return JsonResponse({"status": "error", "message": "Please provide an old_certificate_id"}, status=400)
    if not old_certificate_type:
        return JsonResponse({"status": "error", "message": "Please provide an old_certificate_type"}, status=400)
    if not new_certificate_id:
        return JsonResponse({"status": "error", "message": "Please provide an new_certificate_id"}, status=400)
    if not new_certificate_type:
        return JsonResponse({"status": "error", "message": "Please provide an new_certificate_type"}, status=400)

    entity = Entity.objects.get(id=entity_id)
    try:
        new_certificate = GenericCertificate.objects.get(
            certificate_type=new_certificate_type, certificate_id=new_certificate_id
        )
    except:
        return JsonResponse({"status": "error", "message": "Could not find new certificate"}, status=400)
    try:
        old_certificate = EntityCertificate.objects.get(entity=entity, certificate__certificate_id=old_certificate_id)
    except:
        return JsonResponse({"status": "error", "message": "Could not find old certificate"}, status=400)
    obj, created = EntityCertificate.objects.update_or_create(entity=entity, certificate=new_certificate)
    ProductionSiteCertificate.objects.filter(entity=entity, certificate=old_certificate).update(certificate=obj)
    old_certificate.has_been_updated = True
    old_certificate.save()
    return JsonResponse({"status": "success"})
