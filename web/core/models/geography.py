from django.db import models
from django.utils import timezone


class Pays(models.Model):
    code_pays = models.CharField(max_length=64)
    name = models.CharField(max_length=128)
    name_en = models.CharField(max_length=128)
    date_added = models.DateField(default=timezone.now)
    is_in_europe = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    def natural_key(self):
        return {
            "code_pays": self.code_pays,
            "name": self.name,
            "name_en": self.name_en,
            "is_in_europe": self.is_in_europe,
        }

    class Meta:
        db_table = "pays"
        verbose_name = "Pays"
        verbose_name_plural = "Pays"
        ordering = ["name"]


class Region(models.Model):
    code_region = models.CharField(max_length=3, unique=True)
    name = models.CharField(max_length=128)

    def __str__(self):
        return f"{self.code_region} - {self.name}"

    def natural_key(self):
        return {
            "code_region": self.code_region,
            "name": self.name,
        }

    class Meta:
        db_table = "regions"
        verbose_name = "Région"
        verbose_name_plural = "Régions"
        ordering = ["code_region"]


class Department(models.Model):
    code_dept = models.CharField(max_length=3, unique=True)
    name = models.CharField(max_length=128)
    region = models.ForeignKey(Region, on_delete=models.SET_NULL, null=True, blank=False)

    def __str__(self):
        return f"{self.code_dept} - {self.name}"

    def natural_key(self):
        return {
            "code_dept": self.code_dept,
            "name": self.name,
            "region": self.region.natural_key() if self.region else None,
        }

    class Meta:
        db_table = "departements"
        verbose_name = "Département"
        verbose_name_plural = "Départements"
        ordering = ["code_dept"]
