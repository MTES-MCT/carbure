import datetime
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.auth import get_user_model
import hashlib
from django.db.models.signals import pre_delete, pre_save
from django.dispatch import receiver

usermodel = get_user_model()

class Entity(models.Model):
    PRODUCER = 'Producteur'
    OPERATOR = 'Opérateur'
    TRADER = 'Trader'
    ADMIN = 'Administration'
    AUDITOR = 'Auditor'
    EXTERNAL_ADMIN = 'Administration Externe'
    UNKNOWN = 'Unknown'
    ENTITY_TYPES = ((PRODUCER, 'Producteur'), (OPERATOR, 'Opérateur'),
                    (ADMIN, 'Administration'), (TRADER, 'Trader'),
                    (AUDITOR, 'Auditeur'), (EXTERNAL_ADMIN, EXTERNAL_ADMIN),
                    (UNKNOWN, 'Unknown'))

    name = models.CharField(max_length=64, unique=True)
    date_added = models.DateTimeField(auto_now_add=True)
    entity_type = models.CharField(max_length=64, choices=ENTITY_TYPES, default='Unknown')
    parent_entity = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE)

    has_mac = models.BooleanField(default=False)
    has_trading = models.BooleanField(default=False)
    has_stocks = models.BooleanField(default=False)
    has_direct_deliveries = models.BooleanField(default=False)

    legal_name = models.CharField(max_length=128, blank=True, default='')
    registration_id = models.CharField(max_length=64, blank=True, default='')
    sustainability_officer_phone_number = models.CharField(max_length=32, blank=True, default='')
    sustainability_officer = models.CharField(max_length=256, blank=True, default='')
    registered_address = models.TextField(blank=True, default='')
    hash = models.CharField(max_length=32, null=True, blank=True, default='')
    default_certificate = models.CharField(max_length=64, null=True, blank=True, default='')
    notifications_enabled = models.BooleanField(default=False)
    preferred_unit = models.CharField(max_length=64, choices=(('l', 'litres'), ('kg', 'kg'), ('MJ', 'MJ')), default='l')

    def __str__(self):
        return self.name

    def natural_key(self):
        d = {'name': self.name, 'id': self.id, 'entity_type': self.entity_type,
            'has_mac': self.has_mac, 'has_trading': self.has_trading, 'has_direct_deliveries': self.has_direct_deliveries, 'has_stocks': self.has_stocks,
            'legal_name': self.legal_name, 'registration_id': self.registration_id,
            'sustainability_officer': self.sustainability_officer, 'sustainability_officer_phone_number': self.sustainability_officer_phone_number,
            'registered_address': self.registered_address, 'default_certificate': self.default_certificate, 'preferred_unit': self.preferred_unit}
        if self.entity_type == Entity.EXTERNAL_ADMIN:
            d['ext_admin_pages'] = [e.right for e in self.externaladminrights_set.all()]
        return d

    def url_friendly_name(self):
        return self.name.replace(' ', '').upper()

    def save(self, *args, **kwargs):
        date_added = self.date_added
        if not date_added:
            date_added = datetime.date.today()
        data = self.name + self.entity_type + date_added.strftime('%Y%m%d')
        hash = hashlib.md5(data.encode('utf-8')).hexdigest()
        self.hash = hash
        super(Entity, self).save(*args, **kwargs)


    class Meta:
        db_table = 'entities'
        verbose_name = 'Entity'
        verbose_name_plural = 'Entities'



class UserPreferences(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    default_entity = models.ForeignKey(Entity, blank=True, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.user.email

    class Meta:
        db_table = 'users_preferences'
        verbose_name = 'User Preference'
        verbose_name_plural = 'User Preferences'


class UserRights(models.Model):
    RO = 'RO'
    RW = 'RW'
    ADMIN = 'ADMIN'
    AUDITOR = 'AUDITOR'
    ROLES = ((RO, 'Lecture Seule'), (RW, 'Lecture/Écriture'), (ADMIN, 'Administrateur'), (AUDITOR, 'Auditeur'))

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE)
    date_added = models.DateTimeField(auto_now_add=True)
    role = models.CharField(max_length=32, choices=ROLES, default=RO)
    expiration_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return '%s - %s' % (self.user.email, self.entity.name)

    def natural_key(self):
        return {'name': self.user.name, 'email': self.user.email, 'entity': self.entity.natural_key(),
                'role': self.role, 'expiration_date': self.expiration_date}

    class Meta:
        db_table = 'users_rights'
        verbose_name = 'User Right'
        verbose_name_plural = 'Users Rights'


class UserRightsRequests(models.Model):
    STATUS_TYPES = (('PENDING', 'En attente de validation'), ('ACCEPTED', 'Accepté'), ('REJECTED', 'Refusé'), ('REVOKED', 'Révoqué'))

    RO = 'RO'
    RW = 'RW'
    ADMIN = 'ADMIN'
    AUDITOR = 'AUDITOR'
    ROLES = ((RO, 'Lecture Seule'), (RW, 'Lecture/Écriture'), (ADMIN, 'Administrateur'), (AUDITOR, 'Auditeur'))

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE)
    date_requested = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=32, choices=STATUS_TYPES, default='PENDING')
    comment = models.TextField(blank=True, null=True)

    role = models.CharField(max_length=32, choices=ROLES, default=RO)
    expiration_date = models.DateTimeField(null=True, blank=True)

    def natural_key(self):
        return {'id': self.id, 'user': self.user.natural_key(), 'entity': self.entity.natural_key(),
                'date_requested': self.date_requested, 'status': self.status, 'comment': self.comment,
                'role': self.role, 'expiration_date': self.expiration_date}

    class Meta:
        db_table = 'users_rights_requests'
        verbose_name = 'User Right Request'
        verbose_name_plural = 'Users Rights Requests'


