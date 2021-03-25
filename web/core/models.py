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
    ENTITY_TYPES = ((PRODUCER, 'Producteur'), (OPERATOR, 'Opérateur'),
                    (ADMIN, 'Administration'), (TRADER, 'Trader'), ('Unknown', 'Unknown'))

    name = models.CharField(max_length=64, unique=True)
    date_added = models.DateTimeField(auto_now_add=True)
    entity_type = models.CharField(max_length=64, choices=ENTITY_TYPES, default='Unknown')
    parent_entity = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE)

    trading_certificate = models.FileField(null=True, blank=True)
    has_mac = models.BooleanField(default=False)
    has_trading = models.BooleanField(default=False)
    national_system_certificate = models.CharField(max_length=64, null=True, blank=True)

    legal_name = models.CharField(max_length=128, blank=True, default='')
    registration_id = models.CharField(max_length=64, blank=True, default='')
    sustainability_officer_phone_number = models.CharField(max_length=32, blank=True, default='')
    sustainability_officer = models.CharField(max_length=32, blank=True, default='')
    registered_address = models.TextField(blank=True, default='')

    def __str__(self):
        return self.name

    def natural_key(self):
        return {'name': self.name, 'id': self.id, 'entity_type': self.entity_type, 'has_mac': self.has_mac, 'has_trading': self.has_trading,
            'national_system_certificate': self.national_system_certificate, 'legal_name': self.legal_name, 'registration_id': self.registration_id,
            'sustainability_officer': self.sustainability_officer, 'sustainability_officer_phone_number': self.sustainability_officer_phone_number,
            'registered_address': self.registered_address}

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
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '%s - %s' % (self.user.email, self.entity.name)

    def natural_key(self):
        return {'name': self.user.name, 'email': self.user.email, 'entity': self.entity.name, 'entity_type': self.entity.entity_type}

    class Meta:
        db_table = 'users_rights'
        verbose_name = 'User Right'
        verbose_name_plural = 'Users Rights'


class UserRightsRequests(models.Model):
    STATUS_TYPES = (('PENDING', 'En attente de validation'), ('ACCEPTED', 'Accepté'), ('REJECTED', 'Refusé'), ('REVOKED', 'Révoqué'))

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE)
    date_requested = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=32, choices=STATUS_TYPES, default='PENDING')
    comment = models.TextField(blank=True, null=True)

    def natural_key(self):
        return {'id': self.id, 'user': self.user.natural_key(), 'entity': self.entity.natural_key(), 
                'date_requested': self.date_requested, 'status': self.status, 'comment': self.comment}

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
    MP_CATEGORIES = (('CONV', 'Conventionnel'), ('ANN-IX-A', 'ANNEXE IX-A'), ('ANN-IX-B', 'ANNEXE IX-B'), ('OTHER', 'Autre'))

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
        return {'code': self.code, 'name': self.name, 'is_double_compte': self.is_double_compte}

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
        'unknown_production_site_dbl_counting': self.unknown_production_site_dbl_counting, 'volume': self.volume, 'matiere_premiere': self.matiere_premiere.natural_key() if self.matiere_premiere else None,
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
        ]


class LotTransaction(models.Model):
    DELIVERY_STATUS = (('N', 'En Attente'), ('A', 'Accepté'), ('R', 'Refusé'), ('AC', 'À corriger'), ('AA', 'Corrigé'))
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
    champ_libre = models.CharField(max_length=128, blank=True, null=True, default='')
    # mise a consommation?
    is_mac = models.BooleanField(default=False)
    # this PoS is part of a multiple PoS batch
    is_batch = models.BooleanField(default=False)
    # this PoS has been forwarded by an Operator to another Operator (outsourced blending)
    is_forwarded = models.BooleanField(default=False)

    def __str__(self):
        return str(self.id)

    def natural_key(self):
        return {'lot': self.lot.natural_key(), 'carbure_vendor': self.carbure_vendor.natural_key() if self.carbure_vendor else None, 'carbure_vendor_certificate': self.carbure_vendor_certificate,
        'dae': self.dae, 'client_is_in_carbure': self.client_is_in_carbure, 'carbure_client': self.carbure_client.natural_key() if self.carbure_client else None,
        'unknown_client': self.unknown_client, 'delivery_date': self.delivery_date, 'delivery_site_is_in_carbure': self.delivery_site_is_in_carbure,
        'carbure_delivery_site': self.carbure_delivery_site.natural_key() if self.carbure_delivery_site else None, 'unknown_delivery_site': self.unknown_delivery_site,
        'unknown_delivery_site_country': self.unknown_delivery_site_country.natural_key() if self.unknown_delivery_site_country else None, 'delivery_status': self.delivery_status,
        'champ_libre': self.champ_libre, 'is_mac': self.is_mac, 'is_batch': self.is_batch,
        'id': self.id, 'is_forwarded': self.is_forwarded}

    class Meta:
        db_table = 'transactions'
        verbose_name = 'Transaction'
        verbose_name_plural = 'Transactions'
        indexes = [
            models.Index(fields=["carbure_vendor"]),
            models.Index(fields=["carbure_client"]),
        ]


