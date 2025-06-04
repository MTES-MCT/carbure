from rest_framework_api_key.permissions import HasAPIKey
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


class TokenObtainPairViewWithAPIKey(TokenObtainPairView):
    permission_classes = [HasAPIKey]


class TokenRefreshViewWithAPIKey(TokenRefreshView):
    permission_classes = [HasAPIKey]
