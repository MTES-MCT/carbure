from django.db import models

class LockedYear(models.Model):
    year = models.IntegerField(blank=False, null=False) # index
    locked = models.BooleanField(default=True)

    class Meta:
            db_table = 'locked_years'
            indexes = [models.Index(fields=['year']),]
            verbose_name = 'Locked Year'
            verbose_name_plural = 'Locked Years'
