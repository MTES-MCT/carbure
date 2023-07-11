from django.db import models
from django.contrib.auth import get_user_model
from django.dispatch import receiver

from core.models import Entity, MatierePremiere, Pays, Biocarburant
from producers.models import ProductionSite
from django.db.models.signals import pre_save

usermodel = get_user_model()


class DoubleCountingAgreement(models.Model):
    PENDING = "PENDING"
    INPROGRESS = "INPROGRESS"
    REJECTED = "REJECTED"
    ACCEPTED = "ACCEPTED"
    LAPSED = "LAPSED"

    DCA_STATUS_CHOICES = (
        (PENDING, PENDING),
        (INPROGRESS, INPROGRESS),
        (REJECTED, REJECTED),
        (ACCEPTED, ACCEPTED),
        (LAPSED, LAPSED),
    )

    producer = models.ForeignKey(Entity, on_delete=models.CASCADE, null=True, blank=True)
    production_site = models.ForeignKey(ProductionSite, on_delete=models.CASCADE, null=True, blank=True)
    producer_user = models.ForeignKey(
        usermodel, blank=True, null=True, on_delete=models.SET_NULL, related_name="producer_user"
    )
    creation_date = models.DateTimeField(auto_now_add=True)
    period_start = models.DateField(null=False, blank=False)
    period_end = models.DateField(null=False, blank=False)
    agreement_id = models.CharField(max_length=16)
    status = models.CharField(max_length=32, choices=DCA_STATUS_CHOICES, default=PENDING)

    dgec_validated = models.BooleanField(default=False)
    dgec_validator = models.ForeignKey(
        usermodel, blank=True, null=True, on_delete=models.SET_NULL, related_name="dgec_validator"
    )
    dgec_validated_dt = models.DateTimeField(null=True, blank=True)

    dgddi_validated = models.BooleanField(default=False)
    dgddi_validator = models.ForeignKey(
        usermodel, blank=True, null=True, on_delete=models.SET_NULL, related_name="dgddi_validator"
    )
    dgddi_validated_dt = models.DateTimeField(null=True, blank=True)

    dgpe_validated = models.BooleanField(default=False)
    dgpe_validator = models.ForeignKey(
        usermodel, blank=True, null=True, on_delete=models.SET_NULL, related_name="dgpe_validator"
    )
    dgpe_validated_dt = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        producer = self.producer.name if self.producer else ""
        return "%s %d - %d" % (producer, self.period_start.year, self.period_end.year)

    def natural_key(self):
        producer = self.producer.name if self.producer else ""
        production_site = self.production_site.name if self.production_site else ""
        return {
            "producer": producer,
            "production_site": production_site,
            "period_end": self.period_end,
            "period_start": self.period_start,
            "status": self.status,
        }

    class Meta:
        db_table = "double_counting_agreements"
        verbose_name = "Dossier Double Compte"
        verbose_name_plural = "Dossiers Double Compte"


@receiver(pre_save, sender=DoubleCountingAgreement)
def set_agreement_id(sender, instance, **kwargs):
    instance.agreement_id = "FR_" + instance.production_site.dc_number + "_" + instance.period_end.strftime("%Y")


class DoubleCountingSourcing(models.Model):
    dca = models.ForeignKey(DoubleCountingAgreement, on_delete=models.CASCADE, related_name="sourcing")
    year = models.IntegerField(blank=False, null=False)
    feedstock = models.ForeignKey(MatierePremiere, on_delete=models.CASCADE)
    origin_country = models.ForeignKey(Pays, on_delete=models.CASCADE, related_name="origin_country")
    supply_country = models.ForeignKey(Pays, blank=True, null=True, on_delete=models.CASCADE, related_name="supply_country")
    transit_country = models.ForeignKey(
        Pays, blank=True, null=True, on_delete=models.CASCADE, related_name="transit_country"
    )
    metric_tonnes = models.IntegerField(blank=False, null=False)

    class Meta:
        db_table = "double_counting_sourcing"
        verbose_name = "Sourcing Double Compte"
        verbose_name_plural = "Sourcing Double Compte"


class DoubleCountingProduction(models.Model):
    dca = models.ForeignKey(DoubleCountingAgreement, on_delete=models.CASCADE, related_name="production")
    year = models.IntegerField(blank=False, null=False)
    biofuel = models.ForeignKey(Biocarburant, on_delete=models.CASCADE)
    feedstock = models.ForeignKey(MatierePremiere, on_delete=models.CASCADE)
    max_production_capacity = models.IntegerField(blank=False, null=False, default=0)
    estimated_production = models.IntegerField(blank=False, null=False, default=0)
    requested_quota = models.IntegerField(blank=False, null=False, default=0)
    approved_quota = models.IntegerField(blank=False, null=False, default=-1)

    class Meta:
        db_table = "double_counting_production"
        verbose_name = "Production Double Compte"
        verbose_name_plural = "Production Double Compte"


class DoubleCountingDocFile(models.Model):
    DECISION = "DECISION"
    SOURCING = "SOURCING"
    FILE_TYPE = ((SOURCING, SOURCING), (DECISION, DECISION))

    url = models.TextField()
    file_name = models.CharField(max_length=128, default="")
    file_type = models.CharField(max_length=128, choices=FILE_TYPE, default=SOURCING)
    dca = models.ForeignKey(DoubleCountingAgreement, on_delete=models.CASCADE, related_name="documents")
    link_expiry_dt = models.DateTimeField()

    class Meta:
        db_table = "double_counting_doc_files"
        verbose_name = "Fichier Double Compte"
        verbose_name_plural = "Fichiers Double Compte"
