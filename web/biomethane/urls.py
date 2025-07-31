from rest_framework_nested.routers import SimpleRouter

from .views.entity_config_agreement.entity_config_agreement import BiomethaneEntityConfigAgreementViewSet

router = SimpleRouter()
router.register("", BiomethaneEntityConfigAgreementViewSet, basename="entity-config-agreement")

urlpatterns = router.urls
