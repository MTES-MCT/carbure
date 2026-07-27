from django.views.decorators.csrf import ensure_csrf_cookie
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from core.models import UserRights, UserRightsRequests
from core.permissions import IsVerified
from user.serializers import (
    UserSettingsResponseSerializer,
)


@extend_schema(
    responses=UserSettingsResponseSerializer,
)
@api_view(["GET"])
@permission_classes([IsVerified])
@ensure_csrf_cookie
def get_settings(request, *args, **kwargs):
    # user-rights
    rights = UserRights.objects.filter(user=request.user).select_related("user", "entity")
    request.session["rights"] = {ur.entity.id: ur.role for ur in rights}
    # requests
    requests = UserRightsRequests.objects.filter(user=request.user).select_related("user", "entity")
    serializer = UserSettingsResponseSerializer(
        {
            "email": request.user.email,
            "name": request.user.name,
            "rights": rights,
            "requests": requests,
        }
    ).data

    return Response(serializer)
