from core.decorators import check_rights, otp_or_403
from core.models import CarbureStock, UserRights, UserRightsRequests
from django.contrib.auth import get_user_model
from django.http import JsonResponse


@check_rights("entity_id", role=[UserRights.ADMIN, UserRights.RW])
def enable_mac(request, *args, **kwargs):
    entity = kwargs["context"]["entity"]
    entity.has_mac = True
    entity.save()
    return JsonResponse({"status": "success"})


@check_rights("entity_id", role=[UserRights.ADMIN, UserRights.RW])
def disable_mac(request, *args, **kwargs):
    entity = kwargs["context"]["entity"]
    entity.has_mac = False
    entity.save()
    return JsonResponse({"status": "success"})


@check_rights("entity_id", role=[UserRights.ADMIN, UserRights.RW])
def enable_trading(request, *args, **kwargs):
    entity = kwargs["context"]["entity"]
    entity.has_trading = True
    entity.save()
    return JsonResponse({"status": "success"})


@check_rights("entity_id", role=[UserRights.ADMIN, UserRights.RW])
def disable_trading(request, *args, **kwargs):
    entity = kwargs["context"]["entity"]
    entity.has_trading = False
    entity.save()
    return JsonResponse({"status": "success"})


@check_rights("entity_id", role=[UserRights.ADMIN, UserRights.RW])
def enable_stocks(request, *args, **kwargs):
    entity = kwargs["context"]["entity"]
    entity.has_stocks = True
    entity.save()
    return JsonResponse({"status": "success"})


@check_rights("entity_id", role=[UserRights.ADMIN, UserRights.RW])
def disable_stocks(request, *args, **kwargs):
    entity = kwargs["context"]["entity"]
    stocks = CarbureStock.objects.filter(carbure_client=entity)
    if stocks.count() > 0:
        return JsonResponse({"status": "error", "message": "Cannot disable stocks if you have stocks"}, status=400)
    entity.has_stocks = False
    entity.save()
    return JsonResponse({"status": "success"})


@check_rights("entity_id", role=[UserRights.ADMIN, UserRights.RW])
def enable_direct_deliveries(request, *args, **kwargs):
    entity = kwargs["context"]["entity"]
    entity.has_direct_deliveries = True
    entity.save()
    return JsonResponse({"status": "success"})


@check_rights("entity_id", role=[UserRights.ADMIN, UserRights.RW])
def disable_direct_deliveries(request, *args, **kwargs):
    entity = kwargs["context"]["entity"]
    entity.has_direct_deliveries = False
    entity.save()
    return JsonResponse({"status": "success"})


@otp_or_403
@check_rights("entity_id")
def get_entity_rights(request, *args, **kwargs):
    context = kwargs["context"]
    entity = context["entity"]

    rights = UserRights.objects.filter(entity=entity)
    requests = UserRightsRequests.objects.filter(entity=entity, status__in=["PENDING", "ACCEPTED"])

    data = {}
    data["rights"] = [r.natural_key() for r in rights]
    data["requests"] = [r.natural_key() for r in requests]
    return JsonResponse({"status": "success", "data": data})


@otp_or_403
@check_rights("entity_id", role=[UserRights.ADMIN, UserRights.RW])
def invite_user(request, *args, **kwargs):
    context = kwargs["context"]
    entity = context["entity"]

    email = request.POST.get("email", None)
    role = request.POST.get("role", None)
    expiration_date = request.POST.get("expiration_date", None)

    if email is None:
        return JsonResponse({"status": "error", "message": "Missing user email"}, status=400)

    if role not in [UserRights.RO, UserRights.RW, UserRights.ADMIN, UserRights.AUDITOR]:
        return JsonResponse({"status": "error", "message": "Unknown right"}, status=400)

    if role == UserRights.AUDITOR and not expiration_date:
        return JsonResponse(
            {"status": "error", "message": "Please specify an expiration date for Auditor Role"}, status=400
        )

    user_model = get_user_model()
    try:
        user = user_model.objects.get(email=email)
    except:
        return JsonResponse({"status": "error", "message": "Unknown user"}, status=400)

    try:
        UserRightsRequests.objects.update_or_create(
            user=user, entity=entity, defaults={"role": role, "expiration_date": expiration_date}
        )
        UserRights.objects.update_or_create(
            user=user, entity=entity, defaults={"role": role, "expiration_date": expiration_date}
        )
    except Exception:
        return JsonResponse({"status": "error", "message": "Could not create rights"}, status=400)

    return JsonResponse({"status": "success"})


@otp_or_403
@check_rights("entity_id", UserRights.ADMIN)
def revoke_user(request, *args, **kwargs):
    context = kwargs["context"]
    entity = context["entity"]
    email = request.POST.get("email", None)
    user_model = get_user_model()

    try:
        user = user_model.objects.get(email=email)
    except:
        return JsonResponse({"status": "error", "message": "Could not find user"}, status=400)

    try:
        UserRights.objects.filter(user=user, entity=entity).delete()
    except:
        pass
    try:
        rr = UserRightsRequests.objects.get(user=user, entity=entity)
        rr.status = "REVOKED"
        rr.save()
    except:
        pass

    return JsonResponse({"status": "success"})


@otp_or_403
@check_rights("entity_id", UserRights.ADMIN)
def accept_user(request, *args, **kwargs):
    context = kwargs["context"]
    entity = context["entity"]

    request_id = request.POST.get("request_id", None)

    if request_id is None:
        return JsonResponse({"status": "error", "message": "Missing request_id"}, status=400)

    try:
        right_request = UserRightsRequests.objects.get(id=request_id, entity=entity)
        right_request.status = "ACCEPTED"
        UserRights.objects.update_or_create(
            user=right_request.user,
            entity=entity,
            defaults={"role": right_request.role, "expiration_date": right_request.expiration_date},
        )
        right_request.save()
    except Exception:
        return JsonResponse({"status": "error", "message": "Could not create rights"}, status=400)
    return JsonResponse({"status": "success"})


@otp_or_403
@check_rights("entity_id")
def get_entity_hash(request, *args, **kwargs):
    entity = kwargs["context"]["entity"]
    return JsonResponse({"status": "success", "data": {"hash": entity.hash}})
