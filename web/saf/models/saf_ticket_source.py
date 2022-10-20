from django.db import models


class SafTicketSource(models.Model):
    class Meta:
        db_table = "saf_ticket_source"
        verbose_name = "Tickets source SAF"
        verbose_name_plural = "Tickets source SAF"
        ordering = ["carbure_id"]

    carbure_id = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    added_by = models.ForeignKey("core.Entity", null=True, blank=True, on_delete=models.SET_NULL, related_name="saf_source_owner")  # fmt: skip

    year = models.IntegerField(blank=False, null=False)
    period = models.IntegerField(blank=False, null=False)

    total_volume = models.FloatField(blank=False, null=False)
    assigned_volume = models.FloatField(blank=False, null=False)

    feedstock = models.ForeignKey("core.MatierePremiere", null=True, on_delete=models.SET_NULL)
    biofuel = models.ForeignKey("core.Biocarburant", null=True, on_delete=models.SET_NULL)
    country_of_origin = models.ForeignKey("core.Pays", null=True, on_delete=models.SET_NULL, related_name="saf_source_origin_country")  # fmt: skip

    carbure_producer = models.ForeignKey("core.Entity", null=True, blank=True, default=None, on_delete=models.SET_NULL, related_name="saf_source_producer")  # fmt: skip
    unknown_producer = models.CharField(max_length=64, blank=True, null=True, default=None)

    carbure_production_site = models.ForeignKey("producers.ProductionSite", null=True, blank=True, default=None, on_delete=models.SET_NULL)  # fmt: skip
    unknown_production_site = models.CharField(max_length=64, blank=True, null=True, default=None)
    production_country = models.ForeignKey("core.Pays", null=True, blank=True, default=None, on_delete=models.SET_NULL, related_name="saf_source_production_country")  # fmt: skip
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

    parent_lot = models.ForeignKey("core.CarbureLot", null=True, blank=True, on_delete=models.CASCADE)


def create_ticket_source_from_lot(lot):
    return SafTicketSource(
        carbure_id=lot.carbure_id,
        created_at=lot.created_at,
        added_by_id=lot.carbure_client_id,
        year=lot.year,
        period=lot.period,
        total_volume=lot.volume,
        assigned_volume=0,
        feedstock_id=lot.feedstock_id,
        biofuel_id=lot.biofuel_id,
        country_of_origin_id=lot.country_of_origin_id,
        carbure_producer_id=lot.carbure_producer_id,
        unknown_producer=lot.unknown_producer,
        carbure_production_site_id=lot.carbure_production_site_id,
        unknown_production_site=lot.unknown_production_site,
        production_country_id=lot.production_country_id,
        production_site_commissioning_date=lot.production_site_commissioning_date,
        eec=lot.eec,
        el=lot.el,
        ep=lot.ep,
        etd=lot.etd,
        eu=lot.eu,
        esca=lot.esca,
        eccs=lot.eccs,
        eccr=lot.eccr,
        eee=lot.eee,
        ghg_total=lot.ghg_total,
        ghg_reference=lot.ghg_reference,
        ghg_reduction=lot.ghg_reduction,
        parent_lot=lot,
    )
