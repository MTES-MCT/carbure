from datetime import datetime

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.text import slugify

from core import private_storage
from core.models import Entity


def rename_conditions_file(instance, filename):
    base_filename = f"{instance.pk}_CF_{slugify(instance.producer.name)}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    return rename_file(filename, base_filename)


def rename_file(filename, base_filename):
    ext = filename.split(".")[-1]
    return f"biomethane/contracts/{base_filename}.{ext}"


class BiomethaneContract(models.Model):
    TARIFF_RULE_1 = ["2011", "2020"]
    TARIFF_RULE_2 = ["2021", "2023"]

    TARIFF_REFERENCE_CHOICES = tuple((year, year) for year in TARIFF_RULE_1 + TARIFF_RULE_2)

    # Méthanisation en digesteur de produits ou déchets non dangereux,
    # hors matières résultant du traitement des eaux usées urbaines ou industrielles
    INSTALLATION_CATEGORY_1 = "INSTALLATION_CATEGORY_1"

    # Méthanisation en digesteur de produits ou déchets non dangereux,
    # y compris des matières résultant du traitement des eaux usées urbaines ou industrielles
    INSTALLATION_CATEGORY_2 = "INSTALLATION_CATEGORY_2"

    # Installations de stockage de déchets non dangereux à partir de déchets ménagers et assimilés
    INSTALLATION_CATEGORY_3 = "INSTALLATION_CATEGORY_3"
    INSTALLATION_CATEGORIES = (
        (INSTALLATION_CATEGORY_1, INSTALLATION_CATEGORY_1),
        (INSTALLATION_CATEGORY_2, INSTALLATION_CATEGORY_2),
        (INSTALLATION_CATEGORY_3, INSTALLATION_CATEGORY_3),
    )

    tariff_reference = models.CharField(choices=TARIFF_REFERENCE_CHOICES, max_length=28, null=True, blank=True)
    buyer = models.ForeignKey(Entity, on_delete=models.CASCADE, related_name="buyer", null=True, blank=True)
    producer = models.OneToOneField(Entity, on_delete=models.CASCADE, related_name="biomethane_contract")
    installation_category = models.CharField(choices=INSTALLATION_CATEGORIES, max_length=32, null=True, blank=True)
    cmax = models.FloatField(null=True, blank=True)
    cmax_annualized = models.BooleanField(default=False, null=True, blank=True)
    cmax_annualized_value = models.FloatField(null=True, blank=True)
    pap_contracted = models.FloatField(null=True, blank=True)
    signature_date = models.DateField(null=True, blank=True)
    effective_date = models.DateField(null=True, blank=True)
    conditions_file = models.FileField(storage=private_storage, null=True, blank=True, upload_to=rename_conditions_file)

    # List of amendment types that are tracked for the contract when some values are updated
    # (if cmax or pap is updated, we need to save CMAX_PAP_UPDATE to force the user to add an amendment)
    tracked_amendment_types = models.JSONField(default=list, blank=True)

    # Aide complémentaire à l'investissement
    COMPLEMENTARY_AID_ORGANISM_ADEME = "ADEME"
    COMPLEMENTARY_AID_ORGANISM_REGION = "REGION"
    COMPLEMENTARY_AID_ORGANISM_OTHER = "OTHER"

    COMPLEMENTARY_AID_ORGANISMS_CHOICES = [
        (COMPLEMENTARY_AID_ORGANISM_ADEME, "Ademe"),
        (COMPLEMENTARY_AID_ORGANISM_REGION, "Région"),
        (COMPLEMENTARY_AID_ORGANISM_OTHER, "Autre"),
    ]

    # Est-ce que votre installation a bénéficié d'une ou plusieurs aide(s) complémentaire(s) à l'investissement?
    has_complementary_investment_aid = models.BooleanField(default=False, null=True, blank=True)

    # Préciser l'organisme qui a attribué l'aide complémentaire (Ademe, Région, Autre)
    complementary_aid_organisms = models.JSONField(null=True, blank=True, default=list)

    # Précisez le nom du ou des organismes publics ayant octroyé l'aide (si "Autre" est sélectionné)
    complementary_aid_other_organism_name = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = "biomethane_contract"
        verbose_name = "Contrat d'achat"
        verbose_name_plural = "Contrats d'achat"

    @property
    def production_unit(self):
        return getattr(self.producer, "biomethane_production_unit", None)

    def does_contract_exist(self):
        return bool(self.signature_date)

    @property
    def watched_fields(self):
        from biomethane.services.annual_declaration import BiomethaneAnnualDeclarationService

        watched_fields = BiomethaneAnnualDeclarationService.get_watched_fields()
        return watched_fields["contract"]


@receiver(post_save, sender=BiomethaneContract)
def update_red_ii_status(sender, instance, **kwargs):
    if instance.producer.is_red_ii:
        return

    should_be_red_ii = (instance.cmax and instance.cmax > 200) or (
        instance.pap_contracted and instance.pap_contracted > 19.5
    )

    if should_be_red_ii:
        instance.producer.is_red_ii = True
        instance.producer.save(update_fields=["is_red_ii"])


@receiver(post_save, sender=BiomethaneContract)
def clear_contract_fields_on_save(sender, instance, **kwargs):
    """
    Clear specific BiomethaneContract fields based on tariff reference and boolean values.

    This signal is triggered when a BiomethaneContract is saved and clears fields
    that should be reset based on the tariff configuration.
    """
    from biomethane.services.contract import BiomethaneContractService

    update_data = BiomethaneContractService.clear_fields_based_on_tariff(instance)

    if update_data:
        BiomethaneContract.objects.filter(pk=instance.pk).update(**update_data)
