from django.urls import path
from .declarations import get_declarations
from .invalidate import invalidate_declaration
from .validate import validate_declaration


urlpatterns = [
    path("", get_declarations, name="transactions-declarations"),
    path("invalidate", invalidate_declaration, name="transactions-declarations-invalidate"),
    path("validate", validate_declaration, name="transactions-declarations-validate"),
]
