from django.db import models

from feedstocks.classification_computed_attributes import (
    INTERMEDIATE,
    PRIMARY,
    get_crop_type,
)


class Classification(models.Model):
    group = models.CharField(max_length=128, blank=True)
    category = models.CharField(max_length=128, blank=True)
    subcategory = models.CharField(max_length=128, blank=True)

    @property
    def crop_type(self) -> str | None:
        return get_crop_type(self)

    @property
    def is_primary_crop(self) -> bool:
        return self.crop_type == PRIMARY

    @property
    def is_intermediate_crop(self) -> bool:
        return self.crop_type == INTERMEDIATE

    def __str__(self):
        return f"{self.group} / {self.category} / {self.subcategory}"

    class Meta:
        db_table = "classification"
        verbose_name = "Classification"
        verbose_name_plural = "Classifications"
        unique_together = ("group", "category", "subcategory")
