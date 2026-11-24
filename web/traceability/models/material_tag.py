from django.db import models

from traceability.models.action import Industry


class Tag(models.TextChoices):
    INDUSTRY = "industry", "Filière"


class MaterialTag(models.Model):
    VALUES_PER_TYPE = {
        Tag.INDUSTRY: dict(Industry.choices),
    }

    material = models.ForeignKey("traceability.Material", on_delete=models.CASCADE, related_name="tags")
    type = models.CharField(max_length=32, choices=Tag.choices)
    value = models.CharField(max_length=64, choices=VALUES_PER_TYPE)
