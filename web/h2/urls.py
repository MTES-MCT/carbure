from rest_framework.routers import SimpleRouter

from h2.views import H2StationViewSet

router = SimpleRouter()
router.register("stations", H2StationViewSet, basename="h2-station")

urlpatterns = [
    *router.urls,
]
