from django.views.decorators.csrf import ensure_csrf_cookie
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.decorators import otp_or_403
from core.models import UserRights, UserRightsRequests
from user.serializers import UpdateEmailSerializer, UserErrors, UserSettingsResponseSeriaizer


@extend_schema(
    responses=UserSettingsResponseSeriaizer,
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
@ensure_csrf_cookie
@otp_or_403
def get_settings(request, *args, **kwargs):
    # user-rights
    rights = UserRights.objects.filter(user=request.user).select_related("user", "entity")
    request.session["rights"] = {ur.entity.id: ur.role for ur in rights}
    rights_sez = [r.natural_key() for r in rights]
    # requests
    requests = UserRightsRequests.objects.filter(user=request.user).select_related("user", "entity")
    requests_sez = [r.natural_key() for r in requests]
    return Response({"rights": rights_sez, "email": request.user.email, "requests": requests_sez})


@extend_schema(
    request=UpdateEmailSerializer,
    responses={
        200: {"type": "object", "properties": {"status": {"type": "string"}, "message": {"type": "string"}}},
        400: {"type": "object", "properties": {"message": {"type": "string"}}},
    },
)
@api_view(["PUT"])
@permission_classes([IsAuthenticated])
@ensure_csrf_cookie
@otp_or_403
def update_email(request):
    serializer = UpdateEmailSerializer(data=request.data, context={"request": request})

    if not serializer.is_valid():
        return Response(
            {"message": UserErrors.INVALID_DATA, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
        )

    new_email = serializer.validated_data["new_email"]
    request.user.email = new_email
    request.user.save()

    return Response({"status": "success", "message": UserErrors.EMAIL_UPDATE_SUCCESS}, status=status.HTTP_200_OK)