class LotV2Error(models.Model):
    lot = models.ForeignKey(LotV2, null=False, blank=False, on_delete=models.CASCADE)
    field = models.CharField(max_length=64, null=False, blank=False)
    value = models.CharField(max_length=128, null=True, blank=True)
    error = models.CharField(max_length=256, null=False, blank=False)

    def __str__(self):
        return self.error

    def natural_key(self):
        return {'lot_id': self.lot.id, 'field': self.field, 'value': self.value, 'error': self.error}

    class Meta:
        db_table = 'lotsv2_errors'
        verbose_name = 'LotV2Error'
        verbose_name_plural = 'LotV2Errors'


class TransactionError(models.Model):
    tx = models.ForeignKey(LotTransaction, null=False, blank=False, on_delete=models.CASCADE)
    field = models.CharField(max_length=64, null=False, blank=False)
    value = models.CharField(max_length=128, null=True, blank=True)
    error = models.CharField(max_length=256, null=False, blank=False)

    def __str__(self):
        return self.error

    def natural_key(self):
        return {'tx_id': self.tx.id, 'field': self.field, 'value': self.value, 'error': self.error}

    class Meta:
        db_table = 'tx_errors'
        verbose_name = 'TransactionError'
        verbose_name_plural = 'TransactionsErrors'


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


class GHGValues(models.Model):
    matiere_premiere = models.ForeignKey(MatierePremiere, blank=True, null=True, on_delete=models.CASCADE)
    biocarburant = models.ForeignKey(Biocarburant, on_delete=models.CASCADE)
    condition = models.CharField(max_length=256, null=True, blank=True)
    eec_default = models.FloatField(default=0.0)
    eec_typical = models.FloatField(default=0.0)
    ep_default = models.FloatField(default=0.0)
    ep_typical = models.FloatField(default=0.0)
    etd_default = models.FloatField(default=0.0)
    etd_typical = models.FloatField(default=0.0)

    def __str__(self):
        return '%s - %s - %f -  %f - %f' % (self.biocarburant, self.matiere_premiere,
                                            self.eec_default, self.ep_default, self.etd_default)

    class Meta:
        db_table = 'ghg_values'
        verbose_name = 'Valeur GES de référence'
        verbose_name_plural = 'Valeurs GES de référence'


# deprecated, to delete
class CheckRule(models.Model):
    CONDITIONS = (('EQ', 'Equals'), ('GT', 'Greater Than'), ('GTE', 'Greater Than or Equal'), ('LT', 'Less Than'), ('LTE', 'Less Than or Equal'), ('DIFF', 'Is Different than'), ('IN', 'Is In'), ('NIN', 'Is Not In'))

    condition_col = models.CharField(max_length=32, null=True, blank=True)
    condition = models.CharField(max_length=64, choices=CONDITIONS, default='EQ')
    condition_value = models.CharField(max_length=256, null=True, blank=True)

    check_col = models.CharField(max_length=32, null=True, blank=True)
    check = models.CharField(max_length=64, choices=CONDITIONS, default='EQ')
    check_value = models.CharField(max_length=256, null=True, blank=True)

    warning_to_user = models.BooleanField(default=False)
    warning_to_admin = models.BooleanField(default=False)
    block_validation = models.BooleanField(default=False)
    message = models.CharField(max_length=256, blank=True, null=True, default='')

    def __str__(self):
        return self.message

    class Meta:
        db_table = 'check_rules'
        verbose_name = 'Règle Métier'
        verbose_name_plural = 'Règles Métier'


