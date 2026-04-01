from django.db import models

from core.models.declaration_period import DeclarationPeriod


class DeclarationPeriodManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(app=DeclarationPeriod.BIOMETHANE)


class BiomethaneDeclarationPeriod(DeclarationPeriod):
    class Meta:
        proxy = True

    def save(self, *args, **kwargs):
        self.app = DeclarationPeriod.BIOMETHANE
        super().save(*args, **kwargs)

    objects = DeclarationPeriodManager()
