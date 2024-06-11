from django.urls import include, path

urlpatterns = [
    path("cpo/", include("elec.api.cpo")),
    path("operator/", include("elec.api.operator")),
    path("admin/", include("elec.api.admin")),
    path("audit/", include("elec.api.audit")),
]
