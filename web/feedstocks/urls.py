from rest_framework.routers import SimpleRouter

from feedstocks.views.feedstock import FeedstockViewSet

router = SimpleRouter()
router.register(
    "feedstocks",
    FeedstockViewSet,
    basename="feedstocks-list",
)
urlpatterns = router.urls