class Biocarburant(models.Model):
    name = models.CharField(max_length=64)
    name_en = models.CharField(max_length=64)
    description = models.CharField(max_length=128)
    date_added = models.DateField(default=timezone.now)
    code = models.CharField(max_length=16, unique=True)
    pci_kg = models.FloatField(default=0)
    pci_litre = models.FloatField(default=0)
    masse_volumique = models.FloatField(default=0)
    is_alcool = models.BooleanField(default=False)
    is_graisse = models.BooleanField(default=False)
    is_displayed = models.BooleanField(default=True)

    compatible_essence = models.BooleanField(default=False)
    compatible_diesel = models.BooleanField(default=False)
    dgddi_category = models.CharField(max_length=8, blank=True, null=True, default=None)

    def __str__(self):
        return self.name

    def __eq__(self, other):
        return self.code == other

    def __hash__(self):
        return super().__hash__()

    def natural_key(self):
        return {'code': self.code, 'name': self.name}

    class Meta:
        db_table = 'biocarburants'
        verbose_name = 'Biocarburant'
        verbose_name_plural = 'Biocarburants'


class MatierePremiere(models.Model):
    CONV = 'CONV'
    IXA = 'ANN-IX-A'
    IXB = 'ANN-IX-B'
    TALLOL = 'TALLOL'
    OTHER = 'OTHER'

    MP_CATEGORIES = ((CONV, 'Conventionnel'), (IXA, 'ANNEXE IX-A'), (IXB, 'ANNEXE IX-B'), (TALLOL, 'Tallol'), (OTHER, 'Autre'))

    name = models.CharField(max_length=128)
    name_en = models.CharField(max_length=128)
    description = models.CharField(max_length=128)
    date_added = models.DateField(default=timezone.now)
    code = models.CharField(max_length=64, unique=True)
    compatible_alcool = models.BooleanField(default=False)
    compatible_graisse = models.BooleanField(default=False)
    is_double_compte = models.BooleanField(default=False)
    is_huile_vegetale = models.BooleanField(default=False)
    is_displayed = models.BooleanField(default=True)
    category = models.CharField(max_length=32, choices=MP_CATEGORIES, default='CONV')
    dgddi_category = models.CharField(max_length=32, blank=True, null=True, default=None)

    def __str__(self):
        return self.name

    def natural_key(self):
        return {'code': self.code, 'name': self.name, 'is_double_compte': self.is_double_compte, 'category': self.category}

    class Meta:
        db_table = 'matieres_premieres'
        verbose_name = 'Matiere Premiere'
        verbose_name_plural = 'Matieres Premieres'


class Pays(models.Model):
    code_pays = models.CharField(max_length=64)
    name = models.CharField(max_length=128)
    name_en = models.CharField(max_length=128)
    date_added = models.DateField(default=timezone.now)
    is_in_europe = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    def natural_key(self):
        return {'code_pays': self.code_pays, 'name': self.name, 'name_en': self.name_en, 'is_in_europe': self.is_in_europe}

    class Meta:
        db_table = 'pays'
        verbose_name = 'Pays'
        verbose_name_plural = 'Pays'


class Depot(models.Model):
    EFS = 'EFS'
    EFPE = 'EFPE'
    OTHER = 'OTHER'
    OILDEPOT = 'OIL DEPOT'
    BIOFUELDEPOT = 'BIOFUEL DEPOT'

    TYPE_DEPOT = ((EFS, 'EFS'), (EFPE, 'EFPE'), (OILDEPOT, "OIL DEPOT"), (BIOFUELDEPOT, "BIOFUEL DEPOT"), (OTHER, 'Autre'),)
    name = models.CharField(max_length=128, null=False, blank=False)
    city = models.CharField(max_length=128, null=True, blank=True)
    depot_id = models.CharField(max_length=32, null=False, blank=False)
    country = models.ForeignKey(Pays, null=True, blank=False, on_delete=models.SET_NULL)
    depot_type = models.CharField(max_length=32, choices=TYPE_DEPOT, default=OTHER)

    address = models.CharField(max_length=128, blank=True)
    postal_code = models.CharField(max_length=32, blank=True)

    gps_coordinates = models.CharField(max_length=64, blank=True, null=True, default=None)
    accise = models.CharField(max_length=32, blank=True, null=True, default=None)

    def __str__(self):
        return self.name

    def natural_key(self):
        return {'depot_id': self.depot_id, 'name': self.name, 'city': self.city, 'country': self.country.natural_key(),
            'depot_type': self.depot_type, 'address': self.address, 'postal_code': self.postal_code}

    class Meta:
        db_table = 'depots'
        verbose_name = 'Dépôt'
        verbose_name_plural = 'Dépôts'

