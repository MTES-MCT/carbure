from datetime import datetime

from django.db import models
from django.utils.text import slugify

from core import private_storage
from core.models import Entity


def rename_general_conditions_file(instance, filename):
    base_filename = f"{instance.pk}_CG_{slugify(instance.entity.name)}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    return rename_file(instance, filename, base_filename)


def rename_specific_conditions_file(instance, filename):
    base_filename = f"{instance.pk}_CP_{slugify(instance.entity.name)}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    return rename_file(instance, filename, base_filename)


def rename_file(instance, filename, base_filename):
    ext = filename.split(".")[-1]
    return f"biomethane/contracts/{base_filename}.{ext}"


class BiomethaneEntityConfigContract(models.Model):
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
    entity = models.OneToOneField(Entity, on_delete=models.CASCADE)
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
        db_table = "biomethane_entity_config_contract"
        verbose_name = "Biométhane - Contrat d'achat"

    def does_contract_exist(self):
        return bool(self.signature_date)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self._update_red_ii_status()

    def _update_red_ii_status(self):
        if self.entity.is_red_ii:
            return

        if (self.cmax and self.cmax > 200) or (self.pap_contracted and self.pap_contracted > 19.5):
            self.entity.is_red_ii = True
            self.entity.save()
