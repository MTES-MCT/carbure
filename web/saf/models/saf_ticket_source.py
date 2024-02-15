from django.db import models, transaction
from django.db.models import Sum
from django.db.models.functions import Coalesce
from core.utils import bulk_update_or_create


class SafTicketSource(models.Model):
    class Meta:
        db_table = "saf_ticket_source"
        verbose_name = "Tickets source SAF"
        verbose_name_plural = "Tickets source SAF"
        ordering = ["carbure_id"]
        indexes = [
            models.Index(fields=["parent_lot"]),
            models.Index(fields=["parent_ticket"]),
        ]

    carbure_id = models.CharField(max_length=64, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    added_by = models.ForeignKey("core.Entity", null=True, blank=True, on_delete=models.SET_NULL, related_name="saf_source_owner")  # fmt: skip

    year = models.IntegerField(blank=False, null=False)
    delivery_period = models.IntegerField(blank=False, null=False)

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
    parent_ticket = models.ForeignKey("saf.SafTicket", null=True, blank=True, on_delete=models.CASCADE)

    def generate_carbure_id(self):
        production_country = self.production_country.code_pays if self.production_country else None
        self.carbure_id = "TS{period}-{production_country}-{id}".format(
            period=self.delivery_period,
            production_country=production_country,
            id=self.id,
        )


# list of accepted SAF
SAF = ("HVOC", "HOC", "HCC")


@transaction.atomic
def create_ticket_sources_from_lots(lots):
    ticket_source_data = []

    # make sure we only have declared lots of SAF in the queryset
    saf_lots = lots.filter(lot_status__in=["ACCEPTED", "FROZEN"]).filter(biofuel__code__in=SAF)

    for lot in saf_lots.iterator():
        ticket_source_data.append(
            {
                "carbure_id": None,
                "added_by_id": lot.carbure_client_id,
                "year": lot.year,
                "delivery_period": lot.period,
                "total_volume": lot.volume,
                "assigned_volume": 0,
                "feedstock_id": lot.feedstock_id,
                "biofuel_id": lot.biofuel_id,
                "country_of_origin_id": lot.country_of_origin_id,
                "carbure_producer_id": lot.carbure_producer_id,
                "unknown_producer": lot.unknown_producer,
                "carbure_production_site_id": lot.carbure_production_site_id,
                "unknown_production_site": lot.unknown_production_site,
                "production_country_id": lot.production_country_id,
                "production_site_commissioning_date": lot.production_site_commissioning_date,
                "eec": lot.eec,
                "el": lot.el,
                "ep": lot.ep,
                "etd": lot.etd,
                "eu": lot.eu,
                "esca": lot.esca,
                "eccs": lot.eccs,
                "eccr": lot.eccr,
                "eee": lot.eee,
                "ghg_total": lot.ghg_total,
                "ghg_reference": lot.ghg_reference_red_ii,
                "ghg_reduction": lot.ghg_reduction_red_ii,
                "parent_lot_id": lot.id,
            }
        )

    # update ticket sources that were already created for some of the given lots (happens when a lot was declared then undeclared then declared again)
    # and create new ones for lots that were not already declared
    updated, created = bulk_update_or_create(SafTicketSource, "parent_lot_id", ticket_source_data)

    bulk_update_assigned_volume(updated)

    # regenerate carbure_ids for the new ticket sources now that they definitely have an actual id
    ticket_sources = SafTicketSource.objects.filter(parent_lot_id__in=saf_lots.values("id"))
    for ticket_source in ticket_sources:
        ticket_source.generate_carbure_id()
    SafTicketSource.objects.bulk_update(ticket_sources, ["carbure_id"])

    return ticket_sources


def create_source_from_ticket(ticket, entity_id):
    ticket_source = SafTicketSource.objects.create(
        added_by_id=entity_id,
        assigned_volume=0,
        total_volume=ticket.volume,
        year=ticket.year,
        delivery_period=ticket.assignment_period,
        biofuel=ticket.biofuel,
        feedstock=ticket.feedstock,
        country_of_origin=ticket.country_of_origin,
        carbure_producer=ticket.carbure_producer,
        unknown_producer=ticket.unknown_producer,
        carbure_production_site=ticket.carbure_production_site,
        unknown_production_site=ticket.unknown_production_site,
        production_country=ticket.production_country,
        production_site_commissioning_date=ticket.production_site_commissioning_date,
        eec=ticket.eec,
        el=ticket.el,
        ep=ticket.ep,
        etd=ticket.etd,
        eu=ticket.eu,
        esca=ticket.esca,
        eccs=ticket.eccs,
        eccr=ticket.eccr,
        eee=ticket.eee,
        ghg_total=ticket.ghg_total,
        ghg_reference=ticket.ghg_reference,
        ghg_reduction=ticket.ghg_reduction,
        parent_ticket=ticket,
    )

    ticket_source.generate_carbure_id()
    ticket_source.save()

    return ticket_source


def bulk_update_assigned_volume(ticket_sources):
    ticket_sources = SafTicketSource.objects.filter(pk__in=[ts.pk for ts in ticket_sources])
    ticket_sources = ticket_sources.annotate(used_volume=Coalesce(Sum("saf_tickets__volume"), 0.0))

    for ticket_source in ticket_sources:
        ticket_source.assigned_volume = ticket_source.used_volume

    SafTicketSource.objects.bulk_update(ticket_sources, ["assigned_volume"])
