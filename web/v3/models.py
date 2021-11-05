from django.db import models
from django.contrib.auth import get_user_model

from core.models import Entity, Depot, ProductionSite, MatierePremiere, Pays, Biocarburant

usermodel = get_user_model()

class CarbureLot(models.Model):
    period = models.IntegerField(blank=False, null=False) # index
    year = models.IntegerField(blank=False, null=False) # index
    carbure_id = models.CharField(max_length=64, blank=True, default='')

    # production data
    carbure_producer = models.ForeignKey(Entity, null=True, blank=True, default=None, on_delete=models.SET_NULL)
    unknown_producer = models.CharField(max_length=64, blank=True, null=True, default=None)
    carbure_production_site = models.ForeignKey(ProductionSite, null=True, blank=True, default=None, on_delete=models.SET_NULL)
    unknown_production_site = models.CharField(max_length=64, blank=True, null=True, default=None)
    production_country = models.ForeignKey(Pays, null=True, blank=True, default=None, on_delete=models.SET_NULL)
    production_site_commissioning_date = models.DateField(blank=True, null=True)
    production_site_certificate = models.CharField(max_length=64, blank=True, null=True, default=None)
    production_site_certificate_type = models.CharField(max_length=64, blank=True, null=True, default=None)
    production_site_double_counting_certificate = models.CharField(max_length=64, blank=True, null=True, default=None)
    # supplier data
    carbure_supplier = models.ForeignKey(Entity, null=True, blank=True, on_delete=models.SET_NULL)
    unknown_supplier = models.CharField(max_length=64, blank=True, null=True, default=None)
    supplier_certificate = models.CharField(max_length=64, blank=True, null=True, default=None)
    supplier_certificate_type = models.CharField(max_length=64, blank=True, null=True, default=None)

    # delivery
    DAU = "DAU"
    DAE = "DAE"
    DSA = "DSA"
    DSAC = "DSAC"
    DSP = "DSP"
    OTHER = "OTHER"
    TRANSPORT_DOCUMENT_TYPES = ((DAU, DAU), (DAE, DAE), (DSA, DSA), (DSAC, DSAC), (DSP, DSP), (OTHER, OTHER),)
    transport_document_type = models.CharField(max_length=12, blank=False, null=False, choices=TRANSPORT_DOCUMENT_TYPES, default=DAE)
    transport_document_reference = models.CharField(max_length=64, blank=False, null=False, default=None)
    carbure_client = models.ForeignKey(Entity, null=True, blank=True, default=None, on_delete=models.SET_NULL)
    unknown_client = models.CharField(max_length=64, blank=True, null=True, default=None)
    dispatch_date = models.DateField(blank=True, null=True)
    carbure_dispatch_site = models.ForeignKey(Depot, null=True, blank=True, default=None, on_delete=models.SET_NULL)
    unknown_dispatch_site = models.CharField(max_length=64, blank=True, null=True, default=None)
    dispatch_site_country = models.ForeignKey(Pays, null=True, blank=True, on_delete=models.SET_NULL)
    delivery_date = models.DateField(blank=True, null=True)
    carbure_delivery_site = models.ForeignKey(Depot, null=True, blank=True, default=None, on_delete=models.SET_NULL)
    unknown_delivery_site = models.CharField(max_length=64, blank=True, null=True, default=None)
    delivery_site_country = models.ForeignKey(Pays, null=True, blank=True, on_delete=models.SET_NULL)

    DRAFT = "DRAFT"
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    FROZEN = "FROZEN"
    DELETED = "DELETED"
    LOT_STATUSES = ((DRAFT, DRAFT), (PENDING, PENDING), (ACCEPTED, ACCEPTED), (REJECTED, REJECTED), (FROZEN, FROZEN), (DELETED, DELETED),)
    lot_status = models.CharField(max_length=24, choices=LOT_STATUSES, default=DRAFT)
    
    NO_PROBLEMO = "NO_PROBLEMO"
    IN_CORRECTION = "IN_CORRECTION"
    FIXED = "FIXED"
    CORRECTION_STATUSES = ((NO_PROBLEMO, NO_PROBLEMO), (IN_CORRECTION, IN_CORRECTION), (FIXED, FIXED))
    correction_status = models.CharField(max_length=64, choices=CORRECTION_STATUSES, default=NO_PROBLEMO)

    UNKNOWN = "UNKNOWN"
    RFC = "RFC" # release for consumption / mise a consommation
    STOCK = "STOCK"
    BLENDING = "BLENDING" # incorporation
    EXPORT = "EXPORT"
    TRADING = "TRADING"
    PROCESSING = "PROCESSING"
    DIRECT = "DIRECT" # livraison directe
    DELIVERY_TYPES = ((UNKNOWN, UNKNOWN), (RFC, RFC), (STOCK, STOCK), (BLENDING, BLENDING), (EXPORT, EXPORT), (TRADING, TRADING), (PROCESSING, PROCESSING), (DIRECT, DIRECT),)
    delivery_type = models.CharField(max_length=64, choices=DELIVERY_TYPES, blank=False, null=False, default=UNKNOWN)
    declared_by_supplier = models.BooleanField(default=False)
    declared_by_client = models.BooleanField(default=False)


    # lot details
    volume = models.FloatField(default=0.0)
    weight = models.FloatField(default=0.0)
    lhv_amount = models.FloatField(default=0.0)
    feedstock = models.ForeignKey(MatierePremiere, null=True, on_delete=models.SET_NULL)
    biofuel = models.ForeignKey(Biocarburant, null=True, on_delete=models.SET_NULL)
    country_of_origin = models.ForeignKey(Pays, null=True, on_delete=models.SET_NULL)

    # GHG values
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
    ghg_reference_red_ii = models.FloatField(default=0.0)
    ghg_reduction_red_ii = models.FloatField(default=0.0)

    added_by = models.ForeignKey(Entity, null=True, blank=True, on_delete=models.SET_NULL)
    parent_lot = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE)
    parent_stock = models.ForeignKey('CarbureStock', null=True, blank=True, on_delete=models.CASCADE)

    free_field = models.TextField(blank=True, null=True, default=None)

    # admin / auditor checks & filters
    highlighted_by_admin = models.BooleanField(default=False)
    highlighted_by_auditor = models.BooleanField(default=False)

    class Meta:
        db_table = 'carbure_lots'
        indexes = [models.Index(fields=['year']),
                   models.Index(fields=['year', 'carbure_client']),
                   models.Index(fields=['year', 'carbure_supplier']),
                   models.Index(fields=['year', 'period']),
                   models.Index(fields=['year', 'period', 'carbure_client']),
                   models.Index(fields=['year', 'period', 'carbure_supplier']),
                  ]
        verbose_name = 'Lot'
        verbose_name_plural = 'Lots'


