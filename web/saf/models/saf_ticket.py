from django.db import models


class SafTicket(models.Model):
    class Meta:
        db_table = "saf_ticket"
        verbose_name = "Ticket SAF"
        verbose_name_plural = "Tickets SAF"
        ordering = ["carbure_id"]

    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"

    ticket_statuses = [(PENDING, "En attente"), (ACCEPTED, "Accepté"), (REJECTED, "Refusé")]
    status = models.CharField(max_length=24, choices=ticket_statuses, default=PENDING)

    carbure_id = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    added_by = models.ForeignKey("core.Entity", null=True, blank=True, on_delete=models.SET_NULL, related_name="saf_owner")  # fmt: skip

    year = models.IntegerField(blank=False, null=False)
    period = models.IntegerField(blank=False, null=False)

    agreement_reference = models.CharField(max_length=64, unique=True)
    agreement_date = models.DateField(null=True)

    volume = models.FloatField(blank=False, null=False)
    biofuel = models.ForeignKey("core.Biocarburant", null=True, on_delete=models.SET_NULL)
    feedstock = models.ForeignKey("core.MatierePremiere", null=True, on_delete=models.SET_NULL)
    country_of_origin = models.ForeignKey("core.Pays", null=True, on_delete=models.SET_NULL, related_name="saf_origin_country")  # fmt: skip

    client = models.ForeignKey("core.Entity", null=True, blank=True, default=None, on_delete=models.SET_NULL)  # fmt: skip

    carbure_producer = models.ForeignKey("core.Entity", null=True, blank=True, default=None, on_delete=models.SET_NULL, related_name="saf_producer")  # fmt: skip
    unknown_producer = models.CharField(max_length=64, blank=True, null=True, default=None)

    carbure_production_site = models.ForeignKey("producers.ProductionSite", null=True, blank=True, default=None, on_delete=models.SET_NULL, related_name="saf_production_site")  # fmt: skip
    unknown_production_site = models.CharField(max_length=64, blank=True, null=True, default=None)
    production_country = models.ForeignKey("core.Pays", null=True, blank=True, default=None, on_delete=models.SET_NULL, related_name="saf_production_country")  # fmt: skip
    production_site_commissioning_date = models.DateField(blank=True, null=True)

    eec = models.FloatField(default=0.0)
    el = models.FloatField(default=0.0)
    ep = models.FloatField(default=0.0)
    etd = models.FloatField(default=0.0)
    eu = models.FloatField(default=0.0)
    esca = models.FloatField(default=0.0)
    eccs = models.FloatField(default=0.0)
    eccr = models.FloatField(default=0.0)
    eee = models.FloatField(default=0.0)
    ghg_total = models.FloatField(default=0.0)
    ghg_reference = models.FloatField(default=0.0)
    ghg_reduction = models.FloatField(default=0.0)

    parent_ticket_source = models.ForeignKey("saf.SafTicketSource", null=True, on_delete=models.SET_NULL, related_name="saf_ticket")  # fmt: skip
