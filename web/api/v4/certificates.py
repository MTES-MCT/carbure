import traceback

from carbure.tasks import background_bulk_sanity_checks
from certificates.models import ProductionSiteCertificate
from core.decorators import check_user_rights
from core.models import CarbureLot, Entity, EntityCertificate, GenericCertificate, UserRights
from core.serializers import EntityCertificateSerializer
from django.db.models.query_utils import Q
from django.http.response import JsonResponse


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


@check_user_rights(role=[UserRights.ADMIN, UserRights.RW])
def delete_certificate(request, *args, **kwargs):
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
    try:
        EntityCertificate.objects.get(entity=entity, certificate=certificate).delete()
        lots = CarbureLot.objects.filter(
            Q(supplier_certificate=certificate_id) | Q(production_site_certificate=certificate_id)
        )
        background_bulk_sanity_checks(lots)
    except:
        return JsonResponse({"status": "error", "message": "Could not find certificate"}, status=400)
    return JsonResponse({"status": "success"})


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
