import requests
from django.conf import settings
from drf_spectacular.utils import extend_schema
from rest_framework import serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

REQUEST_TIMEOUT_SECONDS = 5


class MetabaseStatusSerializer(serializers.Serializer):
    available = serializers.BooleanField()


def is_metabase_available() -> bool:
    try:
        response = requests.get(settings.METABASE_SITE_URL, timeout=REQUEST_TIMEOUT_SECONDS)
        response.raise_for_status()
        return True
    except requests.RequestException:
        return False


@extend_schema(responses={200: MetabaseStatusSerializer})
@api_view(["GET"])
@permission_classes([AllowAny])
def get_metabase_status(_request):
    serializer = MetabaseStatusSerializer({"available": is_metabase_available()})
    return Response(serializer.data)
