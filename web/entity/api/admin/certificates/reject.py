from django.http import JsonResponse

from carbure.tasks import background_bulk_scoring
from core.decorators import check_admin_rights
from core.models import CarbureLot, CarbureNotification, EntityCertificate


@check_admin_rights()
def reject_entity_certificate(request):
    entity_certificate_id = request.POST.get("entity_certificate_id", False)
    if not entity_certificate_id:
        return JsonResponse({"status": "error", "message": "Missing entity_certificate_id"}, status=400)
    try:
        ec = EntityCertificate.objects.get(id=entity_certificate_id)
        ec.checked_by_admin = False
        ec.rejected_by_admin = True
        ec.save()
        slots = CarbureLot.objects.filter(carbure_supplier=ec.entity, supplier_certificate=ec.certificate.certificate_id)
        plots = CarbureLot.objects.filter(
            carbure_producer=ec.entity, production_site_certificate=ec.certificate.certificate_id
        )

        CarbureNotification.objects.create(
            type=CarbureNotification.CERTIFICATE_REJECTED,
            dest_id=ec.entity.id,
            send_by_email=True,
            meta={"certificate": ec.certificate.certificate_id},
        )

        background_bulk_scoring(list(slots) + list(plots))
        return JsonResponse({"status": "success"})
    except Exception:
        return JsonResponse({"status": "error", "message": "Could not mark certificate as checked"}, status=500)
