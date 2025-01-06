from django.contrib.auth import get_user_model
from django.db.models import Q
from django.http import JsonResponse

from core.decorators import check_admin_rights


@check_admin_rights()
def get_users(request):
    q = request.GET.get("q", False)
    company_id = request.GET.get("company_id", False)

    user_model = get_user_model()
    users = user_model.objects.all()

    if q:
        users = users.filter(Q(email__icontains=q) | Q(name__icontains=q))
    if company_id:
        users = users.filter(userrights__entity__id=company_id)

    users_sez = [{"email": u.email, "name": u.name, "id": u.id} for u in users]
    return JsonResponse({"status": "success", "data": users_sez})
