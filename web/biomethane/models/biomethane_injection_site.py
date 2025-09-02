from django.db import models

from core.models import Entity


class BiomethaneInjectionSite(models.Model):
    TRANSPORT = "TRANSPORT"
    DISTRIBUTION = "DISTRIBUTION"

    NETWORK_TYPE_CHOICES = [
        (TRANSPORT, "Transport"),
        (DISTRIBUTION, "Dristribution"),
    ]

    producer = models.OneToOneField(Entity, on_delete=models.CASCADE, related_name="biomethane_injection_site")

    # Numéro d'identifiant unique du poste d'injection
    unique_identification_number = models.CharField(max_length=32, unique=True)
    # Raccordement à un poste d'injection mutualisé
    is_shared_injection_site = models.BooleanField(default=False)
    # N° de compteur associé au poste d'injection
    meter_number = models.CharField(max_length=32, blank=True, null=True)
    # Le poste d'injection est différent du poste de production
    is_different_from_production_site = models.BooleanField(default=False)
    # Adresse de la société (Numéro et rue)
    company_address = models.CharField(max_length=255, blank=True, null=True)
    # Ville
    city = models.CharField(max_length=100, blank=True, null=True)
    # Code postal
    postal_code = models.CharField(max_length=10, blank=True, null=True)
    # Type de réseau
    network_type = models.CharField(
        max_length=32,
        choices=NETWORK_TYPE_CHOICES,
        blank=True,
        null=True,
    )
    # Nom du gestionnaire de réseau
    network_manager_name = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        db_table = "biomethane_injection_site"
        verbose_name = "Biométhane - Site d'injection"
