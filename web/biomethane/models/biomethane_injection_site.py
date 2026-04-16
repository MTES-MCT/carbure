from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

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
    unique_identification_number = models.CharField(
        verbose_name="Numéro d'identifiant unique du site d'injection",
        max_length=32,
        unique=True,
    )
    # Raccordement à un poste d'injection mutualisé
    is_shared_injection_site = models.BooleanField(
        verbose_name="Raccordement à un site d'injection mutualisé",
        default=False,
    )
    # N° de compteur associé au poste d'injection
    meter_number = models.CharField(
        verbose_name="N° de compteur associé au site d'injection",
        max_length=32,
        blank=True,
        null=True,
    )
    # Le poste d'injection est différent du poste de production
    is_different_from_production_site = models.BooleanField(
        verbose_name="Le site d'injection est différent du site de production",
        default=False,
    )
    # Adresse de la société (Numéro et rue)
    company_address = models.CharField(
        verbose_name="Adresse du site d'injection (Numéro et rue)",
        max_length=255,
        blank=True,
        null=True,
    )
    # Ville
    city = models.CharField(verbose_name="Commune", max_length=100, blank=True, null=True)
    # Code postal
    postal_code = models.CharField(verbose_name="Code postal", max_length=10, blank=True, null=True)
    # Type de réseau
    network_type = models.CharField(
        verbose_name="Type de réseau",
        max_length=32,
        choices=NETWORK_TYPE_CHOICES,
        blank=True,
        null=True,
    )
    # Nom du gestionnaire de réseau
    network_manager_name = models.CharField(
        verbose_name="Nom du gestionnaire de réseau",
        max_length=100,
        blank=True,
        null=True,
    )

    class Meta:
        db_table = "biomethane_injection_site"
        verbose_name = "Site d'injection"
        verbose_name_plural = "Sites d'injection"

    @property
    def production_unit(self):
        return getattr(self.producer, "biomethane_production_unit", None)


@receiver(post_save, sender=BiomethaneInjectionSite)
def clear_injection_site_fields_on_save(sender, instance, **kwargs):
    """
    Clear specific BiomethaneInjectionSite fields based on boolean field values.

    This signal is triggered when a BiomethaneInjectionSite is saved and clears
    fields that should be reset based on the configuration changes.
    """
    fields_to_clear = []

    # Clear meter number if injection site is not shared
    if not instance.is_shared_injection_site:
        fields_to_clear.append("meter_number")

    # Clear address fields if injection site is same as production site
    if not instance.is_different_from_production_site:
        fields_to_clear.extend(["company_address", "city", "postal_code"])

    if fields_to_clear:
        update_data = {field: None for field in fields_to_clear}
        BiomethaneInjectionSite.objects.filter(pk=instance.pk).update(**update_data)
