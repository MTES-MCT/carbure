from django.urls import path, include

from .search_company import search_company
from .add_company import add_company

urlpatterns = [
    path("search-company", search_company, name="entity-registration-search-company"),
    path("add-company", add_company, name="entity-registration-add-company"),
]
