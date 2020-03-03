from django.urls import path

from . import views

urlpatterns = [
	# public, autocomplete api
	path('type-biocarburant-autocomplete/', views.type_biocarburant_autocomplete, name='type-biocarburant-autocomplete'),
	path('matiere-premiere-autocomplete/', views.matiere_premiere_autocomplete, name='matiere-premiere-autocomplete'),
	path('pays-autocomplete/', views.pays_autocomplete, name='pays-autocomplete'),
    path('lot/validate', views.lot_validate, name='api-lot-validate'),
    path('lot/save', views.lot_save, name='api-lot-save'),
    path('producers/sample-lots', views.producers_sample_lots, name='api-producers-sample-lots'),
]
