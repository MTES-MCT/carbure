from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth import get_user_model

from core.models import Entity, UserRights

User = get_user_model()


@receiver(post_save, sender=Entity)
def link_dgac_to_airline(sender, instance, created, update_fields={}, *args, **kwargs):
    if instance.entity_type == Entity.AIRLINE:
        dgac_users = User.objects.filter(email__endswith="@aviation-civile.gouv.fr")

        for user in dgac_users:
            UserRights.objects.update_or_create(user=user, entity=instance, role=UserRights.RO)
