from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.models import UserRights, UserRightsRequests
from saf.permissions import HasUserRights
from user.serializers import ResponseSuccessSerializer, RevokeAccessSerializer


@extend_schema(
    examples=[
        OpenApiExample(
            "Example of response.",
            value={"status": "success"},
            request_only=False,
            response_only=True,
        ),
    ],
    request=RevokeAccessSerializer,
    responses={200: ResponseSuccessSerializer},
)
@api_view(["POST"])
@permission_classes([IsAuthenticated, HasUserRights(None, [])])
def revoke_myself(request, *args, **kwargs):
    serializer = RevokeAccessSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    entity = serializer.validated_data["entity_id"]
    try:
        right = UserRights.objects.get(user=request.user, entity_id=entity.id)
        right.delete()
    except Exception:
        pass

    try:
        rr = UserRightsRequests.objects.get(user=request.user, entity_id=entity.id)
        rr.delete()
    except Exception:
        pass

    return Response({"status": "success"})