class CarbureStockTransformation(models.Model):
    UNKNOWN = "UNKNOWN"
    ETH_ETBE = "ETH_ETBE"
    TRANSFORMATION_TYPES = ((UNKNOWN, UNKNOWN), (ETH_ETBE, ETH_ETBE), )
    transformation_type = models.CharField(max_length=32, choices=TRANSFORMATION_TYPES, null=False, blank=False, default=UNKNOWN)
    source_stock = models.ForeignKey('CarbureStock', null=False, blank=False, on_delete=models.CASCADE)
    dest_stock = models.ForeignKey('CarbureStock', null=False, blank=False, on_delete=models.CASCADE)
    volume_deducted_from_source = models.FloatField(null=False, blank=False, default=0.0)
    volume_destination = models.FloatField(null=False, blank=False, default=0.0)
    metadata = models.JsonField() # ex: {‘volume_denaturant’: 1000, ‘volume_etbe_eligible’: 420000}
    transformed_by = models.ForeignKey(usermodel, null=True, blank=True, on_delete=models.SET_NULL)
    entity = models.ForeignKey(Entity, null=True, blank=True, on_delete=models.SET_NULL)
    transformation_dt = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'carbure_stock_transformations'
        indexes = [models.Index(fields=['entity']),]
        verbose_name = 'CarbureStockTransformation'
        verbose_name_plural = 'CarbureStockTransformation'


