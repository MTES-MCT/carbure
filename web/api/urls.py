from django.urls import path

from . import views

urlpatterns = [
	# public, autocomplete api
	path('biocarburant-autocomplete/', views.biocarburant_autocomplete, name='api-biocarburant-autocomplete'),
	path('matiere-premiere-autocomplete/', views.matiere_premiere_autocomplete, name='api-matiere-premiere-autocomplete'),
	path('country-autocomplete/', views.country_autocomplete, name='api-country-autocomplete'),

    path('lot/validate', views.lot_validate, name='api-lot-validate'),
    path('lot/save', views.lot_save, name='api-lot-save'),
    path('producers/sample-lots', views.producers_sample_lots, name='api-producers-sample-lots'),


    # private, autocomplete
    path('administrators/users-autocomplete/', views.admin_users_autocomplete, name='admin-api-users-autocomplete'),
    path('administrators/entities-autocomplete/', views.admin_entities_autocomplete, name='admin-api-entities-autocomplete'),

]
