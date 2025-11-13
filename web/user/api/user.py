from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie

from core.decorators import otp_or_403
from core.models import UserRights, UserRightsRequests


@ensure_csrf_cookie
@otp_or_403
def get_settings(request):
    # user-rights
    rights = UserRights.objects.filter(user=request.user).select_related("user", "entity")
    request.session["rights"] = {ur.entity.id: ur.role for ur in rights}
    rights_sez = [r.natural_key() for r in rights]
    # requests
    requests = UserRightsRequests.objects.filter(user=request.user).select_related("user", "entity")
    requests_sez = [r.natural_key() for r in requests]
    return JsonResponse(
        {"status": "success", "data": {"rights": rights_sez, "email": request.user.email, "requests": requests_sez}}
    )
