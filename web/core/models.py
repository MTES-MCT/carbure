import datetime
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.auth import get_user_model


usermodel = get_user_model()


class Entity(models.Model):
    PRODUCER = 'Producteur'
    OPERATOR = 'Opérateur'
    TRADER = 'Trader'
    ADMIN = 'Administration'
    AUDITOR = 'Auditor'
    ENTITY_TYPES = ((PRODUCER, 'Producteur'), (OPERATOR, 'Opérateur'),
                    (ADMIN, 'Administration'), (TRADER, 'Trader'),
                    (AUDITOR, 'Auditeur'), ('Unknown', 'Unknown'))

    name = models.CharField(max_length=64, unique=True)
    date_added = models.DateTimeField(auto_now_add=True)
    entity_type = models.CharField(max_length=64, choices=ENTITY_TYPES, default='Unknown')
    parent_entity = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE)

    has_mac = models.BooleanField(default=False)
    has_trading = models.BooleanField(default=False)

    legal_name = models.CharField(max_length=128, blank=True, default='')
    registration_id = models.CharField(max_length=64, blank=True, default='')
    sustainability_officer_phone_number = models.CharField(max_length=32, blank=True, default='')
    sustainability_officer = models.CharField(max_length=256, blank=True, default='')
    registered_address = models.TextField(blank=True, default='')
    hash = models.CharField(max_length=32, null=True, blank=True, default='')
    default_certificate = models.CharField(max_length=64, null=True, blank=True, default='')

    def __str__(self):
        return self.name

    def natural_key(self):
        return {'name': self.name, 'id': self.id, 'entity_type': self.entity_type, 'has_mac': self.has_mac, 'has_trading': self.has_trading,
            'legal_name': self.legal_name, 'registration_id': self.registration_id,
            'sustainability_officer': self.sustainability_officer, 'sustainability_officer_phone_number': self.sustainability_officer_phone_number,
            'registered_address': self.registered_address, 'default_certificate': self.default_certificate}

    def url_friendly_name(self):
        return self.name.replace(' ', '').upper()

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
    description = models.CharField(max_length=128)
    date_added = models.DateField(default=timezone.now)
    code = models.CharField(max_length=64, unique=True)
    compatible_alcool = models.BooleanField(default=False)
    compatible_graisse = models.BooleanField(default=False)
    is_double_compte = models.BooleanField(default=False)
    is_huile_vegetale = models.BooleanField(default=False)
    is_displayed = models.BooleanField(default=True)
    category = models.CharField(max_length=32, choices=MP_CATEGORIES, default='CONV')


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


from producers.models import ProductionSite

# deprecated. Use LotV2
class Lot(models.Model):
    carbure_id = models.CharField(max_length=64, blank=True, default='')
    class Meta:
        db_table = 'lots'