class EntityDepot(models.Model):
    OWN = 'OWN'
    THIRD_PARTY = 'THIRD_PARTY'
    PROCESSING = 'PROCESSING'
    TYPE_OWNERSHIP = ((OWN, 'Propre'), (THIRD_PARTY, 'Tiers'), (PROCESSING, 'Processing'))

    entity = models.ForeignKey(Entity, null=False, blank=False, on_delete=models.CASCADE)
    depot = models.ForeignKey(Depot, null=False, blank=False, on_delete=models.CASCADE)
    ownership_type = models.CharField(max_length=32, choices=TYPE_OWNERSHIP, default=THIRD_PARTY)
    blending_is_outsourced = models.BooleanField(default=False)
    blender = models.ForeignKey(Entity, null=True, blank=True, on_delete=models.CASCADE, related_name='blender')

    def __str__(self):
        return str(self.id)

    def natural_key(self):
        return {'depot': self.depot.natural_key(), 'ownership_type': self.ownership_type, 'blending_is_outsourced': self.blending_is_outsourced, 'blender': self.blender.natural_key() if self.blender else None}

    class Meta:
        db_table = 'entity_depot'
        verbose_name = 'Dépôt Entité'
        verbose_name_plural = 'Dépôts Entité'


from producers.models import ProductionSite, ProductionSiteInput, ProductionSiteOutput


class SustainabilityDeclaration(models.Model):
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE)
    declared = models.BooleanField(default=False)
    checked = models.BooleanField(default=False)
    deadline = models.DateField(default=datetime.datetime.now, blank=True)
    period = models.DateField(default=datetime.datetime.now, blank=True)
    reminder_count = models.IntegerField(default=0)

    def natural_key(self):
        return {'id': self.id,'entity': self.entity.natural_key(), 'declared': self.declared, 'period': self.period, 'deadline': self.deadline, 'checked': self.checked, 'month': self.period.month, 'year': self.period.year, 'reminder_count': self.reminder_count}

    class Meta:
        db_table = 'declarations'
        verbose_name = ' Déclaration de Durabilité'
        verbose_name_plural = ' Déclarations de Durabilité'



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

    lot = models.ForeignKey('CarbureLot', null=True, blank=True, on_delete=models.SET_NULL)

    field = models.CharField(max_length=64, null=True, blank=True)
    fields = models.JSONField(null=True, blank=True)
    value = models.CharField(max_length=128, null=True, blank=True)
    extra = models.CharField(max_length=256, null=True, blank=True)


    class Meta:
        db_table = 'generic_errors'
        verbose_name = 'Generic Error'
        verbose_name_plural = 'Generic Errors'


class TransactionDistance(models.Model):
    starting_point = models.CharField(max_length=64, blank=True, null=True, default=None)
    delivery_point = models.CharField(max_length=64, blank=True, null=True, default=None)
    distance = models.FloatField(default=0.0)

    class Meta:
        db_table = 'transaction_distances'
        verbose_name = 'Distance'
        verbose_name_plural = 'Distances'

class ExternalAdminRights(models.Model):
    DOUBLE_COUNTING_AGREEMENT = "DCA"
    CUSTOM_STATS_AGRIMER = "AGRIMER"
    TIRIB_STATS = "TIRIB"

    RIGHTS = ((DOUBLE_COUNTING_AGREEMENT, DOUBLE_COUNTING_AGREEMENT), (CUSTOM_STATS_AGRIMER, CUSTOM_STATS_AGRIMER), (TIRIB_STATS, TIRIB_STATS))
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE)
    right = models.CharField(max_length=32, choices=RIGHTS, default='', blank=False, null=False)

    class Meta:
        db_table = 'ext_admin_rights'
        verbose_name = 'External Admin Right'
        verbose_name_plural = 'External Admin Rights'


from django.db import models
from django.contrib.auth import get_user_model

from core.models import Entity, Depot, ProductionSite, MatierePremiere, Pays, Biocarburant

usermodel = get_user_model()

