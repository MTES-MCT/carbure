from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from transactions.models import Depot, ProductionSite

from .certificate import GenericCertificate
from .entity import Entity
from .feedstock import Biocarburant, MatierePremiere
from .geography import Pays

usermodel = get_user_model()


class TransactionDistance(models.Model):
    starting_point = models.CharField(max_length=64, blank=True, null=True, default=None)
    delivery_point = models.CharField(max_length=64, blank=True, null=True, default=None)
    distance = models.FloatField(default=0.0)

    class Meta:
        db_table = "transaction_distances"
        verbose_name = "Distance"
        verbose_name_plural = "Distances"


class CarbureLot(models.Model):
    period = models.IntegerField(blank=False, null=False)  # index
    year = models.IntegerField(blank=False, null=False)  # index
    carbure_id = models.CharField(max_length=64, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    # UDB
    udb_transaction_id = models.CharField(max_length=64, blank=True)

    # production data
    carbure_producer = models.ForeignKey(
        Entity, null=True, blank=True, default=None, on_delete=models.SET_NULL, related_name="carbure_producer"
    )
    unknown_producer = models.CharField(max_length=64, blank=True, null=True, default=None)
    carbure_production_site = models.ForeignKey(
        ProductionSite, null=True, blank=True, default=None, on_delete=models.SET_NULL
    )
    unknown_production_site = models.CharField(max_length=64, blank=True, null=True, default=None)
    production_country = models.ForeignKey(
        Pays, null=True, blank=True, default=None, on_delete=models.SET_NULL, related_name="production_country"
    )
    production_site_commissioning_date = models.DateField(blank=True, null=True)
    production_site_certificate = models.CharField(max_length=64, blank=True, null=True, default=None)
    production_site_certificate_type = models.CharField(max_length=64, blank=True, null=True, default=None)
    production_site_double_counting_certificate = models.CharField(max_length=64, blank=True, null=True, default=None)
    # supplier data
    carbure_supplier = models.ForeignKey(
        Entity, null=True, blank=True, on_delete=models.SET_NULL, related_name="carbure_supplier"
    )
    unknown_supplier = models.CharField(max_length=64, blank=True, null=True, default=None)
    supplier_certificate = models.CharField(max_length=64, blank=True, null=True, default=None)
    supplier_certificate_type = models.CharField(max_length=64, blank=True, null=True, default=None)

    # ONLY SET FOR SPECIFIC TRADING TRANSACTIONS
    carbure_vendor = models.ForeignKey(
        Entity, null=True, blank=True, on_delete=models.SET_NULL, related_name="carbure_vendor"
    )
    vendor_certificate = models.CharField(max_length=64, blank=True, null=True, default=None)
    vendor_certificate_type = models.CharField(max_length=64, blank=True, null=True, default=None)

    # delivery
    DAU = "DAU"
    DAE = "DAE"
    DSA = "DSA"
    DSAC = "DSAC"
    DSP = "DSP"
    OTHER = "OTHER"
    TRANSPORT_DOCUMENT_TYPES = (
        (DAU, DAU),
        (DAE, DAE),
        (DSA, DSA),
        (DSAC, DSAC),
        (DSP, DSP),
        (OTHER, OTHER),
    )
    transport_document_type = models.CharField(
        max_length=12, blank=False, null=False, choices=TRANSPORT_DOCUMENT_TYPES, default=DAE
    )
    transport_document_reference = models.CharField(max_length=128, blank=True, null=True, default=None)
    carbure_client = models.ForeignKey(
        Entity, null=True, blank=True, default=None, on_delete=models.SET_NULL, related_name="carbure_client"
    )
    unknown_client = models.CharField(max_length=64, blank=True, null=True, default=None)
    dispatch_date = models.DateField(blank=True, null=True)
    carbure_dispatch_site = models.ForeignKey(
        Depot, null=True, blank=True, default=None, on_delete=models.SET_NULL, related_name="carbure_dispatch_site"
    )
    unknown_dispatch_site = models.CharField(max_length=64, blank=True, null=True, default=None)
    dispatch_site_country = models.ForeignKey(
        Pays, null=True, blank=True, on_delete=models.SET_NULL, related_name="dispatch_site_country"
    )
    delivery_date = models.DateField(blank=True, null=True)
    carbure_delivery_site = models.ForeignKey(
        Depot, null=True, blank=True, default=None, on_delete=models.SET_NULL, related_name="carbure_delivery_site"
    )
    unknown_delivery_site = models.CharField(max_length=64, blank=True, null=True, default=None)
    delivery_site_country = models.ForeignKey(
        Pays, null=True, blank=True, on_delete=models.SET_NULL, related_name="delivery_site_country"
    )

    DRAFT = "DRAFT"
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    FROZEN = "FROZEN"
    DELETED = "DELETED"
    LOT_STATUSES = (
        (DRAFT, DRAFT),
        (PENDING, PENDING),
        (ACCEPTED, ACCEPTED),
        (REJECTED, REJECTED),
        (FROZEN, FROZEN),
        (DELETED, DELETED),
    )
    lot_status = models.CharField(max_length=24, choices=LOT_STATUSES, default=DRAFT)

    NO_PROBLEMO = "NO_PROBLEMO"
    IN_CORRECTION = "IN_CORRECTION"
    FIXED = "FIXED"
    CORRECTION_STATUSES = ((NO_PROBLEMO, NO_PROBLEMO), (IN_CORRECTION, IN_CORRECTION), (FIXED, FIXED))
    correction_status = models.CharField(max_length=64, choices=CORRECTION_STATUSES, default=NO_PROBLEMO)

    UNKNOWN = "UNKNOWN"
    RFC = "RFC"  # release for consumption / mise a consommation
    STOCK = "STOCK"
    BLENDING = "BLENDING"  # incorporation
    EXPORT = "EXPORT"
    TRADING = "TRADING"
    PROCESSING = "PROCESSING"
    DIRECT = "DIRECT"  # livraison directe
    FLUSHED = "FLUSHED"  # emptying stock for accounting or rounding purpose
    CONSUMPTION = "CONSUMPTION"  # consuming the biofuel for special uses
    DELIVERY_TYPES = (
        (UNKNOWN, UNKNOWN),
        (RFC, RFC),
        (STOCK, STOCK),
        (BLENDING, BLENDING),
        (EXPORT, EXPORT),
        (TRADING, TRADING),
        (PROCESSING, PROCESSING),
        (DIRECT, DIRECT),
        (FLUSHED, FLUSHED),
        (CONSUMPTION, CONSUMPTION),
    )
    delivery_type = models.CharField(max_length=64, choices=DELIVERY_TYPES, blank=False, null=False, default=UNKNOWN)
    declared_by_supplier = models.BooleanField(default=False)
    declared_by_client = models.BooleanField(default=False)

    # lot details
    volume = models.FloatField(default=0.0)
    weight = models.FloatField(default=0.0)
    lhv_amount = models.FloatField(default=0.0)
    feedstock = models.ForeignKey(MatierePremiere, null=True, on_delete=models.SET_NULL)
    biofuel = models.ForeignKey(Biocarburant, null=True, on_delete=models.SET_NULL)
    country_of_origin = models.ForeignKey(Pays, null=True, on_delete=models.SET_NULL, related_name="country_of_origin")

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
    parent_lot = models.ForeignKey("self", null=True, blank=True, on_delete=models.SET_NULL)
    parent_stock = models.ForeignKey("CarbureStock", null=True, blank=True, on_delete=models.SET_NULL)

    free_field = models.TextField(blank=True, null=True, default=None)

    # admin / auditor checks & filters
    highlighted_by_admin = models.BooleanField(default=False)  # admin requests audit of this lot
    highlighted_by_auditor = models.BooleanField(default=False)  # auditor suspicion - adds it to the control list
    random_control_requested = models.BooleanField(default=False)  # random control
    ml_control_requested = models.BooleanField(default=False)  # machine learning suspicion
    ml_scoring = models.FloatField(default=0.0)  # score calculated by machine learning script

    # auditor decision
    CONFORM = "CONFORM"
    NONCONFORM = "NONCONFORM"
    AUDIT_STATUS = ((UNKNOWN, UNKNOWN), (CONFORM, CONFORM), (NONCONFORM, NONCONFORM))
    audit_status = models.CharField(max_length=24, choices=AUDIT_STATUS, default=UNKNOWN)

    # scoring
    data_reliability_score = models.CharField(max_length=1, default="F")

    # saf
    pos_number = models.CharField(max_length=128, null=True)

    class Meta:
        db_table = "carbure_lots"
        indexes = [
            models.Index(fields=["year"]),
            models.Index(fields=["period"]),
            models.Index(fields=["biofuel"]),
            models.Index(fields=["feedstock"]),
            models.Index(fields=["carbure_supplier"]),
            models.Index(fields=["carbure_client"]),
            models.Index(fields=["carbure_delivery_site"]),
            models.Index(fields=["carbure_production_site"]),
            models.Index(fields=["year", "carbure_client"]),
            models.Index(fields=["year", "carbure_supplier"]),
            models.Index(fields=["year", "period"]),
            models.Index(fields=["year", "lot_status"]),
            models.Index(fields=["year", "period", "lot_status"]),
            models.Index(fields=["year", "period", "carbure_client"]),
            models.Index(fields=["year", "period", "carbure_supplier"]),
            models.Index(fields=["parent_lot"]),
            models.Index(fields=["parent_stock"]),
        ]
        verbose_name = "CarbureLot"
        verbose_name_plural = "CarbureLots"

    def __str__(self):
        return str(self.id)

    def get_volume(self):  # from mass
        if not self.biofuel:
            return 0
        if self.weight == 0:
            return 0
        return round(self.weight / self.biofuel.masse_volumique, 2)

    def get_weight(self):
        if not self.biofuel:
            return 0
        return round(self.volume * self.biofuel.masse_volumique, 2)

    def get_lhv_amount(self):
        if not self.biofuel:
            return 0
        return round(self.volume * self.biofuel.pci_litre, 2)

    def generate_carbure_id(self):
        country_of_production = "00"
        if self.production_country:
            country_of_production = self.production_country.code_pays
        delivery_site_id = "00"
        if self.carbure_delivery_site:
            delivery_site_id = self.carbure_delivery_site.depot_id
        self.carbure_id = "L{period}-{country_of_production}-{delivery_site_id}-{id}".format(
            period=self.period,
            country_of_production=country_of_production,
            delivery_site_id=delivery_site_id,
            id=self.id,
        )

    def copy_production_details(self, other):
        self.carbure_producer = other.carbure_producer
        self.unknown_producer = other.unknown_producer
        self.carbure_production_site = other.carbure_production_site
        self.unknown_production_site = other.unknown_production_site
        self.production_country = other.production_country
        self.production_site_commissioning_date = other.production_site_commissioning_date
        self.production_site_certificate = other.production_site_certificate
        self.production_site_certificate_type = other.production_site_certificate_type
        self.production_site_double_counting_certificate = other.production_site_double_counting_certificate

    def update_ghg(self):
        self.ghg_total = round(
            self.eec + self.el + self.ep + self.etd + self.eu - self.esca - self.eccs - self.eccr - self.eee, 2
        )
        self.ghg_reference = 83.8
        self.ghg_reduction = round((1.0 - (self.ghg_total / self.ghg_reference)) * 100.0, 2)
        self.ghg_reference_red_ii = 94.0
        self.ghg_reduction_red_ii = round((1.0 - (self.ghg_total / self.ghg_reference_red_ii)) * 100.0, 2)

    def copy_sustainability_data(self, other):
        self.biofuel = other.biofuel
        self.feedstock = other.feedstock
        self.country_of_origin = other.country_of_origin
        self.eec = other.eec
        self.el = other.el
        self.ep = other.ep
        self.etd = other.etd
        self.eu = other.eu
        self.esca = other.esca
        self.eccs = other.eccs
        self.eccr = other.eccr
        self.eee = other.eee
        self.ghg_total = other.ghg_total
        self.ghg_reference = other.ghg_reference
        self.ghg_reduction = other.ghg_reduction
        self.ghg_reference_red_ii = other.ghg_reference_red_ii
        self.ghg_reduction_red_ii = other.ghg_reduction_red_ii
        self.update_ghg()

    def recalc_reliability_score(self, prefetched_data):
        # data source is producer 3 POINTS
        data_source_is_producer = CarbureLotReliabilityScore(
            lot=self, item=CarbureLotReliabilityScore.DATA_SOURCE_IS_PRODUCER, max_score=3, score=0
        )
        if self.carbure_producer is not None:
            data_source_is_producer.score = 3

        # lot declared by both 1 POINT
        lot_declared_both = CarbureLotReliabilityScore(
            lot=self, item=CarbureLotReliabilityScore.LOT_DECLARED, max_score=1, score=0
        )
        if self.lot_status == CarbureLot.FROZEN:
            lot_declared_both.score = 1

        # certificates validated by DGEC 2 points
        certificates_validated = CarbureLotReliabilityScore(
            lot=self,
            item=CarbureLotReliabilityScore.CERTIFICATES_VALIDATED,
            max_score=2,
            score=0,
            meta={"producer_certificate_checked": False, "supplier_certificate_checked": False},
        )
        if (
            self.carbure_producer
            and self.carbure_producer.id in prefetched_data["entity_certificates"]
            and self.production_site_certificate in prefetched_data["entity_certificates"][self.carbure_producer.id]
            and prefetched_data["entity_certificates"][self.carbure_producer.id][
                self.production_site_certificate
            ].checked_by_admin
        ):
            certificates_validated.meta["producer_certificate_checked"] = True
            certificates_validated.score += 1
        if (
            self.carbure_supplier
            and self.carbure_supplier.id in prefetched_data["entity_certificates"]
            and self.supplier_certificate in prefetched_data["entity_certificates"][self.carbure_supplier.id]
            and prefetched_data["entity_certificates"][self.carbure_supplier.id][self.supplier_certificate].checked_by_admin
        ):
            certificates_validated.meta["supplier_certificate_checked"] = True
            certificates_validated.score += 1

        ### configuration issues
        config = CarbureLotReliabilityScore(
            lot=self,
            item=CarbureLotReliabilityScore.ANOMALIES_CONFIGURATION,
            max_score=1,
            score=0,
            meta={"feedstock_registered": False, "biofuel_registered": False, "delivery_site_registered": False},
        )
        if self.carbure_production_site and self.carbure_production_site.id in prefetched_data["production_sites"]:
            if self.feedstock.id in prefetched_data["production_sites"][self.carbure_production_site.id]["feedstock_ids"]:
                config.meta["feedstock_registered"] = True
            if self.biofuel.id in prefetched_data["production_sites"][self.carbure_production_site.id]["biofuel_ids"]:
                config.meta["biofuel_registered"] = True

        if self.carbure_delivery_site and self.carbure_client:
            if (
                self.carbure_client.id in prefetched_data["depotsbyentity"]
                and self.carbure_delivery_site.depot_id in prefetched_data["depotsbyentity"][self.carbure_client.id]
            ):
                config.meta["delivery_site_registered"] = True
        if (
            config.meta["feedstock_registered"]
            and config.meta["biofuel_registered"]
            and config.meta["delivery_site_registered"]
        ):
            config.score = 1

        # certificates
        certificates = CarbureLotReliabilityScore(
            lot=self,
            item=CarbureLotReliabilityScore.ANOMALIES_CERTIFICATES,
            max_score=1,
            score=0,
            meta={
                "producer_certificate_provided": False,
                "producer_certificate_exists": False,
                "supplier_certificate_provided": False,
                "supplier_certificate_exists": False,
            },
        )
        # certificates are provided
        if self.production_site_certificate:
            certificates.meta["producer_certificate_provided"] = True
        if self.supplier_certificate:
            certificates.meta["supplier_certificate_provided"] = True

        # certificates exist in our database
        if self.production_site_certificate in prefetched_data["checked_certificates"]:
            certificates.meta["producer_certificate_exists"] = prefetched_data["checked_certificates"][
                self.production_site_certificate
            ]
        elif GenericCertificate.objects.filter(certificate_id=self.production_site_certificate).count() > 0:
            certificates.meta["producer_certificate_exists"] = True
            prefetched_data["checked_certificates"][self.production_site_certificate] = True  # add to cache
        else:
            prefetched_data["checked_certificates"][self.production_site_certificate] = False  # add to cache

        if self.supplier_certificate in prefetched_data["checked_certificates"]:
            certificates.meta["supplier_certificate_exists"] = prefetched_data["checked_certificates"][
                self.supplier_certificate
            ]
        elif GenericCertificate.objects.filter(certificate_id=self.supplier_certificate).count() > 0:
            certificates.meta["supplier_certificate_exists"] = True
            prefetched_data["checked_certificates"][self.supplier_certificate] = True  # add to cache
        else:
            prefetched_data["checked_certificates"][self.supplier_certificate] = False  # add to cache

        if (
            certificates.meta["producer_certificate_provided"]
            and certificates.meta["producer_certificate_exists"]
            and certificates.meta["supplier_certificate_provided"]
            and certificates.meta["supplier_certificate_exists"]
        ):
            certificates.score = 1

        score_entries = [data_source_is_producer, lot_declared_both, certificates_validated, config, certificates]
        nb_points = sum([s.score for s in score_entries])
        if nb_points == 8:
            self.data_reliability_score = "A"
        elif nb_points >= 6:
            self.data_reliability_score = "B"
        elif nb_points >= 3:
            self.data_reliability_score = "C"
        elif nb_points >= 1:
            self.data_reliability_score = "D"
        else:
            self.data_reliability_score = "E"
        return score_entries


class CarbureLotReliabilityScore(models.Model):
    CUSTOMS_AND_CARBURE_MATCH = "CUSTOMS_AND_CARBURE_MATCH"  # 0 or 4 --- NO META
    DATA_SOURCE_IS_PRODUCER = "DATA_SOURCE_IS_PRODUCER"  # 0 or 3 --- NO META
    LOT_DECLARED = "LOT_DECLARED"  # 0 or 1 --- NO META

    CERTIFICATES_VALIDATED = "CERTIFICATES_VALIDATED"  # 0, 1, 2 --- META
    ANOMALIES_CERTIFICATES = "ANOMALIES_CERTIFICATES"  # 0, 1 --- META
    ANOMALIES_CONFIGURATION = "ANOMALIES_CONFIGURATION"  # 0, 1 ---META

    SCORE_ITEMS = (
        (CUSTOMS_AND_CARBURE_MATCH, CUSTOMS_AND_CARBURE_MATCH),
        (DATA_SOURCE_IS_PRODUCER, DATA_SOURCE_IS_PRODUCER),
        (LOT_DECLARED, LOT_DECLARED),
        (ANOMALIES_CERTIFICATES, ANOMALIES_CERTIFICATES),
        (ANOMALIES_CONFIGURATION, ANOMALIES_CONFIGURATION),
    )

    lot = models.ForeignKey(CarbureLot, blank=False, null=False, on_delete=models.CASCADE)
    max_score = models.FloatField(default=1)
    score = models.FloatField(default=1)
    item = models.CharField(max_length=32, choices=SCORE_ITEMS, blank=False, null=False, default="Unknown")
    meta = models.JSONField(blank=True, null=True, default=None)

    def __str__(self):
        return self.item

    class Meta:
        db_table = "carbure_lots_scores"
        indexes = [
            models.Index(fields=["lot"]),
        ]
        verbose_name = "CarbureLotReliabilityScore"
        verbose_name_plural = "CarbureLotReliabilityScores"


class GenericError(models.Model):
    error = models.CharField(max_length=256, null=False, blank=False)

    display_to_creator = models.BooleanField(default=False)
    display_to_recipient = models.BooleanField(default=False)
    display_to_admin = models.BooleanField(default=False)
    display_to_auditor = models.BooleanField(default=False)

    acked_by_creator = models.BooleanField(default=False)
    acked_by_recipient = models.BooleanField(default=False)
    acked_by_admin = models.BooleanField(default=False)
    acked_by_auditor = models.BooleanField(default=False)

    highlighted_by_admin = models.BooleanField(default=False)
    highlighted_by_auditor = models.BooleanField(default=False)

    is_blocking = models.BooleanField(default=False)

    lot = models.ForeignKey("CarbureLot", null=True, blank=True, on_delete=models.SET_NULL)

    field = models.CharField(max_length=64, null=True, blank=True)
    fields = models.JSONField(null=True, blank=True)
    value = models.CharField(max_length=128, null=True, blank=True)
    extra = models.CharField(max_length=256, null=True, blank=True)

    class Meta:
        db_table = "generic_errors"
        verbose_name = "Generic Error"
        verbose_name_plural = "Generic Errors"
        indexes = [
            models.Index(fields=["lot"]),
            models.Index(fields=["lot", "acked_by_admin", "display_to_admin"]),
            models.Index(fields=["lot", "acked_by_creator", "display_to_creator"]),
            models.Index(fields=["lot", "acked_by_recipient", "display_to_recipient"]),
            models.Index(fields=["lot", "acked_by_auditor", "display_to_auditor"]),
        ]


class CarbureLotEvent(models.Model):
    CREATED = "CREATED"
    UPDATED = "UPDATED"
    UPDATED_BY_ADMIN = "UPDATED_BY_ADMIN"
    VALIDATED = "VALIDATED"
    FIX_REQUESTED = "FIX_REQUESTED"
    MARKED_AS_FIXED = "MARKED_AS_FIXED"
    FIX_ACCEPTED = "FIX_ACCEPTED"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    RECALLED = "RECALLED"
    DECLARED = "DECLARED"
    DECLCANCEL = "DECLCANCEL"
    DELETED = "DELETED"
    DELETED_BY_ADMIN = "DELETED_BY_ADMIN"
    RESTORED = "RESTORED"
    CANCELLED = "CANCELLED"
    EVENT_TYPES = (
        (CREATED, CREATED),
        (UPDATED, UPDATED),
        (VALIDATED, VALIDATED),
        (FIX_REQUESTED, FIX_REQUESTED),
        (MARKED_AS_FIXED, MARKED_AS_FIXED),
        (FIX_ACCEPTED, FIX_ACCEPTED),
        (ACCEPTED, ACCEPTED),
        (REJECTED, REJECTED),
        (RECALLED, RECALLED),
        (DECLARED, DECLARED),
        (DELETED, DELETED),
        (DECLCANCEL, DECLCANCEL),
        (RESTORED, RESTORED),
        (CANCELLED, CANCELLED),
        (UPDATED_BY_ADMIN, UPDATED_BY_ADMIN),
        (DELETED_BY_ADMIN, DELETED_BY_ADMIN),
    )
    event_type = models.CharField(max_length=32, null=False, blank=False, choices=EVENT_TYPES)
    event_dt = models.DateTimeField(auto_now_add=True, null=False, blank=False)
    lot = models.ForeignKey(CarbureLot, null=False, blank=False, on_delete=models.CASCADE)
    user = models.ForeignKey(usermodel, null=True, blank=True, on_delete=models.SET_NULL)
    metadata = models.JSONField(null=True, blank=True)
    entity = models.ForeignKey(Entity, null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        db_table = "carbure_lots_events"
        indexes = [
            models.Index(fields=["lot"]),
        ]
        verbose_name = "CarbureLotEvent"
        verbose_name_plural = "CarbureLotEvents"


class CarbureLotComment(models.Model):
    REGULAR = "REGULAR"
    AUDITOR = "AUDITOR"
    ADMIN = "ADMIN"
    COMMENT_TYPES = ((REGULAR, REGULAR), (AUDITOR, AUDITOR), (ADMIN, ADMIN))

    entity = models.ForeignKey(Entity, null=True, blank=True, on_delete=models.SET_NULL)
    user = models.ForeignKey(usermodel, null=True, blank=True, on_delete=models.SET_NULL)
    lot = models.ForeignKey(CarbureLot, on_delete=models.CASCADE)
    comment_type = models.CharField(max_length=16, choices=COMMENT_TYPES, default=REGULAR)
    comment_dt = models.DateTimeField(auto_now_add=True)
    comment = models.TextField()
    is_visible_by_admin = models.BooleanField(default=False)  # AUDITOR comment must be explicitly shared with admin
    is_visible_by_auditor = models.BooleanField(default=False)  # ADMIN comment must be explicitly shared with auditor

    class Meta:
        db_table = "carbure_lots_comments"
        indexes = [
            models.Index(fields=["lot"]),
        ]
        verbose_name = "CarbureLotComment"
        verbose_name_plural = "CarbureLotComments"


@receiver(pre_save, sender=CarbureLot)
def lot_pre_save_update_quantities(sender, instance, *args, **kwargs):
    if instance.volume == 0:
        instance.volume = instance.get_volume()
    if instance.weight == 0:
        instance.weight = instance.get_weight()
    if instance.lhv_amount == 0:
        instance.lhv_amount = instance.get_lhv_amount()


@receiver(post_save, sender=CarbureLot)
def lot_post_save_gen_carbure_id(sender, instance, created, update_fields=None, *args, **kwargs):
    if update_fields is None:
        update_fields = {}
    old_carbure_id = instance.carbure_id
    instance.generate_carbure_id()

    if instance.carbure_id != old_carbure_id and instance.lot_status in ("PENDING", "ACCEPTED", "REJECTED", "FROZEN"):
        instance.save(update_fields=["carbure_id"])
