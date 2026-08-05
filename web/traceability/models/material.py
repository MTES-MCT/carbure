from django.db import models


class Material(models.Model):
    code = models.CharField(max_length=8)
    name = models.CharField(max_length=64)

    class Meta:
        db_table = "material"
        verbose_name = "Matière"
        verbose_name_plural = "Matières"
        ordering = ["name"]
