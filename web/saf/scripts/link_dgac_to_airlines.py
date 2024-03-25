import os
import django
from django.contrib.auth import get_user_model
from django.db import transaction


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()

from core.models import Entity, UserRights

User = get_user_model()


@transaction.atomic()
def link_dgac_to_airlines():
    airlines = Entity.objects.filter(entity_type=Entity.AIRLINE)

    dgac_users = User.objects.filter(email__endswith="@aviation-civile.gouv.fr")

    # delete old rights
    UserRights.objects.filter(entity__entity_type=Entity.AIRLINE, user__in=dgac_users).delete()

    dgac_rights = []
    for airline in airlines:
        for user in dgac_users:
            right = UserRights(user=user, entity=airline, role=UserRights.RO)
            dgac_rights.append(right)

    # create new rights
    UserRights.objects.bulk_create(dgac_rights)


if __name__ == "__main__":
    link_dgac_to_airlines()