class LotV2(models.Model):
    DRAFT = 'Draft'
    VALIDATED = 'Validated'

    LOT_STATUS = ((DRAFT, 'Brouillon'), (VALIDATED, 'Validé'))
    SOURCE_CHOICES = (('EXCEL', 'Excel'), ('MANUAL', 'Manual'))

    period = models.CharField(max_length=64, blank=True, default='')
    carbure_id = models.CharField(max_length=64, blank=True, default='')
    # producer
    producer_is_in_carbure = models.BooleanField(default=True)
    carbure_producer = models.ForeignKey(Entity, null=True, blank=True, on_delete=models.SET_NULL, related_name='producer_lotv2')
    unknown_producer = models.CharField(max_length=64, blank=True, null=True, default='')

    production_site_is_in_carbure = models.BooleanField(default=True)
    carbure_production_site = models.ForeignKey(ProductionSite, null=True, blank=True, on_delete=models.SET_NULL)
    carbure_production_site_reference = models.CharField(max_length=64, blank=True, null=True, default='')
    unknown_production_site = models.CharField(max_length=64, blank=True, null=True, default='')
    unknown_production_country = models.ForeignKey(Pays, null=True, blank=True, on_delete=models.SET_NULL, related_name='unknown_production_site_country')
    unknown_production_site_com_date = models.DateField(blank=True, null=True)
    unknown_production_site_reference = models.CharField(max_length=64, blank=True, null=True, default='')
    unknown_production_site_dbl_counting = models.CharField(max_length=64, blank=True, null=True, default='')

    unknown_supplier = models.CharField(max_length=64, blank=True, null=True, default='')
    unknown_supplier_certificate = models.CharField(max_length=64, blank=True, null=True, default='')

    # lot details
    volume = models.FloatField(default=0.0)
    remaining_volume = models.FloatField(default=0.0)
    matiere_premiere = models.ForeignKey(MatierePremiere, null=True, on_delete=models.SET_NULL)
    biocarburant = models.ForeignKey(Biocarburant, null=True, on_delete=models.SET_NULL)
    pays_origine = models.ForeignKey(Pays, null=True, on_delete=models.SET_NULL)

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

    # other
    status = models.CharField(max_length=64, choices=LOT_STATUS, default='Draft')
    source = models.CharField(max_length=32, choices=SOURCE_CHOICES, default='Manual')
    added_by = models.ForeignKey(Entity, null=True, blank=True, on_delete=models.SET_NULL)
    added_by_user = models.ForeignKey(usermodel, null=True, blank=True, on_delete=models.SET_NULL)
    added_time = models.DateTimeField(auto_now_add=True)

    # lot has been split into many sublots ?
    parent_lot = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE)
    is_split = models.BooleanField(default=False)

    # lot has been fused
    is_fused = models.BooleanField(default=False)
    fused_with = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='lotv2_fused_with')

    # lot has been transformed (ETBE)
    is_transformed = models.BooleanField(default=False)
    # when True, parent_lot will be set

    # entity responsible for the original data
    data_origin_entity = models.ForeignKey(Entity, null=True, blank=True, on_delete=models.SET_NULL, related_name='data_origin_entity')

    # sanity checks
    blocking_sanity_checked_passed = models.BooleanField(default=False)
    nonblocking_sanity_checked_passed = models.BooleanField(default=False)

    is_valid = models.BooleanField(default=False)


    def natural_key(self):
        return {'id': self.id, 'period': self.period, 'carbure_id': self.carbure_id, 'producer_is_in_carbure': self.producer_is_in_carbure, 'carbure_producer': self.carbure_producer.natural_key() if self.carbure_producer else None,
        'unknown_producer': self.unknown_producer, 'production_site_is_in_carbure': self.production_site_is_in_carbure, 'carbure_production_site': self.carbure_production_site.natural_key() if self.carbure_production_site else None,
        'unknown_production_site': self.unknown_production_site, 'unknown_production_country': self.unknown_production_country.natural_key() if self.unknown_production_country else None,
        'unknown_production_site_com_date': self.unknown_production_site_com_date, 'unknown_production_site_reference': self.unknown_production_site_reference,
        'unknown_production_site_dbl_counting': self.unknown_production_site_dbl_counting, 'volume': round(self.volume, 2), 'remaining_volume': round(self.remaining_volume, 2), 'matiere_premiere': self.matiere_premiere.natural_key() if self.matiere_premiere else None,
        'biocarburant': self.biocarburant.natural_key() if self.biocarburant else None, 'pays_origine': self.pays_origine.natural_key() if self.pays_origine else None,
        'eec': self.eec, 'el': self.el, 'ep': self.ep, 'etd': self.etd, 'eu': self.eu, 'esca': self.esca, 'eccs': self.eccs, 'eccr': self.eccr, 'eee': self.eee,
        'ghg_total': self.ghg_total, 'ghg_reference': self.ghg_reference, 'ghg_reduction': self.ghg_reduction, 'status': self.status, 'source': self.source,
        'parent_lot': self.parent_lot.natural_key() if self.parent_lot else None, 'is_split': self.is_split, 'is_fused': self.is_fused, 'fused_with': self.fused_with.natural_key() if self.fused_with else None,
        'data_origin_entity': self.data_origin_entity.natural_key() if self.data_origin_entity else None, 'added_by': self.added_by.natural_key() if self.added_by else None, 'is_transformed': self.is_transformed,
        'unknown_supplier': self.unknown_supplier, 'unknown_supplier_certificate': self.unknown_supplier_certificate, 'carbure_production_site_reference': self.carbure_production_site_reference}

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'lots_v2'
        verbose_name = 'LotV2'
        verbose_name_plural = 'LotsV2'
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["added_by"]),
            models.Index(fields=["period"]),
            models.Index(fields=["biocarburant"]),
            models.Index(fields=["matiere_premiere"]),
            models.Index(fields=["pays_origine"]),
            models.Index(fields=["carbure_production_site"]),
            models.Index(fields=["unknown_production_site"]),
        ]

