import datetime

from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from transactions.models import Depot, ProductionSite

from .entity import Entity
from .feedstock import Biocarburant, MatierePremiere
from .geography import Pays
from .lot import CarbureLot

usermodel = get_user_model()


class CarbureStockTransformation(models.Model):
    UNKNOWN = "UNKNOWN"
    ETH_ETBE = "ETH_ETBE"
    TRANSFORMATION_TYPES = (
        (UNKNOWN, UNKNOWN),
        (ETH_ETBE, ETH_ETBE),
    )
    transformation_type = models.CharField(
        max_length=32, choices=TRANSFORMATION_TYPES, null=False, blank=False, default=UNKNOWN
    )
    source_stock = models.ForeignKey(
        "CarbureStock", null=False, blank=False, on_delete=models.CASCADE, related_name="source_stock"
    )
    dest_stock = models.ForeignKey(
        "CarbureStock", null=False, blank=False, on_delete=models.CASCADE, related_name="dest_stock"
    )
    volume_deducted_from_source = models.FloatField(null=False, blank=False, default=0.0)
    volume_destination = models.FloatField(null=False, blank=False, default=0.0)
    metadata = models.JSONField()  # ex: {'volume_denaturant': 1000, 'volume_etbe_eligible': 420000}
    transformed_by = models.ForeignKey(usermodel, null=True, blank=True, on_delete=models.SET_NULL)
    entity = models.ForeignKey(Entity, null=True, blank=True, on_delete=models.SET_NULL)
    transformation_dt = models.DateTimeField(auto_now_add=True)

    def get_weight(self):
        return self.volume_destination * self.source_stock.biofuel.masse_volumique

    def get_lhv_amount(self):
        return self.volume_destination * self.source_stock.biofuel.pci_litre

    class Meta:
        db_table = "carbure_stock_transformations"
        verbose_name = "CarbureStockTransformation"
        verbose_name_plural = "CarbureStockTransformation"
        indexes = [
            models.Index(fields=["entity"]),
            models.Index(fields=["source_stock"]),
            models.Index(fields=["dest_stock"]),
        ]


class CarbureStock(models.Model):
    parent_lot = models.ForeignKey(CarbureLot, null=True, blank=True, on_delete=models.CASCADE)
    parent_transformation = models.ForeignKey(CarbureStockTransformation, null=True, blank=True, on_delete=models.CASCADE)
    carbure_id = models.CharField(max_length=64, blank=False, null=False, default="")
    depot = models.ForeignKey(Depot, null=True, blank=True, on_delete=models.SET_NULL)
    carbure_client = models.ForeignKey(
        Entity, null=True, blank=True, on_delete=models.SET_NULL, related_name="stock_carbure_client"
    )
    remaining_volume = models.FloatField(default=0.0)
    remaining_weight = models.FloatField(default=0.0)
    remaining_lhv_amount = models.FloatField(default=0.0)
    feedstock = models.ForeignKey(MatierePremiere, null=True, on_delete=models.SET_NULL)
    biofuel = models.ForeignKey(Biocarburant, null=True, on_delete=models.SET_NULL)
    country_of_origin = models.ForeignKey(Pays, null=True, on_delete=models.SET_NULL, related_name="stock_country_of_origin")
    carbure_production_site = models.ForeignKey(
        ProductionSite, null=True, blank=True, on_delete=models.SET_NULL, related_name="stock_production_site"
    )
    unknown_production_site = models.CharField(max_length=64, blank=True, null=True, default=None)
    production_country = models.ForeignKey(
        Pays, null=True, blank=True, on_delete=models.SET_NULL, related_name="stock_production_country"
    )
    carbure_supplier = models.ForeignKey(
        Entity, null=True, blank=True, on_delete=models.SET_NULL, related_name="stock_carbure_supplier"
    )
    unknown_supplier = models.CharField(max_length=64, blank=True, null=True, default=None)
    ghg_reduction = models.FloatField(default=0.0)
    ghg_reduction_red_ii = models.FloatField(default=0.0)

    class Meta:
        db_table = "carbure_stock"
        indexes = [
            models.Index(fields=["carbure_client"]),
            models.Index(fields=["carbure_client", "depot"]),
            models.Index(fields=["parent_lot"]),
            models.Index(fields=["parent_transformation"]),
        ]
        verbose_name = "CarbureStock"
        verbose_name_plural = "CarbureStocks"

    def get_weight(self):
        return self.remaining_volume * self.biofuel.masse_volumique

    def get_lhv_amount(self):
        return self.remaining_volume * self.biofuel.pci_litre

    def get_parent_lot(self):
        if self.parent_transformation:
            return self.parent_transformation.source_stock.get_parent_lot()
        else:
            return self.parent_lot

    def get_delivery_date(self):
        if self.parent_lot:
            return self.parent_lot.delivery_date
        elif self.parent_transformation:
            return self.parent_transformation.transformation_dt.date()
        else:
            return datetime.date.today()
        # return self.parent_lot.delivery_date if self.parent_lot else self.parent_transformation.transformation_dt

    def update_remaining_volume(self, diff):
        self.remaining_volume = round(self.remaining_volume + diff, 2)
        self.remaining_lhv_amount = self.get_lhv_amount()
        self.remaining_weight = self.get_weight()

    def generate_carbure_id(self):
        country_of_production = "00"
        if self.production_country:
            country_of_production = self.production_country.code_pays
        delivery_site_id = "00"
        if self.depot:
            delivery_site_id = self.depot.depot_id
        period = "000000"
        parent_lot = self.get_parent_lot()
        if parent_lot:
            period = parent_lot.period
        self.carbure_id = "S{period}-{country_of_production}-{delivery_site_id}-{id}".format(
            period=period, country_of_production=country_of_production, delivery_site_id=delivery_site_id, id=self.id
        )


class CarbureStockEvent(models.Model):
    CREATED = "CREATED"
    UPDATED = "UPDATED"
    FLUSHED = "FLUSHED"
    SPLIT = "SPLIT"
    UNSPLIT = "UNSPLIT"
    TRANSFORMED = "TRANSFORMED"
    UNTRANSFORMED = "UNTRANSFORMED"
    EVENT_TYPES = (
        (CREATED, CREATED),
        (UPDATED, UPDATED),
        (SPLIT, SPLIT),
        (UNSPLIT, UNSPLIT),
        (FLUSHED, FLUSHED),
        (TRANSFORMED, TRANSFORMED),
        (UNTRANSFORMED, UNTRANSFORMED),
    )
    event_type = models.CharField(max_length=32, null=False, blank=False, choices=EVENT_TYPES)
    event_dt = models.DateTimeField(auto_now_add=True, null=False, blank=False)
    stock = models.ForeignKey(CarbureStock, null=False, blank=False, on_delete=models.CASCADE)
    user = models.ForeignKey(usermodel, null=True, blank=True, on_delete=models.SET_NULL)
    metadata = models.JSONField(null=True, blank=True)
    entity = models.ForeignKey(Entity, null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        db_table = "carbure_stock_events"
        indexes = [
            models.Index(fields=["stock"]),
        ]
        verbose_name = "CarbureStockEvent"
        verbose_name_plural = "CarbureStockEvents"


@receiver(post_save, sender=CarbureStock)
def stock_post_save_gen_carbure_id(sender, instance, created, *args, **kwargs):
    old_carbure_id = instance.carbure_id
    instance.generate_carbure_id()

    if instance.carbure_id != old_carbure_id:
        instance.save(update_fields=["carbure_id"])