class CarbureLot(models.Model):
    period = models.IntegerField(blank=False, null=False) # index
    year = models.IntegerField(blank=False, null=False) # index
    carbure_id = models.CharField(max_length=64, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    # production data
    carbure_producer = models.ForeignKey(Entity, null=True, blank=True, default=None, on_delete=models.SET_NULL, related_name='carbure_producer')
    unknown_producer = models.CharField(max_length=64, blank=True, null=True, default=None)
    carbure_production_site = models.ForeignKey(ProductionSite, null=True, blank=True, default=None, on_delete=models.SET_NULL)
    unknown_production_site = models.CharField(max_length=64, blank=True, null=True, default=None)
    production_country = models.ForeignKey(Pays, null=True, blank=True, default=None, on_delete=models.SET_NULL, related_name='production_country')
    production_site_commissioning_date = models.DateField(blank=True, null=True)
    production_site_certificate = models.CharField(max_length=64, blank=True, null=True, default=None)
    production_site_certificate_type = models.CharField(max_length=64, blank=True, null=True, default=None)
    production_site_double_counting_certificate = models.CharField(max_length=64, blank=True, null=True, default=None)
    # supplier data
    carbure_supplier = models.ForeignKey(Entity, null=True, blank=True, on_delete=models.SET_NULL, related_name='carbure_supplier')
    unknown_supplier = models.CharField(max_length=64, blank=True, null=True, default=None)
    supplier_certificate = models.CharField(max_length=64, blank=True, null=True, default=None)
    supplier_certificate_type = models.CharField(max_length=64, blank=True, null=True, default=None)

    # ONLY SET FOR SPECIFIC TRADING TRANSACTIONS
    carbure_vendor = models.ForeignKey(Entity, null=True, blank=True, on_delete=models.SET_NULL, related_name='carbure_vendor')
    vendor_certificate = models.CharField(max_length=64, blank=True, null=True, default=None)
    vendor_certificate_type = models.CharField(max_length=64, blank=True, null=True, default=None)


    # delivery
    DAU = "DAU"
    DAE = "DAE"
    DSA = "DSA"
    DSAC = "DSAC"
    DSP = "DSP"
    OTHER = "OTHER"
    TRANSPORT_DOCUMENT_TYPES = ((DAU, DAU), (DAE, DAE), (DSA, DSA), (DSAC, DSAC), (DSP, DSP), (OTHER, OTHER),)
    transport_document_type = models.CharField(max_length=12, blank=False, null=False, choices=TRANSPORT_DOCUMENT_TYPES, default=DAE)
    transport_document_reference = models.CharField(max_length=128, blank=True, null=True, default=None)
    carbure_client = models.ForeignKey(Entity, null=True, blank=True, default=None, on_delete=models.SET_NULL, related_name='carbure_client')
    unknown_client = models.CharField(max_length=64, blank=True, null=True, default=None)
    dispatch_date = models.DateField(blank=True, null=True)
    carbure_dispatch_site = models.ForeignKey(Depot, null=True, blank=True, default=None, on_delete=models.SET_NULL, related_name='carbure_dispatch_site')
    unknown_dispatch_site = models.CharField(max_length=64, blank=True, null=True, default=None)
    dispatch_site_country = models.ForeignKey(Pays, null=True, blank=True, on_delete=models.SET_NULL, related_name='dispatch_site_country')
    delivery_date = models.DateField(blank=True, null=True)
    carbure_delivery_site = models.ForeignKey(Depot, null=True, blank=True, default=None, on_delete=models.SET_NULL, related_name='carbure_delivery_site')
    unknown_delivery_site = models.CharField(max_length=64, blank=True, null=True, default=None)
    delivery_site_country = models.ForeignKey(Pays, null=True, blank=True, on_delete=models.SET_NULL, related_name='delivery_site_country')

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
    FLUSHED = "FLUSHED" # emptying stock for accounting or rounding purpose
    DELIVERY_TYPES = ((UNKNOWN, UNKNOWN), (RFC, RFC), (STOCK, STOCK), (BLENDING, BLENDING), (EXPORT, EXPORT),
                      (TRADING, TRADING), (PROCESSING, PROCESSING), (DIRECT, DIRECT), (FLUSHED, FLUSHED))
    delivery_type = models.CharField(max_length=64, choices=DELIVERY_TYPES, blank=False, null=False, default=UNKNOWN)
    declared_by_supplier = models.BooleanField(default=False)
    declared_by_client = models.BooleanField(default=False)


    # lot details
    volume = models.FloatField(default=0.0)
    weight = models.FloatField(default=0.0)
    lhv_amount = models.FloatField(default=0.0)
    feedstock = models.ForeignKey(MatierePremiere, null=True, on_delete=models.SET_NULL)
    biofuel = models.ForeignKey(Biocarburant, null=True, on_delete=models.SET_NULL)
    country_of_origin = models.ForeignKey(Pays, null=True, on_delete=models.SET_NULL, related_name='country_of_origin')

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
    highlighted_by_admin = models.BooleanField(default=False) # admin requests audit of this lot
    highlighted_by_auditor = models.BooleanField(default=False) # auditor suspicion - adds it to the control list
    random_control_requested = models.BooleanField(default=False) # random control
    ml_control_requested = models.BooleanField(default=False) # machine learning suspicion

    # auditor decision
    CONFORM = "CONFORM"
    NONCONFORM = "NONCONFORM"
    AUDIT_STATUS = ((UNKNOWN, UNKNOWN), (CONFORM, CONFORM), (NONCONFORM, NONCONFORM))
    audit_status = models.CharField(max_length=24, choices=AUDIT_STATUS, default=UNKNOWN)

    # scoring
    data_reliability_score = models.CharField(max_length=1, default='F')

    class Meta:
        db_table = 'carbure_lots'
        indexes = [models.Index(fields=['year']),
                   models.Index(fields=['year', 'carbure_client']),
                   models.Index(fields=['year', 'carbure_supplier']),
                   models.Index(fields=['year', 'period']),
                   models.Index(fields=['year', 'period', 'carbure_client']),
                   models.Index(fields=['year', 'period', 'carbure_supplier']),
                  ]
        verbose_name = 'CarbureLot'
        verbose_name_plural = 'CarbureLots'

    def __str__(self):
        return str(self.id)


    def get_weight(self):
        if not self.biofuel:
            return 0
        return self.volume * self.biofuel.masse_volumique

    def get_lhv_amount(self):
        if not self.biofuel:
            return 0
        return self.volume * self.biofuel.pci_litre

    def generate_carbure_id(self):
        country_of_production = '00'
        if self.production_country:
            country_of_production = self.production_country.code_pays
        delivery_site_id = '00'
        if self.carbure_delivery_site:
            delivery_site_id = self.carbure_delivery_site.depot_id
        self.carbure_id = 'L{period}-{country_of_production}-{delivery_site_id}-{id}'.format(period=self.period, country_of_production=country_of_production, delivery_site_id=delivery_site_id, id=self.id)

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
        self.ghg_total = round(self.eec + self.el + self.ep + self.etd + self.eu - self.esca - self.eccs - self.eccr - self.eee, 2)
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
        data_source_is_producer = CarbureLotReliabilityScore(lot=self, item=CarbureLotReliabilityScore.DATA_SOURCE_IS_PRODUCER, max_score=3, score=0)
        if self.carbure_producer != None:
            data_source_is_producer.score = 3

        # lot declared by both 1 POINT
        lot_declared_both = CarbureLotReliabilityScore(lot=self, item=CarbureLotReliabilityScore.LOT_DECLARED, max_score=1, score=0)
        if self.lot_status == CarbureLot.FROZEN:
            lot_declared_both.score = 1

        # certificates validated by DGEC 2 points
        certificates_validated = CarbureLotReliabilityScore(lot=self, item=CarbureLotReliabilityScore.CERTIFICATES_VALIDATED, max_score=2, score=0, meta={'producer_certificate_checked': False, 'supplier_certificate_checked': False})
        if self.carbure_producer \
            and self.carbure_producer.id in prefetched_data['entity_certificates'] \
            and self.production_site_certificate in prefetched_data['entity_certificates'][self.carbure_producer.id] \
            and prefetched_data['entity_certificates'][self.carbure_producer.id][self.production_site_certificate].checked_by_admin:
                certificates_validated.meta['producer_certificate_checked'] = True
                certificates_validated.score += 1
        if self.carbure_supplier \
            and self.carbure_supplier.id in prefetched_data['entity_certificates'] \
            and self.supplier_certificate in prefetched_data['entity_certificates'][self.carbure_supplier.id] \
            and prefetched_data['entity_certificates'][self.carbure_supplier.id][self.supplier_certificate].checked_by_admin:
                certificates_validated.meta['supplier_certificate_checked'] = True
                certificates_validated.score += 1

        ### configuration issues
        config = CarbureLotReliabilityScore(lot=self, item=CarbureLotReliabilityScore.ANOMALIES_CONFIGURATION, max_score=1, score=0, meta={'feedstock_registered': False, 'biofuel_registered': False, 'delivery_site_registered': False})
        if self.carbure_production_site and self.carbure_production_site.id in prefetched_data['production_sites']:
            if self.feedstock.id in prefetched_data['production_sites'][self.carbure_production_site.id]['feedstock_ids']:
                config.meta['feedstock_registered'] = True
            if self.biofuel.id in prefetched_data['production_sites'][self.carbure_production_site.id]['biofuel_ids']:
                config.meta['biofuel_registered'] = True
        if self.carbure_delivery_site and self.carbure_client and self.carbure_client.id in prefetched_data['depotsbyentity'] and self.carbure_delivery_site.depot_id in prefetched_data['depotsbyentity'][self.carbure_client.id]:
            config.meta['delivery_site_registered'] = True
        if config.meta['feedstock_registered'] and config.meta['biofuel_registered'] and config.meta['delivery_site_registered']:
            config.score = 1

        # certificates
        certificates = CarbureLotReliabilityScore(lot=self, item=CarbureLotReliabilityScore.ANOMALIES_CERTIFICATES, max_score=1, score=0, 
        meta={'producer_certificate_provided': False, 'producer_certificate_exists': False, 
            'supplier_certificate_provided': False, 'supplier_certificate_exists':False})
        # certificates are provided
        if self.production_site_certificate:
            certificates.meta['producer_certificate_provided'] = True
        if self.supplier_certificate:
            certificates.meta['supplier_certificate_provided'] = True

        # certificates exist in our database
        if self.production_site_certificate in prefetched_data['checked_certificates']:
            certificates.meta['producer_certificate_exists'] = prefetched_data['checked_certificates'][self.production_site_certificate]
        elif GenericCertificate.objects.filter(certificate_id=self.production_site_certificate).count() > 0:
            certificates.meta['producer_certificate_exists'] = True
            prefetched_data['checked_certificates'][self.production_site_certificate] = True # add to cache
        else:
            prefetched_data['checked_certificates'][self.production_site_certificate] = False # add to cache

        if self.supplier_certificate in prefetched_data['checked_certificates']:
            certificates.meta['supplier_certificate_exists'] = prefetched_data['checked_certificates'][self.supplier_certificate]
        elif GenericCertificate.objects.filter(certificate_id=self.supplier_certificate).count() > 0:
            certificates.meta['supplier_certificate_exists'] = True
            prefetched_data['checked_certificates'][self.supplier_certificate] = True # add to cache
        else:
            prefetched_data['checked_certificates'][self.supplier_certificate] = False # add to cache

        if certificates.meta['producer_certificate_provided'] and certificates.meta['producer_certificate_exists'] and certificates.meta['supplier_certificate_provided'] and certificates.meta['supplier_certificate_exists']:
            certificates.score = 1
        
        score_entries = [data_source_is_producer, lot_declared_both, certificates_validated, config, certificates]
        nb_points = sum([s.score for s in score_entries])
        if nb_points == 8:
            self.data_reliability_score = 'A'
        elif nb_points >= 6:
            self.data_reliability_score = 'B'
        elif nb_points >= 3:
            self.data_reliability_score = 'C'
        elif nb_points >= 1:
            self.data_reliability_score = 'D'
        else:
            self.data_reliability_score = 'E'
        return score_entries

class CarbureLotReliabilityScore(models.Model):
    CUSTOMS_AND_CARBURE_MATCH = "CUSTOMS_AND_CARBURE_MATCH" # 0 or 4 --- NO META
    DATA_SOURCE_IS_PRODUCER = "DATA_SOURCE_IS_PRODUCER" # 0 or 3 --- NO META
    LOT_DECLARED = "LOT_DECLARED" # 0 or 1 --- NO META

    CERTIFICATES_VALIDATED = "CERTIFICATES_VALIDATED" # 0, 1, 2 --- META
    ANOMALIES_CERTIFICATES = "ANOMALIES_CERTIFICATES" # 0, 1 --- META
    ANOMALIES_CONFIGURATION = "ANOMALIES_CONFIGURATION" # 0, 1 ---META

    SCORE_ITEMS = ((CUSTOMS_AND_CARBURE_MATCH, CUSTOMS_AND_CARBURE_MATCH), (DATA_SOURCE_IS_PRODUCER, DATA_SOURCE_IS_PRODUCER), (LOT_DECLARED, LOT_DECLARED), 
                    (ANOMALIES_CERTIFICATES, ANOMALIES_CERTIFICATES), (ANOMALIES_CONFIGURATION, ANOMALIES_CONFIGURATION))

    lot = models.ForeignKey(CarbureLot, blank=False, null=False, on_delete=models.CASCADE)
    max_score = models.FloatField(default=1)
    score = models.FloatField(default=1)
    item = models.CharField(max_length=32, choices=SCORE_ITEMS, blank=False, null=False, default='Unknown')
    meta = models.JSONField(blank=True, null=True, default=None)

    def __str__(self):
        return self.item

    class Meta:
        db_table = 'carbure_lots_scores'
        indexes = [models.Index(fields=['lot']),]
        verbose_name = 'CarbureLotReliabilityScore'
        verbose_name_plural = 'CarbureLotReliabilityScores'



class CarbureStockTransformation(models.Model):
    UNKNOWN = "UNKNOWN"
    ETH_ETBE = "ETH_ETBE"
    TRANSFORMATION_TYPES = ((UNKNOWN, UNKNOWN), (ETH_ETBE, ETH_ETBE), )
    transformation_type = models.CharField(max_length=32, choices=TRANSFORMATION_TYPES, null=False, blank=False, default=UNKNOWN)
    source_stock = models.ForeignKey('CarbureStock', null=False, blank=False, on_delete=models.CASCADE, related_name='source_stock')
    dest_stock = models.ForeignKey('CarbureStock', null=False, blank=False, on_delete=models.CASCADE, related_name='dest_stock')
    volume_deducted_from_source = models.FloatField(null=False, blank=False, default=0.0)
    volume_destination = models.FloatField(null=False, blank=False, default=0.0)
    metadata = models.JSONField() # ex: {‘volume_denaturant’: 1000, ‘volume_etbe_eligible’: 420000}
    transformed_by = models.ForeignKey(usermodel, null=True, blank=True, on_delete=models.SET_NULL)
    entity = models.ForeignKey(Entity, null=True, blank=True, on_delete=models.SET_NULL)
    transformation_dt = models.DateTimeField(auto_now_add=True)

    def get_weight(self):
        return self.volume_destination * self.source_stock.biofuel.masse_volumique

    def get_lhv_amount(self):
        return self.volume_destination * self.source_stock.biofuel.pci_litre

    class Meta:
        db_table = 'carbure_stock_transformations'
        indexes = [models.Index(fields=['entity']),]
        verbose_name = 'CarbureStockTransformation'
        verbose_name_plural = 'CarbureStockTransformation'

@receiver(pre_save, sender=CarbureLot)
def lot_pre_save_gen_carbure_id(sender, instance, *args, **kwargs):
    instance.generate_carbure_id()
    if instance.weight == 0:
        instance.weight = instance.get_weight()
    if instance.lhv_amount == 0:
        instance.lhv_amount = instance.get_lhv_amount()


@receiver(pre_delete, sender=CarbureStockTransformation, dispatch_uid='stock_transformation_delete_signal')
def delete_stock_transformation(sender, instance, using, **kwargs):
    # recredit volume to source stock
    instance.source_stock.remaining_volume = round(instance.source_stock.remaining_volume + instance.volume_deducted_from_source, 2)
    instance.source_stock.save()
    # delete dest_stock
    instance.dest_stock.parent_transformation = None
    instance.dest_stock.parent_lot = None # redundant
    # save event
    event = CarbureStockEvent()
    event.event_type = CarbureStockEvent.UNTRANSFORMED
    event.stock = instance.source_stock
    event.user = None
    event.metadata = {'message': 'delete stock transformation. recredit volume.', 'volume_to_credit': instance.volume_deducted_from_source}
    event.save()


@receiver(pre_delete, sender=CarbureLot, dispatch_uid='lot_delete_signal')
def delete_lot(sender, instance, using, **kwargs):
    # if we come from stock, recredit
    if instance.lot_status != CarbureLot.DELETED and instance.parent_stock: # if lot is already in status DELETED, we have already recredited the stock
        # this lot was a split from a stock
        instance.parent_stock.remaining_volume = round(instance.parent_stock.remaining_volume + instance.volume, 2)
        instance.parent_stock.remaining_weight = instance.parent_stock.get_weight()
        instance.parent_stock.remaining_lhv_amount = instance.parent_stock.get_lhv_amount()        
        instance.parent_stock.save()
        # save event
        event = CarbureStockEvent()
        event.event_type = CarbureStockEvent.UNSPLIT
        event.stock = instance.parent_stock
        event.user = None
        event.metadata = {'message': 'child lot deleted. recredit volume.', 'volume_to_credit': instance.volume}
        event.save()
    # if there is a parent_lot tagged as processing or trading, restore them to their "inbox" status
    if instance.parent_lot:
        if instance.parent_lot.delivery_type in [CarbureLot.PROCESSING, CarbureLot.TRADING]:
            instance.parent_lot.lot_status = CarbureLot.PENDING
            instance.parent_lot.delivery_type = CarbureLot.OTHER
            instance.parent_lot.save()
            # save event
            event = CarbureLotEvent()
            event.event_type = CarbureLotEvent.RECALLED
            event.lot = instance.parent_lot
            event.user = None
            event.metadata = {'message': 'child lot deleted. back to inbox.'}
            #event.save()

class CarbureStock(models.Model):
    parent_lot = models.ForeignKey(CarbureLot, null=True, blank=True, on_delete=models.CASCADE)
    parent_transformation = models.ForeignKey(CarbureStockTransformation, null=True, blank=True, on_delete=models.CASCADE)
    carbure_id = models.CharField(max_length=64, blank=False, null=False, default='')
    depot = models.ForeignKey(Depot, null=True, blank=True, on_delete=models.SET_NULL)
    carbure_client = models.ForeignKey(Entity, null=True, blank=True, on_delete=models.SET_NULL, related_name='stock_carbure_client')
    remaining_volume = models.FloatField(default=0.0)
    remaining_weight = models.FloatField(default=0.0)
    remaining_lhv_amount = models.FloatField(default=0.0)
    feedstock = models.ForeignKey(MatierePremiere, null=True, on_delete=models.SET_NULL)
    biofuel = models.ForeignKey(Biocarburant, null=True, on_delete=models.SET_NULL)
    country_of_origin = models.ForeignKey(Pays, null=True, on_delete=models.SET_NULL, related_name='stock_country_of_origin')
    carbure_production_site = models.ForeignKey(ProductionSite, null=True, blank=True, on_delete=models.SET_NULL)
    unknown_production_site = models.CharField(max_length=64, blank=True, null=True, default=None)
    production_country = models.ForeignKey(Pays, null=True, blank=True, on_delete=models.SET_NULL, related_name='stock_production_country')
    carbure_supplier = models.ForeignKey(Entity, null=True, blank=True, on_delete=models.SET_NULL, related_name='stock_carbure_supplier')
    unknown_supplier = models.CharField(max_length=64, blank=True, null=True, default=None)
    ghg_reduction = models.FloatField(default=0.0)
    ghg_reduction_red_ii = models.FloatField(default=0.0)

    class Meta:
        db_table = 'carbure_stock'
        indexes = [
            models.Index(fields=['carbure_client']),
            models.Index(fields=['carbure_client', 'depot']),
        ]
        verbose_name = 'CarbureStock'
        verbose_name_plural = 'CarbureStocks'

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

    def update_remaining_volume(self, volume_to_recredit, volume_to_debit):
        self.remaining_volume = round(self.remaining_volume + volume_to_recredit, 2)
        self.remaining_volume = round(self.remaining_volume - volume_to_debit, 2)
        self.remaining_lhv_amount = self.get_lhv_amount()
        self.remaining_weight = self.get_weight()
        self.save()

    def generate_carbure_id(self):
        country_of_production = '00'
        if self.production_country:
            country_of_production = self.production_country.code_pays
        delivery_site_id = '00'
        if self.depot:
            delivery_site_id = self.depot.depot_id
        period = '000000'
        parent_lot = self.get_parent_lot()
        if parent_lot:
            period = parent_lot.period
        self.carbure_id = 'S{period}-{country_of_production}-{delivery_site_id}-{id}'.format(period=period, country_of_production=country_of_production, delivery_site_id=delivery_site_id, id=self.id)

@receiver(pre_save, sender=CarbureStock)
def stock_pre_save_gen_carbure_id(sender, instance, *args, **kwargs):
    instance.generate_carbure_id()

class CarbureLotEvent(models.Model):
    CREATED = "CREATED"
    UPDATED = "UPDATED"
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
    RESTORED = "RESTORED"
    EVENT_TYPES = ((CREATED, CREATED), (UPDATED, UPDATED), (VALIDATED, VALIDATED), (FIX_REQUESTED, FIX_REQUESTED), (MARKED_AS_FIXED, MARKED_AS_FIXED),
                    (FIX_ACCEPTED, FIX_ACCEPTED), (ACCEPTED, ACCEPTED), (REJECTED, REJECTED), (RECALLED, RECALLED), (DECLARED, DECLARED), (DELETED, DELETED), (DECLCANCEL, DECLCANCEL),
                    (RESTORED, RESTORED),)
    event_type = models.CharField(max_length=32, null=False, blank=False, choices=EVENT_TYPES)
    event_dt = models.DateTimeField(auto_now_add=True, null=False, blank=False)
    lot = models.ForeignKey(CarbureLot, null=False, blank=False, on_delete=models.CASCADE)
    user = models.ForeignKey(usermodel, null=True, blank=True, on_delete=models.SET_NULL)
    metadata = models.JSONField(null=True, blank=True)

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
    COMMENT_TYPES = ((REGULAR, REGULAR), (AUDITOR, AUDITOR), (ADMIN, ADMIN))

    entity = models.ForeignKey(Entity, null=True, blank=True, on_delete=models.SET_NULL)
    user = models.ForeignKey(usermodel, null=True, blank=True, on_delete=models.SET_NULL)
    lot = models.ForeignKey(CarbureLot, on_delete=models.CASCADE)
    comment_type = models.CharField(max_length=16, choices=COMMENT_TYPES, default=REGULAR)
    comment_dt = models.DateTimeField(auto_now_add=True)
    comment = models.TextField()
    is_visible_by_admin = models.BooleanField(default=False) # AUDITOR comment must be explicitly shared with admin
    is_visible_by_auditor = models.BooleanField(default=False) # ADMIN comment must be explicitly shared with auditor

    class Meta:
        db_table = 'carbure_lots_comments'
        indexes = [
            models.Index(fields=['lot']),
        ]
        verbose_name = 'CarbureLotComment'
        verbose_name_plural = 'CarbureLotComments'

class CarbureStockEvent(models.Model):
    CREATED = "CREATED"
    UPDATED = "UPDATED"
    FLUSHED = "FLUSHED"
    SPLIT = "SPLIT"
    UNSPLIT = "UNSPLIT"
    TRANSFORMED = "TRANSFORMED"
    UNTRANSFORMED = "UNTRANSFORMED"
    EVENT_TYPES = ((CREATED, CREATED), (UPDATED, UPDATED), (SPLIT, SPLIT), (UNSPLIT, UNSPLIT),
                  (FLUSHED, FLUSHED), (TRANSFORMED, TRANSFORMED), (UNTRANSFORMED, UNTRANSFORMED))
    event_type = models.CharField(max_length=32, null=False, blank=False, choices=EVENT_TYPES)
    event_dt = models.DateTimeField(auto_now_add=True, null=False, blank=False)
    stock = models.ForeignKey(CarbureStock, null=False, blank=False, on_delete=models.CASCADE)
    user = models.ForeignKey(usermodel, null=True, blank=True, on_delete=models.SET_NULL)
    metadata = models.JSONField(null=True, blank=True)

    class Meta:
        db_table = 'carbure_stock_events'
        indexes = [
            models.Index(fields=['stock']),
        ]
        verbose_name = 'CarbureStockEvent'
        verbose_name_plural = 'CarbureStockEvents'

class GenericCertificate(models.Model):
    SYSTEME_NATIONAL = "SYSTEME_NATIONAL"
    ISCC = "ISCC"
    REDCERT = "REDCERT"
    DBS = "2BS"
    CERTIFICATE_TYPES = ((SYSTEME_NATIONAL, SYSTEME_NATIONAL), (ISCC, ISCC), (REDCERT, REDCERT), (DBS, DBS))

    certificate_id = models.CharField(max_length=64, blank=False, null=False)
    certificate_type = models.CharField(max_length=32, null=False, blank=False, choices=CERTIFICATE_TYPES)
    certificate_holder = models.CharField(max_length=512, null=False, blank=False)
    certificate_issuer = models.CharField(max_length=256, null=True, blank=True)
    address = models.CharField(max_length=512, null=True, blank=True)
    valid_from = models.DateField(null=False, blank=False)
    valid_until = models.DateField(null=False, blank=False)
    download_link = models.CharField(max_length=512, default=None, null=True)
    scope = models.JSONField(null=True)
    input = models.JSONField(null=True)
    output = models.JSONField(null=True)

    class Meta:
        db_table = 'carbure_certificates'
        indexes = [
            models.Index(fields=['certificate_type']),
        ]
        verbose_name = 'CarbureCertificates'
        verbose_name_plural = 'CarbureCertificates'

class EntityCertificate(models.Model):
    certificate = models.ForeignKey(GenericCertificate, blank=False, null=False, on_delete=models.CASCADE)
    entity = models.ForeignKey(Entity, blank=False, null=False, on_delete=models.CASCADE)
    has_been_updated = models.BooleanField(default=False)
    checked_by_admin = models.BooleanField(default=False)
    rejected_by_admin = models.BooleanField(default=False)
    added_dt = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '%s - %s' % (self.entity.name, self.certificate.certificate_id)

    class Meta:
        db_table = 'carbure_entity_certificates'
        indexes = [
            models.Index(fields=['entity']),
        ]
        verbose_name = 'CarbureEntityCertificates'
        verbose_name_plural = 'CarbureEntityCertificates'


class CarbureNotification(models.Model):
    CORRECTION_REQUEST = "CORRECTION_REQUEST"
    CORRECTION_DONE = "CORRECTION_DONE"
    LOTS_REJECTED = "LOTS_REJECTED"
    LOTS_RECEIVED = "LOTS_RECEIVED"
    LOTS_RECALLED = "LOTS_RECALLED"
    CERTIFICATE_EXPIRED = "CERTIFICATE_EXPIRED"
    DECLARATION_VALIDATED = "DECLARATION_VALIDATED"
    DECLARATION_CANCELLED = "DECLARATION_CANCELLED"

    NOTIFICATION_TYPES = [(CORRECTION_REQUEST, CORRECTION_REQUEST), (CORRECTION_DONE, CORRECTION_DONE), (LOTS_REJECTED, LOTS_REJECTED), (LOTS_RECEIVED, LOTS_RECEIVED), (LOTS_RECALLED, LOTS_RECALLED), (CERTIFICATE_EXPIRED, CERTIFICATE_EXPIRED), (DECLARATION_VALIDATED, DECLARATION_VALIDATED), (DECLARATION_CANCELLED, DECLARATION_CANCELLED)]

    dest = models.ForeignKey(Entity, blank=False, null=False, on_delete=models.CASCADE)
    datetime = models.DateTimeField(null=False, blank=False, auto_now_add=True)
    type = models.CharField(max_length=32, null=False, blank=False, choices=NOTIFICATION_TYPES)
    acked = models.BooleanField(default=False)
    send_by_email = models.BooleanField(default=False)
    notify_administrator = models.BooleanField(default=False)
    email_sent = models.BooleanField(default=False)
    meta = models.JSONField(blank=True, null=True)

    class Meta:
        db_table = 'carbure_notifications'
        indexes = [
            models.Index(fields=['dest_id']),
        ]
        verbose_name = 'CarbureNotification'
        verbose_name_plural = 'CarbureNotifications'
