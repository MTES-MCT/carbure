from django.urls import path
from . import views

urlpatterns = [
    # GET
    path('matieres-premieres', views.get_matieres_premieres, name='api-v3-public-matieres-premieres'),
    path('biocarburants', views.get_biocarburants, name='api-v3-public-biocarburants'),
    path('countries', views.get_countries, name='api-v3-public-countries'),
    path('ges', views.get_ges, name='api-v3-public-get-ges'),
    path('entities', views.get_entities, name='api-v3-public-get-entities'),
    path('producers', views.get_producers, name='api-v3-public-get-producers'),
    path('operators', views.get_operators, name='api-v3-public-get-operators'),
    path('traders', views.get_traders, name='api-v3-public-get-traders'),
    path('delivery-sites', views.get_delivery_sites, name='api-v3-public-get-delivery-sites'),
    path('production-sites', views.get_production_sites, name='api-v3-public-get-production-sites'),
    path('iscc-certificates', views.get_iscc_certificates, name='api-v3-public-search-iscc-certificates'),
    path('2bs-certificates', views.get_2bs_certificates, name='api-v3-public-search-2bs-certificates'),
    path('redcert-certificates', views.get_redcert_certificates, name='api-v3-public-search-redcert-certificates'),
    path('sn-certificates', views.get_sn_certificates, name='api-v3-public-search-sn-certificates'),
    path('certificates', views.get_certificates, name='api-v3-public-search-certificates'),

    # POST
    path('create-delivery-site', views.create_delivery_site, name='api-v3-public-create-delivery-site'),

    # CONTROLS
    path('controls/get', views.get_controls, name='api-v3-public-controls-get'),
    path('controls/upload-document', views.controls_upload_file, name='api-v3-public-controls-upload'),
    path('controls/add-message', views.controls_add_message, name='api-v3-public-controls-add-message'),

]
