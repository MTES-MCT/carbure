from django.urls import path
from .validate import validate_declaration
from .invalidate import invalidate_declaration

urlpatterns = [
    path("validate", validate_declaration, name="api-v5-declaration-validate"),
    path("invalidate", invalidate_declaration, name="api-v5-declaration-invalidate"),
]