class CarbureStock(models.Model):
    parent_lot = models.ForeignKey(CarbureLot, null=True, blank=True, on_delete=models.CASCADE)
    parent_transformation = models.ForeignKey(CarbureStockTransformation, null=True, blank=True, on_delete=models.CASCADE)
    carbure_id = models.CharField(max_length=64, blank=False, null=False, default='')
    depot = models.ForeignKey(Depot, null=True, blank=True, on_delete=models.SET_NULL)
    entity = models.ForeignKey(Entity, null=True, blank=True, on_delete=models.SET_NULL)
    remaining_volume = models.FloatField(default=0.0)
    remaining_weight = models.FloatField(default=0.0)
    remaining_lhv_amount = models.FloatField(default=0.0)
    feedstock = models.ForeignKey(MatierePremiere, null=True, on_delete=models.SET_NULL)
    biofuel = models.ForeignKey(Biocarburant, null=True, on_delete=models.SET_NULL)
    country_of_origin = models.ForeignKey(Pays, null=True, on_delete=models.SET_NULL)
    carbure_production_site = models.ForeignKey(ProductionSite, null=True, blank=True, on_delete=models.SET_NULL)
    unknown_production_site = models.CharField(max_length=64, blank=True, null=True, default='')
    production_country = models.ForeignKey(Pays, null=True, blank=True, on_delete=models.SET_NULL)
    carbure_supplier = models.ForeignKey(Entity, null=True, blank=True, on_delete=models.SET_NULL)
    unknown_supplier = models.CharField(max_length=64, blank=True, null=True, default='')
    ghg_reduction = models.FloatField(default=0.0)
    ghg_reduction_red_ii = models.FloatField(default=0.0)

    class Meta:
        db_table = 'carbure_stock'
        indexes = [
            models.Index(fields=['entity']),
            models.Index(fields=['entity', 'depot']),
        ]
        verbose_name = 'CarbureStock'
        verbose_name_plural = 'CarbureStocks'


class CarbureLotEvent(models.Model):
    CREATED = "CREATED"
    UPDATED = "UPDATED"
    VALIDATED = "VALIDATED"
    FIX_REQUESTED = "FIX_REQUESTED"
    MARKED_AS_FIXED = "MARKED_AS_FIXED"
    FIX_ACCEPTED = "FIX_ACCEPTED"
    ACCEPTED = "ACCEPTED"
    DECLARED = "DECLARED"
    DELETED = "DELETED"
    RESTORED = "RESTORED"
    EVENT_TYPES = ((CREATED, CREATED), (UPDATED, UPDATED), (VALIDATED, VALIDATED), (FIX_REQUESTED, FIX_REQUESTED), (MARKED_AS_FIXED, MARKED_AS_FIXED), (FIX_ACCEPTED, FIX_ACCEPTED), (ACCEPTED, ACCEPTED), (DECLARED, DECLARED), (DELETED, DELETED), (RESTORED, RESTORED))
    event_type = models.CharField(max_length=32, null=False, blank=False, choices=EVENT_TYPES)
    event_dt = models.DateTimeField(default_add_now=True, null=False, blank=False)
    lot = models.ForeignKey(CarbureLot, null=False, blank=False, on_delete=models.CASCADE)
    user = models.ForeignKey(usermodel, null=False, blank=False, on_delete=models.SET_NULL)
    metadata = models.JsonField()

    class Meta:
        db_table = 'carbure_lots_events'
        indexes = [
            models.Index(fields=['lot']),
        ]
        verbose_name = 'CarbureLotEvent'
        verbose_name_plural = 'CarbureLotEvents'


class CarbureLotComment(models.Model):
    REGULAR = "REGULAR"
    AUDITOR = "AUDITOR"
    ADMIN = "ADMIN"
    COMMENT_TYPES = ((REGULAR, REGULAR), (AUDITOR, AUDITOR), (ADMIN))

    entity = models.ForeignKey(Entity, null=True, blank=True, on_delete=models.SET_NULL)
    user = models.ForeignKey(usermodel, null=True, blank=True, on_delete=models.SET_NULL)
    lot = models.ForeignKey(CarbureLot, on_delete=models.CASCADE)
    comment_type = models.CharField(max_length=16, choices=COMMENT_TYPES, default=REGULAR)
    comment_dt = models.DateTimeField(auto_now_add=True)
    comment = models.TextField()
    is_visible_by_admin = models.BooleanField(default=False) # AUDITOR comment must be explicitly shared with admin
    is_visible_by_auditor = models.BooleanField(default=False) # ADMIN comment must be explicitly shared with auditor

    class Meta:
        db_table = 'carbure_lot_comments'
        indexes = [
            models.Index(fields=['lot']),
        ]        
        verbose_name = 'CarbureLotComment'
        verbose_name_plural = 'CarbureLotComments'