class LotValidationError(models.Model):
    lot = models.ForeignKey(LotV2, null=False, blank=False, on_delete=models.CASCADE)
    tx = models.ForeignKey(LotTransaction, null=True, on_delete=models.SET_NULL)
    rule_triggered = models.CharField(max_length=64, blank=True, null=True, default='')

    warning_to_user = models.BooleanField(default=False)
    warning_to_recipient = models.BooleanField(default=False)
    warning_to_admin = models.BooleanField(default=False)
    block_validation = models.BooleanField(default=False)
    message = models.TextField(blank=True, null=True, default='')
    details = models.TextField(blank=True, null=True, default='')

    acked_by_admin = models.BooleanField(default=False)
    highlighted_by_admin = models.BooleanField(default=False)

    def __str__(self):
        return self.rule_triggered

    def natural_key(self):
        return {'lot_id': self.lot.id, 'error': self.message, 'details': self.details, 'is_blocking': self.block_validation, 'is_warning': self.warning_to_user, 'acked_by_admin': self.acked_by_admin, 'highlighted_by_admin': self.highlighted_by_admin}

    class Meta:
        db_table = 'validation_errors'
        verbose_name = 'LotValidationError'
        verbose_name_plural = 'LotValidationErrors'


class ISCCScope(models.Model):
    scope = models.CharField(max_length=8, null=False, blank=False)
    description = models.CharField(max_length=256, null=False, blank=False)

    def __str__(self):
        return self.scope

    class Meta:
        db_table = 'iscc_scopes'
        verbose_name = 'ISCC Scope'
        verbose_name_plural = 'ISCC Scopes'


class ISCCCertificate(models.Model):
    certificate_id = models.CharField(max_length=64, null=False, blank=False)
    # warning, this column must be manually altered in db to support utf8mb4
    # command: ALTER TABLE iscc_certificates CHANGE certificate_holder certificate_holder VARCHAR(512) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
    # do not change anything
    certificate_holder = models.CharField(max_length=256, null=False, blank=False)
    addons = models.CharField(max_length=256, null=False, blank=False)
    valid_from = models.DateField(null=False)
    valid_until = models.DateField(null=False)
    issuing_cb = models.CharField(max_length=256, default='')
    location = models.CharField(max_length=256, default='')
    download_link = models.CharField(max_length=512, default='')

    def natural_key(self):
        scope = [s.scope.scope for s in self.iscccertificatescope_set.all()]

        return {'certificate_id': self.certificate_id,
                'certificate_holder': self.certificate_holder,
                'location': self.location,
                'valid_from': self.valid_from,
                'valid_until': self.valid_until,
                'issuing_cb': self.issuing_cb,
                'download_link': self.download_link,
                'scope': scope}

    def __str__(self):
        return self.certificate_id

    class Meta:
        db_table = 'iscc_certificates'
        verbose_name = 'ISCC Certificate'
        verbose_name_plural = 'ISCC Certificates'


class ISCCCertificateRawMaterial(models.Model):
    certificate = models.ForeignKey(ISCCCertificate, blank=False, null=False, on_delete=models.CASCADE)
    raw_material = models.CharField(max_length=128, blank=False, null=False)
    # add foreign key to MatierePremiere ?

    def __str__(self):
        return self.raw_material

    class Meta:
        db_table = 'iscc_certificates_raw_materials'
        verbose_name = 'ISCC Certificate Raw Material'
        verbose_name_plural = 'ISCC Certificate Raw Materials'


class ISCCCertificateScope(models.Model):
    certificate = models.ForeignKey(ISCCCertificate, blank=False, null=False, on_delete=models.CASCADE)
    scope = models.ForeignKey(ISCCScope, blank=False, null=False, on_delete=models.CASCADE)

    def __str__(self):
        return self.scope.scope

    class Meta:
        db_table = 'iscc_certificates_scopes'
        verbose_name = 'ISCC Certificate Scope'
        verbose_name_plural = 'ISCC Certificate Scopes'


class DBSScope(models.Model):
    certification_type = models.CharField(max_length=512, default='')

    def natural_key(self):
        return {'certification_type': self.certification_type}

    def __str__(self):
        return self.certification_type

    class Meta:
        db_table = 'dbs_scopes'
        verbose_name = '2BS Scope'
        verbose_name_plural = '2BS Scopes'


