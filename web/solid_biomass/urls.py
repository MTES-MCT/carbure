from django.urls import path

from solid_biomass.views.energy_installation import EnergyInstallationView

urlpatterns = [
    path("energy-installation/", EnergyInstallationView.as_view(), name="energy-installation"),
]
