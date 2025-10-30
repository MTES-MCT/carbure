from datetime import datetime

from django.db import models
from django.utils.text import slugify

from biomethane.models.biomethane_contract import BiomethaneContract, rename_file
from core import private_storage


def rename_amendment_file(instance, filename):
    try:
        contract = BiomethaneContract.objects.select_related("producer").get(id=instance.contract_id)
        entity_name = slugify(contract.producer.name)
    except BiomethaneContract.DoesNotExist:
        entity_name = "unknown"

    base_filename = f"{instance.contract_id}_amendment_" f"{entity_name}_" f"{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    return rename_file(instance, filename, base_filename)


class BiomethaneContractAmendment(models.Model):
    CMAX_PAP_UPDATE = "CMAX_PAP_UPDATE"
    EFFECTIVE_DATE = "EFFECTIVE_DATE"
    CMAX_ANNUALIZATION = "CMAX_ANNUALIZATION"
    INPUT_BONUS_UPDATE = "INPUT_BONUS_UPDATE"
    L_INDEXATION_UPDATE = "L_INDEXATION_UPDATE"
    PRODUCER_BUYER_INFO_CHANGE = "PRODUCER_BUYER_INFO_CHANGE"
    ENERGY_ENVIRONMENTAL_EFFICIENCY_UPDATE = "ENERGY_ENVIRONMENTAL_EFFICIENCY_UPDATE"
    OTHER = "OTHER"

    AMENDMENT_OBJECT_CHOICES = [
        # Modification de la CMAX/PAP
        (CMAX_PAP_UPDATE, CMAX_PAP_UPDATE),
        # "Avenant fixant la date de prise d'effet"
        (EFFECTIVE_DATE, EFFECTIVE_DATE),
        # "Annualisation de la CMAX"
        (CMAX_ANNUALIZATION, CMAX_ANNUALIZATION),
        # "Modification des proportions de prime d'intrant"
        (INPUT_BONUS_UPDATE, INPUT_BONUS_UPDATE),
        # "Modification de l'indexation L"
        (L_INDEXATION_UPDATE, L_INDEXATION_UPDATE),
        # "Changement des informations relatives au producteur/acheteur de biométhane"
        (PRODUCER_BUYER_INFO_CHANGE, PRODUCER_BUYER_INFO_CHANGE),
        # "Modification des conditions d'efficacité énergétique et environnementale"
        (ENERGY_ENVIRONMENTAL_EFFICIENCY_UPDATE, ENERGY_ENVIRONMENTAL_EFFICIENCY_UPDATE),
        # "Autres"
        (OTHER, OTHER),
    ]

    TRACKED_AMENDMENT_TYPES = [
        CMAX_PAP_UPDATE,
        CMAX_ANNUALIZATION,
        PRODUCER_BUYER_INFO_CHANGE,
    ]

    contract = models.ForeignKey(BiomethaneContract, on_delete=models.CASCADE, related_name="amendments")
    signature_date = models.DateField()
    effective_date = models.DateField()
    amendment_object = models.JSONField(default=list)
    amendment_file = models.FileField(storage=private_storage, upload_to=rename_amendment_file)
    # Used only if amendment_object is OTHER
    amendment_details = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "biomethane_contract_amendment"
        verbose_name = "Biométhane - Avenant au contrat"
        verbose_name_plural = "Biométhane - Avenants au contrat"

    @property
    def production_unit(self):
        if hasattr(self, "contract") and self.contract:
            return getattr(self.contract.producer, "biomethane_production_unit", None)
