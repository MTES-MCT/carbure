from django.urls import path, re_path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from . import views

schema_view = get_schema_view(
   openapi.Info(
      title="Carbure External API",
      default_version='v1',
      description="External API for the interconnection between Carbure's and users' systems",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="carbure@beta.gouv.fr"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=[permissions.AllowAny],
)


urlpatterns = [
    # api endpoint visualization
    path('auth/', include('rest_framework.urls')),

    # rest urls
    path('', include(views.router.urls)),

    # swagger urls
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    re_path(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]
