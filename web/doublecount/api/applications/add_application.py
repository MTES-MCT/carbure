from core.decorators import check_user_rights
from doublecount.api.admin.applications.add import add_application_by_type
from core.models import Entity, UserRights
from django.db import transaction


@check_user_rights(role=[UserRights.ADMIN, UserRights.RW])
@transaction.atomic
def add_application(request):
    return add_application_by_type(request, Entity.PRODUCER)