class DBSCertificate(models.Model):
    certificate_id = models.CharField(max_length=64, null=False, blank=False)
    certificate_holder = models.CharField(max_length=256, null=False, blank=False)
    # warning, this column must be manually altered in db to support utf8mb4
    # command: ALTER TABLE dbs_certificates CHANGE certificate_holder certificate_holder VARCHAR(512) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
    # command: ALTER TABLE dbs_certificates CHANGE holder_address holder_address VARCHAR(512) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
    # do not change this field
    holder_address = models.CharField(max_length=512, null=False, blank=False)
    valid_from = models.DateField()
    valid_until = models.DateField()
    certification_type = models.CharField(max_length=512, default='')
    download_link = models.CharField(max_length=512, default='')

    def natural_key(self):
        scope = [s.scope.certification_type for s in self.dbscertificatescope_set.all()]
        return {'certificate_id': self.certificate_id,
                'certificate_holder': self.certificate_holder,
                'holder_address': self.holder_address,
                'valid_from': self.valid_from,
                'valid_until': self.valid_until,
                'certification_type': self.certification_type,
                'download_link': self.download_link,
                'scope': scope}

    def __str__(self):
        return self.certificate_id

    class Meta:
        db_table = 'dbs_certificates'
        verbose_name = '2BS Certificate'
        verbose_name_plural = '2BS Certificates'


class DBSCertificateScope(models.Model):
    certificate = models.ForeignKey(DBSCertificate, blank=False, null=False, on_delete=models.CASCADE)
    scope = models.ForeignKey(DBSScope, blank=False, null=False, on_delete=models.CASCADE)

    def __str__(self):
        return self.scope.scope

    class Meta:
        db_table = 'dbs_certificates_scopes'
        verbose_name = '2BS Certificate Scope'
        verbose_name_plural = '2BS Certificate Scopes'


class REDCertScope(models.Model):
    scope = models.CharField(max_length=8, null=False, blank=False)
    description_fr = models.CharField(max_length=256, null=False, blank=False)
    description_en = models.CharField(max_length=256, null=False, blank=False)
    description_de = models.CharField(max_length=256, null=False, blank=False)

    def __str__(self):
        return self.scope

    class Meta:
        db_table = 'redcert_scopes'
        verbose_name = 'REDCert Scope'
        verbose_name_plural = 'REDCert Scopes'


class REDCertBiomassType(models.Model):
    code = models.CharField(max_length=16, null=False, blank=False)
    description_fr = models.CharField(max_length=256, null=False, blank=False)
    description_en = models.CharField(max_length=256, null=False, blank=False)
    description_de = models.CharField(max_length=256, null=False, blank=False)

    def __str__(self):
        return self.code

    class Meta:
        db_table = 'redcert_biomass_types'
        verbose_name = 'REDCert Biomass Type'
        verbose_name_plural = 'REDCert Biomass Types'


class REDCertCertificate(models.Model):
    certificate_id = models.CharField(max_length=64, null=False, blank=False)
    certificate_holder = models.CharField(max_length=256, null=False, blank=False)
    city = models.CharField(max_length=256, default='')
    zip_code = models.CharField(max_length=12, default='')
    country_raw = models.CharField(max_length=32, default='')
    country = models.ForeignKey(Pays, on_delete=models.SET_NULL, blank=True, null=True)
    valid_from = models.DateField(null=False)
    valid_until = models.DateField(null=False)
    certificator = models.CharField(max_length=256, default='')
    certificate_type = models.CharField(max_length=256, default='')
    status = models.CharField(max_length=32, default='')

    def natural_key(self):
        scope = [s.scope.scope for s in self.redcertcertificatescope_set.all()]
        return {'certificate_id': self.certificate_id,
                'certificate_holder': self.certificate_holder,
                'city': self.city,
                'zip_code': self.zip_code,
                'country': self.country.natural_key() if self.country else '',
                'country_raw': self.country_raw,
                'valid_from': self.valid_from,
                'valid_until': self.valid_until,
                'certificator': self.certificator,
                'certificate_type': self.certificate_type,
                'scope': scope,
                'status': self.status}

    def __str__(self):
        return self.certificate_id

    class Meta:
        db_table = 'redcert_certificates'
        verbose_name = 'REDCert Certificate'
        verbose_name_plural = 'REDCert Certificates'


class REDCertCertificateScope(models.Model):
    certificate = models.ForeignKey(REDCertCertificate, blank=False, null=False, on_delete=models.CASCADE)
    scope = models.ForeignKey(REDCertScope, blank=False, null=False, on_delete=models.CASCADE)

    def __str__(self):
        return self.scope.scope

    class Meta:
        db_table = 'redcert_certificates_scopes'
        verbose_name = 'REDCert Certificate Scope'
        verbose_name_plural = 'REDCert Certificate Scopes'


class REDCertCertificateBiomass(models.Model):
    certificate = models.ForeignKey(REDCertCertificate, blank=False, null=False, on_delete=models.CASCADE)
    biomass = models.ForeignKey(REDCertBiomassType, blank=False, null=False, on_delete=models.CASCADE)

    def __str__(self):
        return self.biomass.code

    class Meta:
        db_table = 'redcert_certificates_biomass'
        verbose_name = 'REDCert Certificate Biomass'
        verbose_name_plural = 'REDCert Certificate Biomass'


