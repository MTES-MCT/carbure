from django.db import models
from django.conf import settings


class Entity(models.Model):
    ENTITY_TYPES = (('Producteur', 'Producteur'), ('Opérateur', 'Opérateur'),
                    ('Administration', 'Administration'), ('Unknown', 'Unknown'))

    name = models.CharField(max_length=64)
    date_added = models.DateTimeField(auto_now_add=True)
    entity_type = models.CharField(max_length=64, choices=ENTITY_TYPES, default='Unknown')
    parent_entity = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'entities'
        verbose_name = 'Entity'
        verbose_name_plural = 'Entities'


class UserRights(models.Model):
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '%s - %s' % (self.user.email, self.entity.name)

    class Meta:
        db_table = 'users_rights'
        verbose_name = 'User Right'
        verbose_name_plural = 'Users Rights'
