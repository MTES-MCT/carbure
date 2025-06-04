from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

from auth.views import admin_login_redirect
from carbure.api.redirect_app import redirect_app
from carbure.views.token import TokenObtainPairViewWithAPIKey, TokenRefreshViewWithAPIKey

urlpatterns = [
    re_path("app/(.*)", redirect_app),
    path("admin/login/", admin_login_redirect, name="admin_login_redirect"),
    path("admin/", admin.site.urls),
    # YOUR PATTERNS
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    # Optional UI:
    path(
        "api/schema/swagger-ui/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "api/schema/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
    path("api/", include("carbure.api")),
    path("core/", include("core.urls")),
    path("api/token/", TokenObtainPairViewWithAPIKey.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshViewWithAPIKey.as_view(), name="token_refresh"),
]

if settings.DEBUG:
    urlpatterns += [path("silk/", include("silk.urls", namespace="silk"))]
