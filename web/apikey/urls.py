from django.urls import include, path
from rest_framework_nested.routers import SimpleRouter

from apikey.views import APIKeyViewSet

router = SimpleRouter()
router.register("", APIKeyViewSet, basename="apikey")

urlpatterns = [
    path("", include(router.urls)),
]