class LotTransaction(models.Model):
    PENDING = 'N'
    ACCEPTED = 'A'
    REJECTED = 'R'
    TOFIX = 'AC'
    FIXED = 'AA'
    FROZEN = 'F'

    DELIVERY_STATUS = ((PENDING, 'En Attente'), (ACCEPTED, 'Accepté'), (REJECTED, 'Refusé'), (TOFIX, 'À corriger'), (FIXED, 'Corrigé'), (FROZEN, 'Déclaré'))
    lot = models.ForeignKey(LotV2, null=False, blank=False, on_delete=models.CASCADE, related_name='tx_lot')

    # vendor / producer
    carbure_vendor = models.ForeignKey(Entity, null=True, blank=True, on_delete=models.SET_NULL, related_name='vendor_transaction')
    carbure_vendor_certificate = models.CharField(max_length=64, blank=True, null=True, default='')

    # client / delivery
    dae = models.CharField(max_length=128, blank=True, default='')
    client_is_in_carbure = models.BooleanField(default=True)
    carbure_client = models.ForeignKey(Entity, null=True, blank=True, on_delete=models.SET_NULL, related_name='client_transaction')
    unknown_client = models.CharField(max_length=64, blank=True, default='')
    delivery_date = models.DateField(blank=True, null=True)
    delivery_site_is_in_carbure = models.BooleanField(default=True)
    carbure_delivery_site = models.ForeignKey(Depot, null=True, blank=True, on_delete=models.SET_NULL)
    unknown_delivery_site = models.CharField(max_length=64, blank=True, default='')
    unknown_delivery_site_country = models.ForeignKey(Pays, null=True, blank=True, on_delete=models.SET_NULL, related_name='unknown_delivery_site_country')
    delivery_status = models.CharField(max_length=64, choices=DELIVERY_STATUS, default='N')

    # ghg impact
    etd_impact = models.FloatField(default=0.0)
    ghg_total = models.FloatField(default=0.0)
    ghg_reduction = models.FloatField(default=0.0)

    # other
    champ_libre = models.TextField(blank=True, null=True, default='')
    # mise a consommation?
    is_mac = models.BooleanField(default=False)
    # this PoS is part of a multiple PoS batch
    is_batch = models.BooleanField(default=False)
    # transaction generated by carbure stock-optimisation
    generated_by_carbure = models.BooleanField(default=False)
    # this PoS has been forwarded by an Operator to another Operator (outsourced blending)
    # or this PoS has been forwarded by a Trader to a client (trading without storage, the trader is only an intermediary)
    is_forwarded = models.BooleanField(default=False)
    parent_tx = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE)

    # this PoS has been received by a producer with trading or a trader
    # this flag will make it easier to find "stock" lots
    is_stock = models.BooleanField(default=False)


    # admin / auditor checks & filters
    hidden_by_admin = models.BooleanField(default=False)
    hidden_by_auditor = models.BooleanField(default=False)
    highlighted_by_admin = models.BooleanField(default=False)
    highlighted_by_auditor = models.BooleanField(default=False)

    
    def __str__(self):
        return str(self.id)

    def natural_key(self, admin=False):
        d = {'lot': self.lot.natural_key(), 'carbure_vendor': self.carbure_vendor.natural_key() if self.carbure_vendor else None, 'carbure_vendor_certificate': self.carbure_vendor_certificate,
        'dae': self.dae, 'client_is_in_carbure': self.client_is_in_carbure, 'carbure_client': self.carbure_client.natural_key() if self.carbure_client else None,
        'unknown_client': self.unknown_client, 'delivery_date': self.delivery_date, 'delivery_site_is_in_carbure': self.delivery_site_is_in_carbure,
        'carbure_delivery_site': self.carbure_delivery_site.natural_key() if self.carbure_delivery_site else None, 'unknown_delivery_site': self.unknown_delivery_site,
        'unknown_delivery_site_country': self.unknown_delivery_site_country.natural_key() if self.unknown_delivery_site_country else None, 'delivery_status': self.delivery_status,
        'champ_libre': self.champ_libre, 'is_mac': self.is_mac, 'is_batch': self.is_batch,
        'id': self.id, 'is_forwarded': self.is_forwarded}
        if admin:
            d['hidden_by_admin'] = self.hidden_by_admin
            d['highlighted_by_admin'] = self.highlighted_by_admin
            d['hidden_by_auditor'] = self.hidden_by_auditor
            d['highlighted_by_auditor'] = self.highlighted_by_auditor
        return d

    class Meta:
        db_table = 'transactions'
        verbose_name = 'Transaction'
        verbose_name_plural = 'Transactions'
        indexes = [
            models.Index(fields=["carbure_vendor"]),
            models.Index(fields=["carbure_client"]),
            models.Index(fields=["delivery_status"]),
            models.Index(fields=["unknown_client"]),
            models.Index(fields=["is_forwarded"]),
            models.Index(fields=["is_mac"]),
            models.Index(fields=["carbure_delivery_site"]),
            models.Index(fields=["unknown_delivery_site"]),
            
        ]