class EntityISCCTradingCertificate(models.Model):
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE)
    certificate = models.ForeignKey(ISCCCertificate, on_delete=models.CASCADE)
    has_been_updated = models.BooleanField(default=False)

    def __str__(self):
        return '%s - %s' % (self.entity.name, self.certificate.certificate_id)

    def natural_key(self):
        data = self.certificate.natural_key()
        data['type'] = "ISCC"
        data['has_been_updated'] = self.has_been_updated
        return data

    class Meta:
        db_table = 'entity_iscc_trading_certificates'
        verbose_name = 'Certificat de Trading ISCC'
        verbose_name_plural = 'Certificats de Trading ISCC'


class EntityDBSTradingCertificate(models.Model):
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE)
    certificate = models.ForeignKey(DBSCertificate, on_delete=models.CASCADE)
    has_been_updated = models.BooleanField(default=False)

    def __str__(self):
        return '%s - %s' % (self.entity.name, self.certificate.certificate_id)

    def natural_key(self):
        data = self.certificate.natural_key()
        data['type'] = "2BS"
        data['has_been_updated'] = self.has_been_updated
        return data

    class Meta:
        db_table = 'entity_2bs_trading_certificates'
        verbose_name = 'Certificat de Trading 2BS'
        verbose_name_plural = 'Certificats de Trading 2BS'


class EntityREDCertTradingCertificate(models.Model):
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE)
    certificate = models.ForeignKey(REDCertCertificate, on_delete=models.CASCADE)
    has_been_updated = models.BooleanField(default=False)

    def __str__(self):
        return '%s - %s' % (self.entity.name, self.certificate.certificate_id)

    def natural_key(self):
        data = self.certificate.natural_key()
        data['type'] = "REDCERT"
        data['has_been_updated'] = self.has_been_updated
        return data

    class Meta:
        db_table = 'entity_redcert_trading_certificates'
        verbose_name = 'Certificat de Trading REDCert'
        verbose_name_plural = 'Certificats de Trading REDCert'


class ProductionSiteCertificate(models.Model):
    CERTIFICATE_TYPE = [("ISCC", "ISCC"), ("2BS", "2BS"), ('REDCERT', 'REDCERT')]
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE)
    production_site = models.ForeignKey(ProductionSite, null=True, on_delete=models.CASCADE)
    type = models.CharField(max_length=32, choices=CERTIFICATE_TYPE, default="Pending")

    certificate_iscc = models.ForeignKey(EntityISCCTradingCertificate, null=True, blank=True, on_delete=models.CASCADE)
    certificate_2bs = models.ForeignKey(EntityDBSTradingCertificate, null=True, blank=True, on_delete=models.CASCADE)
    certificate_redcert = models.ForeignKey(EntityREDCertTradingCertificate, null=True, blank=True, on_delete=models.CASCADE)

    def natural_key(self):
        if self.type == 'ISCC':
            cert = self.certificate_iscc
        elif self.type == '2BS':
            cert = self.certificate_2bs
        else:
            cert = self.certificate_redcert
        return {'type': self.type, 'certificate_id': cert.certificate.certificate_id}

    class Meta:
        db_table = 'production_sites_certificates'
        verbose_name = 'Certificat de site de production'
        verbose_name_plural = 'Certificats de sites de productions'


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
    volume_denaturant = models.FloatField(null=False, blank=False, default=0.0)
    volume_fossile = models.FloatField(null=False, blank=False, default=0.0)
    volume_pertes = models.FloatField(null=False, blank=False, default=0.0)

    added_by = models.ForeignKey(Entity, null=True, blank=True, on_delete=models.SET_NULL)
    added_by_user = models.ForeignKey(usermodel, null=True, blank=True, on_delete=models.SET_NULL)
    added_time = models.DateTimeField(auto_now_add=True)


    def natural_key(self):
        return {'previous': self.previous_stock.natural_key(), 'new': self.new_stock.natural_key(), 'volume_ethanol': self.volume_ethanol, 'volume_etbe': self.volume_etbe, 'volume_denaturant': self.volume_denaturant, 'volume_fossile': self.volume_pertes, 
                'added_by': self.added_by.natural_key(), 'added_by_user': self.added_by_user.natural_key(), 'added_time': self.added_time}

    class Meta:
        db_table = 'etbe_transformations'
        verbose_name = 'Transformation ETBE'
        verbose_name_plural = 'Transformations ETBE'