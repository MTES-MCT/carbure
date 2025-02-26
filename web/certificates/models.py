import datetime

from dateutil.relativedelta import relativedelta
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from drf_spectacular.utils import extend_schema_field
from rest_framework.serializers import ChoiceField

from core.models import Biocarburant, Entity, EntityCertificate, MatierePremiere
from doublecount.models import DoubleCountingApplication
from transactions.models import Site


class ProductionSiteCertificate(models.Model):
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE)
    production_site = models.ForeignKey(Site, null=True, on_delete=models.CASCADE)
    certificate = models.ForeignKey(EntityCertificate, null=True, blank=True, on_delete=models.CASCADE)

    def natural_key(self):
        return {
            "type": self.certificate.certificate.certificate_type,
            "certificate_id": self.certificate.certificate.certificate_id,
        }

    class Meta:
        db_table = "production_sites_certificates"
        verbose_name = "Certificat de site de production"
        verbose_name_plural = "Certificats de sites de productions"


class DoubleCountingRegistration(models.Model):
    ACTIVE = "ACTIVE"
    EXPIRED = "EXPIRED"
    EXPIRES_SOON = "EXPIRES_SOON"
    INCOMING = "INCOMING"

    AGREEMENT_STATUS = (
        (ACTIVE, ACTIVE),
        (EXPIRED, EXPIRED),
        (EXPIRES_SOON, EXPIRES_SOON),
        (INCOMING, INCOMING),
    )

    certificate_id = models.CharField(max_length=64)
    certificate_holder = models.CharField(max_length=256)
    production_site = models.ForeignKey(Site, on_delete=models.CASCADE, null=True, blank=True)
    registered_address = models.TextField()
    valid_from = models.DateField()
    valid_until = models.DateField()
    application = models.ForeignKey(DoubleCountingApplication, on_delete=models.SET_NULL, null=True, blank=True)

    def natural_key(self):
        return {
            "certificate_id": self.certificate_id,
            "certificate_holder": self.certificate_holder,
            "registered_address": self.registered_address,
            "valid_from": self.valid_from,
            "valid_until": self.valid_until,
            # "status": self.get_status,
        }

    @property
    @extend_schema_field(ChoiceField(choices=AGREEMENT_STATUS))
    def status(self):
        ENDING_MONTH_DELAY = 6
        current_date = datetime.datetime.now().date()
        if current_date > self.valid_until:
            return DoubleCountingRegistration.EXPIRED
        else:
            expires_soon_date = self.valid_until - relativedelta(months=ENDING_MONTH_DELAY)
            production_site_current_agreement = self.production_site.dc_reference if self.production_site else None
            if current_date > expires_soon_date and production_site_current_agreement != self.certificate_id:
                return DoubleCountingRegistration.EXPIRES_SOON
            elif current_date > self.valid_from:
                return DoubleCountingRegistration.ACTIVE
            else:
                return DoubleCountingRegistration.INCOMING

    def __str__(self):
        psite = self.production_site.name if self.production_site else ""
        return "%s - %s" % (self.certificate_id, psite)

    class Meta:
        db_table = "double_counting_registrations"
        ordering = ["certificate_id", "certificate_holder"]
        verbose_name = "Certificat Double Compte"
        verbose_name_plural = "Certificats Double Compte"


@receiver(post_save, sender=DoubleCountingRegistration)
def dc_registration_post_update_production_site(sender, instance, created, update_fields=None, *args, **kwargs):
    if update_fields is None:
        update_fields = {}
    production_site_id = instance.production_site_id
    try:
        production_site = Site.objects.get(pk=production_site_id)
        production_site.dc_reference = instance.certificate_id
        production_site.eligible_dc = True

        production_site.save()
    except Exception:
        # print("Production Site not found")
        pass


class DoubleCountingRegistrationInputOutput(models.Model):
    certificate = models.ForeignKey(DoubleCountingRegistration, blank=False, null=False, on_delete=models.CASCADE)
    biofuel = models.ForeignKey(Biocarburant, null=False, blank=False, on_delete=models.CASCADE)
    feedstock = models.ForeignKey(MatierePremiere, blank=True, null=True, on_delete=models.CASCADE)

    def natural_key(self):
        return {
            "biofuel": self.biofuel.natural_key(),
            "feedstock": self.feedstock.natural_key() if self.feedstock else "",
        }

    class Meta:
        db_table = "double_counting_registrations_scope"
        verbose_name = "Périmètre Certificat Double Compte"
        verbose_name_plural = "Périmètres Certificats Double Compte"
