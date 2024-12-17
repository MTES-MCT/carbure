from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver

from core.models import Biocarburant, Entity, GenericCertificate, MatierePremiere, Pays
from transactions.models import Site

usermodel = get_user_model()


class DoubleCountingApplication(models.Model):
    PENDING = "PENDING"
    INPROGRESS = "INPROGRESS"
    REJECTED = "REJECTED"
    ACCEPTED = "ACCEPTED"

    DCA_STATUS_CHOICES = (
        (PENDING, PENDING),
        (INPROGRESS, INPROGRESS),
        (REJECTED, REJECTED),
        (ACCEPTED, ACCEPTED),
    )

    producer = models.ForeignKey(Entity, on_delete=models.CASCADE, null=True, blank=True)
    production_site = models.ForeignKey(Site, on_delete=models.CASCADE, null=True, blank=True)
    producer_user = models.ForeignKey(
        usermodel, blank=True, null=True, on_delete=models.SET_NULL, related_name="producer_user"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    # edited_at = models.DateTimeField(auto_now=True)

    period_start = models.DateField(null=False, blank=False)
    period_end = models.DateField(null=False, blank=False)
    certificate_id = models.CharField(max_length=16)  # FR_123456789_2020
    status = models.CharField(max_length=32, choices=DCA_STATUS_CHOICES, default=PENDING)
    download_link = models.CharField(max_length=512, default=None, null=True)

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
        db_table = "double_counting_applications"
        verbose_name = "Dossier Double Compte"
        verbose_name_plural = "Dossiers Double Compte"


@receiver(pre_save, sender=DoubleCountingApplication)
def set_certificate_id(sender, instance, **kwargs):
    # generer un dc_number si jamais été reconnu comme eligible
    if not instance.production_site.dc_reference:
        dc_number = int(instance.production_site.id) + 1000
        instance.production_site.dc_number = str(dc_number)

    if not instance.certificate_id:
        instance.certificate_id = "FR_" + instance.production_site.dc_number + "_" + instance.period_start.strftime("%Y")
        instance.production_site.dc_reference = instance.certificate_id
        instance.production_site.save()


class DoubleCountingSourcing(models.Model):
    dca = models.ForeignKey(DoubleCountingApplication, on_delete=models.CASCADE, related_name="sourcing")
    year = models.IntegerField(blank=False, null=False)
    feedstock = models.ForeignKey(MatierePremiere, on_delete=models.CASCADE)
    origin_country = models.ForeignKey(Pays, on_delete=models.CASCADE, related_name="origin_country")
    supply_country = models.ForeignKey(Pays, blank=True, null=True, on_delete=models.CASCADE, related_name="supply_country")
    transit_country = models.ForeignKey(
        Pays, blank=True, null=True, on_delete=models.CASCADE, related_name="transit_country"
    )
    metric_tonnes = models.IntegerField(blank=False, null=False)

    def __str__(self):
        return "%s - %s - %st %s - %s - %s" % (
            self.dca,
            self.feedstock,
            self.metric_tonnes,
            self.feedstock.name,
            self.origin_country,
            self.supply_country,
        )

    class Meta:
        db_table = "double_counting_sourcing"
        verbose_name = "Sourcing Double Compte"
        verbose_name_plural = "Sourcing Double Compte"


class DoubleCountingSourcingHistory(models.Model):
    dca = models.ForeignKey(DoubleCountingApplication, on_delete=models.CASCADE, related_name="history_sourcing")
    year = models.IntegerField(blank=False, null=False)
    feedstock = models.ForeignKey(MatierePremiere, on_delete=models.CASCADE)
    origin_country = models.ForeignKey(Pays, on_delete=models.CASCADE, related_name="history_origin_country")
    supply_country = models.ForeignKey(
        Pays, blank=True, null=True, on_delete=models.CASCADE, related_name="history_supply_country"
    )
    transit_country = models.ForeignKey(
        Pays, blank=True, null=True, on_delete=models.CASCADE, related_name="history_transit_country"
    )
    metric_tonnes = models.IntegerField(blank=False, null=False)
    raw_material_supplier = models.CharField(max_length=128, default="")
    supplier_certificate_name = models.CharField(max_length=64, default="")
    supplier_certificate = models.ForeignKey(GenericCertificate, on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return "%s - %s - %st %s - %s - %s - %s" % (
            self.dca,
            self.feedstock,
            self.metric_tonnes,
            self.feedstock.name,
            self.origin_country,
            self.supply_country,
            self.raw_material_supplier,
        )

    class Meta:
        db_table = "double_counting_sourcing_history"
        verbose_name = "Sourcing Double Compte Historique"
        verbose_name_plural = "Sourcing Double Compte Historique"


class DoubleCountingProduction(models.Model):
    dca = models.ForeignKey(DoubleCountingApplication, on_delete=models.CASCADE, related_name="production")
    year = models.IntegerField(blank=False, null=False)
    biofuel = models.ForeignKey(Biocarburant, on_delete=models.CASCADE)
    feedstock = models.ForeignKey(MatierePremiere, on_delete=models.CASCADE)
    max_production_capacity = models.IntegerField(blank=False, null=False, default=0)
    estimated_production = models.IntegerField(blank=False, null=False, default=0)
    requested_quota = models.IntegerField(blank=False, null=False, default=0)
    approved_quota = models.IntegerField(blank=False, null=False, default=-1)

    def __str__(self):
        return "%s - %s / %s - %st estimées (%st max) - %st demandées" % (
            self.year,
            self.feedstock,
            self.biofuel,
            self.estimated_production,
            self.max_production_capacity,
            self.requested_quota,
        )

    class Meta:
        db_table = "double_counting_production"
        verbose_name = "Production Double Compte"
        verbose_name_plural = "Production Double Compte"


class DoubleCountingDocFile(models.Model):
    DECISION = "DECISION"
    SOURCING = "SOURCING"
    FILE_TYPE = ((SOURCING, SOURCING), (DECISION, DECISION))

    url = models.TextField()
    certificate_id = models.CharField(max_length=16, default="")
    file_name = models.CharField(max_length=128, default="")
    file_type = models.CharField(max_length=128, choices=FILE_TYPE, default=SOURCING)
    dca = models.ForeignKey(DoubleCountingApplication, on_delete=models.CASCADE, related_name="documents")
    link_expiry_dt = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = "double_counting_doc_files"
        verbose_name = "Fichier Double Compte"
        verbose_name_plural = "Fichiers Double Compte"
