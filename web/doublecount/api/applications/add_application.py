from django.db import transaction

from core.decorators import check_user_rights
from core.models import Entity, UserRights
from doublecount.api.admin.applications.add import add_application_by_type


@check_user_rights(role=[UserRights.ADMIN, UserRights.RW])
@transaction.atomic
def add_application(request):
    return add_application_by_type(request, Entity.PRODUCER)
