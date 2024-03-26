from django.urls import path, include

from .search_company import search_company
from .add_company import apply_for_new_company

urlpatterns = [
    path("search-company", search_company, name="entity-registration-search-company"),
    path("add-company", apply_for_new_company, name="entity-registration-add-company"),
]
