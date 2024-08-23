from django.db.models.query_utils import Q
from django.http.response import JsonResponse

from carbure.tasks import background_bulk_sanity_checks
from core.decorators import check_user_rights
from core.models import CarbureLot, Entity, EntityCertificate, GenericCertificate, UserRights


@check_user_rights(role=[UserRights.ADMIN, UserRights.RW])
def add_certificate(request, *args, **kwargs):
    context = kwargs["context"]
    entity_id = context["entity_id"]
    certificate_id = request.POST.get("certificate_id", False)
    certificate_type = request.POST.get("certificate_type", False)
    if not certificate_id:
        return JsonResponse({"status": "error", "message": "Missing certificate_id"}, status=400)
    if not certificate_type:
        return JsonResponse({"status": "error", "message": "Missing certificate_type"}, status=400)
    entity = Entity.objects.get(id=entity_id)
    certificate = GenericCertificate.objects.get(certificate_type=certificate_type, certificate_id=certificate_id)
    EntityCertificate.objects.update_or_create(entity=entity, certificate=certificate)
    lots = CarbureLot.objects.filter(
        Q(supplier_certificate=certificate_id) | Q(production_site_certificate=certificate_id)
    )
    background_bulk_sanity_checks(lots)
    return JsonResponse({"status": "success"})
