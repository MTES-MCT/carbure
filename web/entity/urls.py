from django.urls import path

from .views import enable_entity

urlpatterns = [
    # TODO integrate this as an action inside a bigger EntityViewset
    path("<int:company_id>/enable/", enable_entity, name="entity-admin-enable"),
]
