from django.urls import path


from .meters import get_meters
from .add_meter import add_elec_meter


urlpatterns = [
    path("", get_meters, name="elec-cpo-meters-get-meters"),
    path("add-meter", add_elec_meter, name="elec-cpo-meters-add-meter"),
]
