from datetime import datetime

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.text import slugify

from core import private_storage
from core.models import Entity


def rename_general_conditions_file(instance, filename):
    base_filename = f"{instance.pk}_CG_{slugify(instance.producer.name)}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    return rename_file(instance, filename, base_filename)


def rename_specific_conditions_file(instance, filename):
    base_filename = f"{instance.pk}_CP_{slugify(instance.producer.name)}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    return rename_file(instance, filename, base_filename)


def rename_file(instance, filename, base_filename):
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

    tariff_reference = models.CharField(choices=TARIFF_REFERENCE_CHOICES, max_length=28)
    buyer = models.ForeignKey(Entity, on_delete=models.CASCADE, related_name="buyer")
    producer = models.OneToOneField(Entity, on_delete=models.CASCADE)
    installation_category = models.CharField(choices=INSTALLATION_CATEGORIES, max_length=32, null=True, blank=True)
    cmax = models.FloatField(null=True, blank=True)
    cmax_annualized = models.BooleanField(default=False)
    cmax_annualized_value = models.FloatField(null=True, blank=True)
    pap_contracted = models.FloatField(null=True, blank=True)
    signature_date = models.DateField(null=True, blank=True)
    effective_date = models.DateField(null=True, blank=True)
    general_conditions_file = models.FileField(
        storage=private_storage, null=True, blank=True, upload_to=rename_general_conditions_file
    )
    specific_conditions_file = models.FileField(
        storage=private_storage, null=True, blank=True, upload_to=rename_specific_conditions_file
    )

    class Meta:
        db_table = "biomethane_contract"
        verbose_name = "Biométhane - Contrat d'achat"

    def does_contract_exist(self):
        return bool(self.signature_date)


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
def clear_fields(sender, instance, **kwargs):
    """If tariff_reference changed, reset certain fields"""
    fields_to_clear = []

    if instance.tariff_reference in BiomethaneContract.TARIFF_RULE_1:
        fields_to_clear = ["pap_contracted"]
    elif instance.tariff_reference in BiomethaneContract.TARIFF_RULE_2:
        fields_to_clear = ["cmax_annualized", "cmax_annualized_value", "cmax"]

    update_data = {}
    for field in fields_to_clear:
        new_value = None if field != "cmax_annualized" else False
        update_data[field] = new_value
    BiomethaneContract.objects.filter(pk=instance.pk).update(**update_data)
