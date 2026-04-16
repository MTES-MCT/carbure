from django.db import models
from django.utils import timezone


class Biocarburant(models.Model):
    name = models.CharField(max_length=64)
    name_en = models.CharField(max_length=64)
    description = models.CharField(max_length=128)
    date_added = models.DateField(default=timezone.now)
    code = models.CharField(max_length=16, unique=True)
    pci_kg = models.FloatField(default=0)
    pci_litre = models.FloatField(default=0)
    masse_volumique = models.FloatField(default=0)
    is_alcool = models.BooleanField(default=False)
    is_graisse = models.BooleanField(default=False)
    is_displayed = models.BooleanField(default=True)

    compatible_essence = models.BooleanField(default=False)
    compatible_diesel = models.BooleanField(default=False)
    dgddi_category = models.CharField(max_length=8, blank=True, null=True, default=None)
    renewable_energy_share = models.FloatField(blank=True, null=True, help_text="saisir 0,50 pour 50%", default=1.0)

    def __str__(self):
        return self.name

    def __eq__(self, other):
        return self.code == other

    def __hash__(self):
        return super().__hash__()

    def natural_key(self):
        return {"code": self.code, "name": self.name}

    class Meta:
        db_table = "biocarburants"
        verbose_name = "Biocarburant"
        verbose_name_plural = "Biocarburants"
        ordering = ["name"]


class MatierePremiereBiofuelManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_biofuel_feedstock=True)


class MatierePremiereBiomethaneManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_methanogenic=True)


class MatierePremiere(models.Model):
    CONV = "CONV"  # CONV
    IXA = "ANN-IX-A"  # Av DC
    IXB = "ANN-IX-B"  # HuHa DC
    TALLOL = "TALLOL"  # Tall
    OTHER = "OTHER"
    EP2AM = "EP2AM"  # EP2 résiduel

    MP_CATEGORIES = (
        (CONV, "Conventionnel"),
        (IXA, "ANNEXE IX-A"),
        (IXB, "ANNEXE IX-B"),
        (TALLOL, "Tallol"),
        (OTHER, "Autre"),
        (EP2AM, "EP2AM"),
    )

    name = models.CharField(max_length=256)
    name_en = models.CharField(max_length=256)
    description = models.CharField(max_length=128)
    date_added = models.DateField(default=timezone.now)
    code = models.CharField(max_length=64, unique=True)
    compatible_alcool = models.BooleanField(default=False)
    compatible_graisse = models.BooleanField(default=False)
    is_double_compte = models.BooleanField(default=False)
    is_huile_vegetale = models.BooleanField(default=False)
    is_displayed = models.BooleanField(default=True)
    category = models.CharField(max_length=32, choices=MP_CATEGORIES, default="")
    dgddi_category = models.CharField(max_length=32, blank=True, null=True, default=None)
    is_methanogenic = models.BooleanField(default=False)
    is_biofuel_feedstock = models.BooleanField(default=False)
    classification = models.ForeignKey("feedstocks.Classification", on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.name

    def natural_key(self):
        return {
            "code": self.code,
            "name": self.name,
            "is_double_compte": self.is_double_compte,
            "category": self.category,
        }

    class Meta:
        db_table = "matieres_premieres"
        verbose_name = "Matiere Premiere"
        verbose_name_plural = "Matieres Premieres"
        ordering = ["name"]

    objects = models.Manager()
    biofuel = MatierePremiereBiofuelManager()
    biomethane = MatierePremiereBiomethaneManager()
