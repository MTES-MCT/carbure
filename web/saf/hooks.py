from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth import get_user_model

from core.models import Entity, UserRights

User = get_user_model()


@receiver(post_save, sender=Entity)
def link_dgac_to_airline(sender, instance, created, update_fields={}, *args, **kwargs):
    if instance.entity_type == Entity.AIRLINE:
        dgac_users = list(
            UserRights.objects.select_related("user")
            .filter(entity__name="DGAC", user__is_staff=False)
            .values_list("user_id", flat=True)
            .distinct()
        )

        for user_id in dgac_users:
            UserRights.objects.update_or_create(user_id=user_id, entity=instance, role=UserRights.RO)
