import os
import django
import argparse

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbure.settings")
django.setup()


from core.models import *
emails = [r.user.email for r in UserRights.objects.exclude(role__in=[UserRights.RO, UserRights.AUDITOR, user__is_staff=True, user__is_superuser=True])]

unique_emails = list(set(emails))

for e in unique_emails:
    print(e)

    
    
