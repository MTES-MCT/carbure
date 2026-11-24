from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
from django.db import models

from transactions.models import Site


class EnergyInstallation(Site):
    ELECTRICITY = "ELECTRICITY"
    HEAT = "HEAT"
    COGENERATION = "COGENERATION"
    PRODUCTION_TYPES = [(ELECTRICITY, "Électricité seule"), (HEAT, "Chaleur/Froid seul"), (COGENERATION, "Cogénération")]
    HEAT_TYPES = [
        ("HOT_WATER", "Eau chaude"),
        ("STEAM", "Vapeur"),
        ("HOT_WATER_STEAM", "Eau chaude et vapeur"),
        ("INDUSTRIAL_PROCESS", "Process industriel"),
    ]
    ICPE_REGIMES = [
        ("AUTHORIZATION", "Autorisation"),
        ("REGISTRATION", "Enregistrement"),
        ("DECLARATION_PERIODIC_CONTROLS", "Déclaration (avec contrôles périodiques)"),
    ]

    producer = models.OneToOneField("core.Entity", on_delete=models.CASCADE, related_name="energy_installation")
    production_type = models.CharField(max_length=20, choices=PRODUCTION_TYPES, null=True, blank=True)
    heat_type = models.CharField(max_length=24, choices=HEAT_TYPES, null=True, blank=True)
    useful_temperature = models.FloatField(null=True, blank=True)
    electrical_efficiency = models.FloatField(
        null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    thermal_efficiency = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(100)])
    icpe_number = models.CharField(
        max_length=10,
        null=True,
        blank=True,
        validators=[RegexValidator(r"^\d{10}$", "Le numéro ICPE doit comporter 10 chiffres.")],
    )
    icpe_regime = models.CharField(max_length=32, choices=ICPE_REGIMES, null=True, blank=True)

    class Meta:
        db_table = "sites_energyinstallations"
        verbose_name = "Installation de chaleur et d'électricité"

    def save(self, *args, **kwargs):
        self.site_type = Site.ENERGY_INSTALLATION
        if not self.created_by_id:
            self.created_by_id = self.producer_id
        super().save(*args, **kwargs)
