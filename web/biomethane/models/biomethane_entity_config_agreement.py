from django.db import models

from core.models import Entity

TARIFF_REFERENCE_CHOICES = [
    (2011, 2011),
    (2021, 2021),
    (2022, 2022),
    (2023, 2023),
]

AMENDMENT_OBJECT_CHOICES = [
    # Modification de la CMAX/PAP
    ("CMAX_PAP_UPDATE", "CMAX_PAP_UPDATE"),
    # "Avenant fixant la date de prise d'effet"
    ("EFFECTIVE_DATE", "EFFECTIVE_DATE"),
    # "Annualisation de la CMAX"
    ("CMAX_ANNUALIZATION", "CMAX_ANNUALIZATION"),
    # "Modification des proportions de prime d'intrant"
    ("INPUT_BONUS_UPDATE", "INPUT_BONUS_UPDATE"),
    # "Modification de l'indexation L"
    ("L_INDEXATION_UPDATE", "L_INDEXATION_UPDATE"),
    # "Changement des informations relatives au producteur/acheteur de biométhane"
    ("PRODUCER_BUYER_INFO_CHANGE", "PRODUCER_BUYER_INFO_CHANGE"),
    # "Modification des conditions d'efficacité énergétique et environnementale"
    ("ENERGY_ENVIRONMENTAL_EFFICIENCY_UPDATE", "ENERGY_ENVIRONMENTAL_EFFICIENCY_UPDATE"),
    # "Autres"
    ("OTHER", "OTHER"),
]


class BiomethaneEntityConfigAgreement(models.Model):
    tariff_reference = models.CharField(choices=TARIFF_REFERENCE_CHOICES, max_length=28)
    buyer = models.ForeignKey(Entity, on_delete=models.CASCADE, related_name="buyer")
    entity = models.OneToOneField(Entity, on_delete=models.CASCADE, primary_key=True)
    installation_category = models.CharField(max_length=128)
    cmax = models.FloatField()
    cmax_annualized = models.BooleanField()
    cmax_annualized_value = models.FloatField()
    pap_contracted = models.FloatField()
    signature_date = models.DateField()
    effective_date = models.DateField()
    general_conditions_file = models.FileField()
    specific_conditions_file = models.FileField()

    class Meta:
        db_table = "biomethane_entity_config_agreement"
        verbose_name = "Biométhane - Contrat d'achat"


class BiomethaneEntityConfigAmendment(models.Model):
    contract = models.ForeignKey(BiomethaneEntityConfigAgreement, on_delete=models.CASCADE, related_name="amendments")
    signature_date = models.DateField()
    effective_date = models.DateField()
    amendment_object = models.CharField(max_length=64, choices=AMENDMENT_OBJECT_CHOICES)

    # Used only if amendment_object is OTHER
    amendment_details = models.TextField(blank=True, null=True)
    amendment_file = models.FileField()

    class Meta:
        db_table = "biomethane_entity_config_amendment"
        verbose_name = "Biométhane - Avenant"