class TransactionComment(models.Model):
    COMMENT_TOPIC = (('SUSTAINABILITY', 'Durabilité'), ('TX', 'Transaction'), ('BOTH', 'Les deux'))
    entity = models.ForeignKey(Entity, null=True, blank=True, on_delete=models.SET_NULL)
    topic = models.CharField(max_length=24, choices=COMMENT_TOPIC, default='BOTH')
    tx = models.ForeignKey(LotTransaction, on_delete=models.CASCADE)
    comment = models.TextField()

    def __str__(self):
        return str(self.comment)

    def natural_key(self):
        return {'entity': self.entity.natural_key(), 'topic':self.topic, 'comment':self.comment}

    class Meta:
        db_table = 'tx_comments'
        verbose_name = 'TransactionComment'
        verbose_name_plural = 'TransactionComments'


class Control(models.Model):
    STATUS = [("OPEN", "Ouvert"), ("CLOSED", "Clôturé")]

    tx = models.ForeignKey(LotTransaction, on_delete=models.CASCADE)
    status = models.CharField(max_length=32, choices=STATUS, default="OPEN")
    opened_at = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)

    def natural_key(self):
        return {'tx': self.tx.natural_key(), 'status': self.status, 'opened_at': self.opened_at, 'last_update': self.last_update}

    class Meta:
        db_table = 'controls'
        verbose_name = 'Contrôle Lot'
        verbose_name_plural = 'Contrôles Lots'


class ControlFiles(models.Model):
    control = models.ForeignKey(Control, on_delete=models.CASCADE)
    date_added = models.DateField(auto_now_add=True)
    file = models.FileField(null=True, blank=True)

    class Meta:
        db_table = 'control_files'
        verbose_name = 'Contrôle - Justificatif'
        verbose_name_plural = 'Contrôles - Justificatifs'


