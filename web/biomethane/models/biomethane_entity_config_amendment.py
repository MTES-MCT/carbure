from datetime import datetime

from django.db import models
from django.utils.text import slugify

from biomethane.models import BiomethaneEntityConfigContract, rename_file
from core import private_storage


def rename_amendment_file(instance, filename):
    try:
        contract = BiomethaneEntityConfigContract.objects.select_related("entity").get(entity_id=instance.contract_id)
        entity_name = slugify(contract.entity.name)
    except BiomethaneEntityConfigContract.DoesNotExist:
        entity_name = "unknown"

    base_filename = f"{instance.contract_id}_amendment_" f"{entity_name}_" f"{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    return rename_file(instance, filename, base_filename)


class BiomethaneEntityConfigAmendment(models.Model):
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

    contract = models.ForeignKey(BiomethaneEntityConfigContract, on_delete=models.CASCADE, related_name="amendments")
    signature_date = models.DateField()
    effective_date = models.DateField()
    amendment_object = models.JSONField(default=list)
    amendment_file = models.FileField(storage=private_storage, upload_to=rename_amendment_file)
    # Used only if amendment_object is OTHER
    amendment_details = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "biomethane_entity_config_amendment"
        verbose_name = "Biométhane - Avenant"
