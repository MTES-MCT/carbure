from rest_framework.routers import SimpleRouter

from traceability.views.action import ActionViewset

router = SimpleRouter()

router.register("actions", ActionViewset, basename="traceability-action")

urlpatterns = router.urls
