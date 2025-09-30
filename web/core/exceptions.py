from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import APIException


class ResourceConflict(APIException):
    status_code = 400
    default_detail = _("Impossible de supprimer cette ressource car elle est liée à d'autres.")
    default_code = "resource_conflict"
