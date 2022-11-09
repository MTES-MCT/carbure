from datetime import datetime
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

    carbure_id = models.CharField(max_length=64, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    year = models.IntegerField(blank=False, null=False)
    period = models.IntegerField(blank=False, null=False)

    agreement_reference = models.CharField(max_length=64, null=True)
    agreement_date = models.DateField(null=True)

    volume = models.FloatField(blank=False, null=False)
    biofuel = models.ForeignKey("core.Biocarburant", null=True, on_delete=models.SET_NULL)
    feedstock = models.ForeignKey("core.MatierePremiere", null=True, on_delete=models.SET_NULL)
    country_of_origin = models.ForeignKey("core.Pays", null=True, on_delete=models.SET_NULL, related_name="saf_origin_country")  # fmt: skip

    supplier = models.ForeignKey("core.Entity", null=True, blank=True, on_delete=models.SET_NULL, related_name="saf_owner")  # fmt: skip
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

    client_comment = models.TextField(blank=True, null=True, default=None)
    parent_ticket_source = models.ForeignKey("saf.SafTicketSource", null=True, on_delete=models.SET_NULL, related_name="saf_tickets")  # fmt: skip

    def generate_carbure_id(self):
        self.carbure_id = "T{period}-{country_of_production}-{id}".format(
            period=self.period,
            country_of_production=self.production_country.code_pays,
            id=self.id,
        )


def create_ticket_from_source(ticket_source, client_id, volume, agreement_date, agreement_reference):
    today = datetime.today()
    period = today.year * 100 + today.month

    ticket = SafTicket.objects.create(
        client_id=client_id,
        volume=volume,
        agreement_date=agreement_date,
        agreement_reference=agreement_reference,
        status=SafTicket.PENDING,
        created_at=ticket_source.created_at,
        year=today.year,
        period=period,
        biofuel=ticket_source.biofuel,
        feedstock=ticket_source.feedstock,
        country_of_origin=ticket_source.country_of_origin,
        supplier_id=ticket_source.added_by_id,
        carbure_producer=ticket_source.carbure_producer,
        unknown_producer=ticket_source.unknown_producer,
        carbure_production_site=ticket_source.carbure_production_site,
        unknown_production_site=ticket_source.unknown_production_site,
        production_country=ticket_source.production_country,
        production_site_commissioning_date=ticket_source.production_site_commissioning_date,
        eec=ticket_source.eec,
        el=ticket_source.el,
        ep=ticket_source.ep,
        etd=ticket_source.etd,
        eu=ticket_source.eu,
        esca=ticket_source.esca,
        eccs=ticket_source.eccs,
        eccr=ticket_source.eccr,
        eee=ticket_source.eee,
        ghg_total=ticket_source.ghg_total,
        ghg_reference=ticket_source.ghg_reference,
        ghg_reduction=ticket_source.ghg_reduction,
        parent_ticket_source=ticket_source,
    )

    ticket.generate_carbure_id()
    ticket.save()

    return ticket