class ControlMessages(models.Model):
    control = models.ForeignKey(Control, on_delete=models.CASCADE)
    entity = models.ForeignKey(Entity, on_delete=models.SET_NULL, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    message = models.TextField(blank=False, null=False)
    dt_added = models.DateTimeField(auto_now_add=True)

    def natural_key(self):
        return {'entity': self.entity.natural_key(), 'message': self.message, 'dt_addded': self.dt_added}

    class Meta:
        db_table = 'control_messages'
        verbose_name = 'Contrôle - Message'
        verbose_name_plural = 'Contrôles - Messages'


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


class ETBETransformation(models.Model):
    previous_stock = models.ForeignKey(LotTransaction, null=False, blank=False, on_delete=models.CASCADE, related_name='previous_stock')
    new_stock = models.ForeignKey(LotTransaction, null=False, blank=False, on_delete=models.CASCADE, related_name='new_stock')

    volume_ethanol = models.FloatField(null=False, blank=False, default=0.0)
    volume_etbe = models.FloatField(null=False, blank=False, default=0.0)
    volume_etbe_eligible = models.FloatField(null=False, blank=False, default=0.0)
    volume_denaturant = models.FloatField(null=False, blank=False, default=0.0)

    added_by = models.ForeignKey(Entity, null=True, blank=True, on_delete=models.SET_NULL)
    added_by_user = models.ForeignKey(usermodel, null=True, blank=True, on_delete=models.SET_NULL)
    added_time = models.DateTimeField(auto_now_add=True)


    def natural_key(self):
        return {'previous': self.previous_stock.natural_key(), 'new': self.new_stock.natural_key(), 'volume_ethanol': self.volume_ethanol, 'volume_etbe': self.volume_etbe, 'volume_denaturant': self.volume_denaturant, 'volume_etbe_eligible': self.volume_etbe_eligible,
                'added_by': self.added_by.natural_key(), 'added_by_user': self.added_by_user.natural_key(), 'added_time': self.added_time}

    class Meta:
        db_table = 'etbe_transformations'
        verbose_name = 'Transformation ETBE'
        verbose_name_plural = 'Transformations ETBE'


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

    tx = models.ForeignKey(LotTransaction, null=False, blank=False, on_delete=models.CASCADE)

    field = models.CharField(max_length=64, null=True, blank=True)
    fields = models.JSONField(null=True, blank=True)
    value = models.CharField(max_length=128, null=True, blank=True)
    extra = models.CharField(max_length=256, null=True, blank=True)

    def natural_key(self):
        return {'error': self.error,
                'display_to_creator': self.display_to_creator, 'display_to_recipient': self.display_to_recipient,
                'display_to_admin': self.display_to_admin, 'display_to_auditor': self.display_to_auditor,
                'acked_by_creator': self.acked_by_creator, 'acked_by_recipient': self.acked_by_recipient,
                'acked_by_admin': self.acked_by_admin, 'acked_by_auditor': self.acked_by_auditor,
                'highlighted_by_admin': self.highlighted_by_admin, 'highlighted_by_auditor': self.highlighted_by_auditor,
                'is_blocking': self.is_blocking, 'tx_id': self.tx_id, 'field': self.field, 'fields': self.fields,
                'value': self.value, 'extra': self.extra}

    class Meta:
        db_table = 'generic_errors'
        verbose_name = 'Generic Error'
        verbose_name_plural = 'Generic Errors'


class TransactionUpdateHistory(models.Model):
    ADD = "ADD"
    REMOVE = "REMOVE"
    UPDATE = "UPDATE"

    TX_HISTORY_TYPES = ((ADD, ADD), (REMOVE, REMOVE), (UPDATE, UPDATE))

    tx = models.ForeignKey(LotTransaction, null=False, blank=False, on_delete=models.CASCADE)
    datetime = models.DateTimeField(auto_now_add=True)
    update_type = models.CharField(max_length=32, null=False, blank=False, choices=TX_HISTORY_TYPES, default=ADD)
    field = models.CharField(max_length=64, null=False, blank=False)
    value_before = models.TextField(null=True)
    value_after = models.TextField(null=True)
    modified_by = models.ForeignKey(usermodel, null=True, blank=True, on_delete=models.SET_NULL)
    modified_by_entity = models.ForeignKey(Entity, null=True, blank=True, on_delete=models.SET_NULL)

    def natural_key(self):
        return {'tx_id': self.tx.id, 'update_type': self.update_type,  'datetime': self.datetime, 'field': self.field, 'value_before': self.value_before, 'value_after': self.value_after,
        'modified_by': self.modified_by.email if self.modified_by else '', 'entity': self.modified_by_entity.name if self.modified_by_entity else ''}

    class Meta:
        db_table = 'transactions_updates'
        verbose_name = 'Transaction Update'
        verbose_name_plural = 'Transaction Updates'


class EmailNotification(models.Model):
    CORRECTION_REQUEST = "CORRECTION_REQUEST"
    CORRECTION_DONE = "CORRECTION_DONE"
    LOT_CHANGED = "LOT_CHANGED"
    LOT_REJECTED = "LOT_REJECTED"
    LOT_PENDING = "LOT_PENDING"
    DEADLINE_APPROACHING = "DEADLINE_APPROACHING"
    DOCUMENTATION_REQUESTED = "DOCUMENTATION_REQUESTED"
    NOTIFICATION_TYPE = ((CORRECTION_REQUEST, CORRECTION_REQUEST), (CORRECTION_DONE, CORRECTION_DONE), (LOT_CHANGED, LOT_CHANGED), 
                         (LOT_REJECTED, LOT_REJECTED), (LOT_PENDING, LOT_PENDING), (DEADLINE_APPROACHING, DEADLINE_APPROACHING),
                         (DOCUMENTATION_REQUESTED, DOCUMENTATION_REQUESTED))

    datetime = models.DateTimeField(auto_now_add=True)
    linked_tx = models.ForeignKey(LotTransaction, null=True, blank=True, on_delete=models.CASCADE)
    notif_type = models.CharField(max_length=32, null=False, blank=False, choices=NOTIFICATION_TYPE, default="")
    entity = models.ForeignKey(Entity, null=True, blank=True, on_delete=models.CASCADE)
    sent = models.BooleanField(default=False)

    class Meta:
        db_table = 'email_notifications'
        verbose_name = 'Email Notification'
        verbose_name_plural = 'Email Notifications'
