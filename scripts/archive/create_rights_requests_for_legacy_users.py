import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()


from core.models import *  # noqa: E402

rights = UserRights.objects.all()

for r in rights:
    requests = UserRightsRequests.objects.filter(user=r.user, entity=r.entity).count()
    if requests == 0:
        UserRightsRequests.objects.update_or_create(user=r.user, entity=r.entity, status="ACCEPTED")
