from django.db import models

from core.models import Entity


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
    entity = models.OneToOneField(Entity, on_delete=models.CASCADE, primary_key=True)
    installation_category = models.CharField(choices=INSTALLATION_CATEGORIES, max_length=32, null=True, blank=True)
    cmax = models.FloatField(null=True, blank=True)
    cmax_annualized = models.BooleanField(default=False)
    cmax_annualized_value = models.FloatField(null=True, blank=True)
    pap_contracted = models.FloatField(null=True, blank=True)
    signature_date = models.DateField(null=True, blank=True)
    effective_date = models.DateField(null=True, blank=True)
    general_conditions_file = models.FileField(null=True, blank=True)
    specific_conditions_file = models.FileField(null=True, blank=True)

    class Meta:
        db_table = "biomethane_entity_config_contract"
        verbose_name = "Biométhane - Contrat d'achat"

    def does_contract_exist(self):
        return bool(self.signature_date)


class BiomethaneEntityConfigAmendment(models.Model):
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

    contract = models.ForeignKey(BiomethaneEntityConfigContract, on_delete=models.CASCADE, related_name="amendments")
    signature_date = models.DateField()
    effective_date = models.DateField()
    amendment_object = models.CharField(max_length=64, choices=AMENDMENT_OBJECT_CHOICES)

    # Used only if amendment_object is OTHER
    amendment_details = models.TextField(blank=True, null=True)
    amendment_file = models.FileField()

    class Meta:
        db_table = "biomethane_entity_config_amendment"
        verbose_name = "Biométhane - Avenant"
