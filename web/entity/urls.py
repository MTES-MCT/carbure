from django.urls import path
from .api import urlpatterns as api_urlpatterns
from .views import enable_entity

urlpatterns = api_urlpatterns + [
    # TODO integrate this as an action inside a bigger EntityViewset
    path('<int:company_id>/enable/', enable_entity, name="entity-admin-enable"),
]
