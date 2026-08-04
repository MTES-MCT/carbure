from django.db import models

PRIMARY = "PRIMARY"
INTERMEDIATE = "INTERMEDIATE"
CROP_TYPES_CHOICES = [(PRIMARY, PRIMARY), (INTERMEDIATE, INTERMEDIATE)]
CATEGORY_PRIMARY_CROPS = "Biomasse agricole - Cultures pour alimentaiton humaine ou animale (principales)"
CATEGORY_INTERMEDIATE_CROPS = "Biomasse agricole - Cultures intermédiaires"


class Classification(models.Model):
    group = models.CharField(max_length=128, blank=True)
    category = models.CharField(max_length=128, blank=True)
    subcategory = models.CharField(max_length=128, blank=True)

    @property
    def crop_type(self) -> str | None:
        if self.category == CATEGORY_PRIMARY_CROPS:
            return PRIMARY
        elif self.category == CATEGORY_INTERMEDIATE_CROPS:
            return INTERMEDIATE
        return None

    def __str__(self):
        return f"{self.group} / {self.category} / {self.subcategory}"

    class Meta:
        db_table = "classification"
        verbose_name = "Classification"
        verbose_name_plural = "Classifications"
        unique_together = ("group", "category", "subcategory")
