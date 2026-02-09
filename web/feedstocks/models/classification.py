from django.db import models


class Classification(models.Model):
    group = models.CharField(max_length=128, blank=True)
    category = models.CharField(max_length=128, blank=True)
    subcategory = models.CharField(max_length=128, blank=True)

    def __str__(self):
        return f"{self.group} / {self.category} / {self.subcategory}"

    class Meta:
        db_table = "classification"
        verbose_name = "Classification"
        verbose_name_plural = "Classifications"
        unique_together = ("group", "category", "subcategory")
