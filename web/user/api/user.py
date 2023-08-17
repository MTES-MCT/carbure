from core.decorators import otp_or_403
from core.models import UserRights
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie


@ensure_csrf_cookie
@otp_or_403
def get_settings(request):
    # user-rights
    rights = UserRights.objects.filter(user=request.user).select_related("user", "entity")
    request.session["rights"] = {ur.entity.id: ur.role for ur in rights}
    rights_sez = [r.natural_key() for r in rights]
    # requests
    return JsonResponse({"status": "success", "data": {"rights": rights_sez, "email": request.user.email}})
