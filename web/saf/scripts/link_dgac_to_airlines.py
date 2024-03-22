import os
import django
from django.contrib.auth import get_user_model
from django.db import transaction


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()

from core.models import Entity, UserRights, UserRightsRequests

User = get_user_model()


@transaction.atomic()
def link_dgac_to_airlines():
    airlines = Entity.objects.filter(entity_type=Entity.AIRLINE)

    dgac_users = list(
        UserRights.objects.select_related("user")
        .filter(entity__name="DGAC", user__is_staff=False)
        .values_list("user_id", flat=True)
        .distinct()
    )

    # delete old rights
    UserRights.objects.filter(entity__entity_type=Entity.AIRLINE, user__id__in=dgac_users).delete()

    dgac_rights = []
    for airline in airlines:
        for user_id in dgac_users:
            right = UserRights(user_id=user_id, entity=airline, role=UserRights.RO)
            dgac_rights.append(right)

    # create new rights
    UserRights.objects.bulk_create(dgac_rights)


if __name__ == "__main__":
    link_dgac_to_airlines()
