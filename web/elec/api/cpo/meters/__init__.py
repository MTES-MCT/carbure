from django.urls import path


from .meters import get_meters


urlpatterns = [
    path("", get_meters, name="elec-cpo-meters-get-meters"),
]
