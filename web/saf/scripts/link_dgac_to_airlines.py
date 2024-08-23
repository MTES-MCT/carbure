import os

import django
from django.db import transaction

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()

from django.contrib.auth import get_user_model

from core.models import Entity, UserRights

User = get_user_model()


@transaction.atomic()
def link_dgac_to_airlines():
    # find all current airlines
    airlines = Entity.objects.filter(entity_type=Entity.AIRLINE)

    # delete old rights
    old_rights = UserRights.objects.filter(entity__in=airlines, user__email__endswith="@aviation-civile.gouv.fr")
    old_rights.delete()

    # find active dgac users
    dgac_rights = UserRights.objects.filter(entity__name="DGAC", user__email__endswith="@aviation-civile.gouv.fr")
    dgac_users = User.objects.filter(is_active=True, pk__in=dgac_rights.values_list("user_id", flat=True))

    # create read only rights for each dgac user-airline couple
    dgac_rights = []
    for airline in airlines:
        for user in dgac_users:
            right = UserRights(user=user, entity=airline, role=UserRights.RO)
            dgac_rights.append(right)

    # save new rights to database
    UserRights.objects.bulk_create(dgac_rights)


if __name__ == "__main__":
    link_dgac_to_airlines()
