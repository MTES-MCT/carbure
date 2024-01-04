from django.urls import path


from .application_template import get_application_template

urlpatterns = [
    path("application-template", get_application_template, name="elec-cpo-get-application-template"),
]
