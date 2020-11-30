from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.auth import get_user_model

usermodel = get_user_model()


class Entity(models.Model):
    ENTITY_TYPES = (('Producteur', 'Producteur'), ('Opérateur', 'Opérateur'),
                    ('Administration', 'Administration'), ('Trader', 'Trader'), ('Unknown', 'Unknown'))

    name = models.CharField(max_length=64, unique=True)
    date_added = models.DateTimeField(auto_now_add=True)
    entity_type = models.CharField(max_length=64, choices=ENTITY_TYPES, default='Unknown')
    parent_entity = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE)

    producer_with_mac = models.BooleanField(default=False)
    producer_with_trading = models.BooleanField(default=False)
    trading_certificate = models.FileField(null=True, blank=True)
    has_mac = models.BooleanField(default=False)
    has_trading = models.BooleanField(default=False)
    national_system_certificate = models.CharField(max_length=64, null=True, blank=True)

    def __str__(self):
        return self.name

    def natural_key(self):
        return {'name': self.name, 'id': self.id, 'entity_type': self.entity_type, 'has_mac': self.has_mac, 'has_trading': self.has_trading, 
            'national_system_certificate': self.national_system_certificate}

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
    name = models.CharField(max_length=128)
    description = models.CharField(max_length=128)
    date_added = models.DateField(default=timezone.now)
    code = models.CharField(max_length=64, unique=True)
    compatible_alcool = models.BooleanField(default=False)
    compatible_graisse = models.BooleanField(default=False)
    is_double_compte = models.BooleanField(default=False)
    is_huile_vegetale = models.BooleanField(default=False)
    
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
    TYPE_DEPOT = (('EFS', 'EFS'), ('EFPE', 'EFPE'), ('OTHER', 'Autre'),)
    name = models.CharField(max_length=128, null=False, blank=False)
    city = models.CharField(max_length=128, null=True, blank=True)
    depot_id = models.CharField(max_length=32, null=False, blank=False)
    country = models.ForeignKey(Pays, null=True, blank=False, on_delete=models.SET_NULL)
    depot_type = models.CharField(max_length=32, choices=TYPE_DEPOT, default='OTHER')

    address = models.CharField(max_length=128, null=False, blank=False)
    postal_code = models.CharField(max_length=32, null=False, blank=False)
    TYPE_OWNERSHIP = (('OWN', 'Propre'), ('THIRD_PARTY', 'Tiers'))
    ownership_type = models.CharField(max_length=32, choices=TYPE_OWNERSHIP, default='THIRD_PARTY')
    
    def __str__(self):
        return self.name

    def natural_key(self):
        return {'depot_id': self.depot_id, 'name': self.name, 'city': self.city, 'country': self.country.natural_key(), 
            'depot_type': self.depot_type, 'address': self.address, 'postal_code': self.postal_code, 'ownership_type': self.ownership_type}

    class Meta:
        db_table = 'depots'
        verbose_name = 'Dépôt'
        verbose_name_plural = 'Dépôts'


from producers.models import ProductionSite

# deprecated. Use LotV2
class Lot(models.Model):
    carbure_id = models.CharField(max_length=64, blank=True, default='')
    class Meta:
        db_table = 'lots'


class LotV2(models.Model):
    LOT_STATUS = (('Draft', 'Brouillon'), ('Validated', 'Validé'))
    SOURCE_CHOICES = (('EXCEL', 'Excel'), ('MANUAL', 'Manual'))

    period = models.CharField(max_length=64, blank=True, default='')
    carbure_id = models.CharField(max_length=64, blank=True, default='')
    # producer
    producer_is_in_carbure = models.BooleanField(default=True)
    carbure_producer = models.ForeignKey(Entity, null=True, blank=True, on_delete=models.SET_NULL, related_name='producer_lotv2')
    unknown_producer = models.CharField(max_length=64, blank=True, null=True, default='')

    production_site_is_in_carbure = models.BooleanField(default=True)
    carbure_production_site = models.ForeignKey(ProductionSite, null=True, blank=True, on_delete=models.SET_NULL)
    unknown_production_site = models.CharField(max_length=64, blank=True, null=True, default='')
    unknown_production_country = models.ForeignKey(Pays, null=True, blank=True, on_delete=models.SET_NULL, related_name='unknown_production_site_country')

    unknown_production_site_com_date = models.DateField(blank=True, null=True)
    unknown_production_site_reference = models.CharField(max_length=64, blank=True, null=True, default='')
    unknown_production_site_dbl_counting = models.CharField(max_length=64, blank=True, null=True, default='')

    # lot details
    volume = models.IntegerField(default=0)
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
        'data_origin_entity': self.data_origin_entity.natural_key() if self.data_origin_entity else None}

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'lots_v2'
        verbose_name = 'LotV2'
        verbose_name_plural = 'LotsV2'
        indexes = [
            models.Index(fields=["status"]),
        ]


class LotTransaction(models.Model):
    DELIVERY_STATUS = (('N', 'En Attente'), ('A', 'Accepté'), ('R', 'Refusé'), ('AC', 'À corriger'), ('AA', 'Corrigé'))
    lot = models.ForeignKey(LotV2, null=False, blank=False, on_delete=models.CASCADE)

    # vendor / producer
    vendor_is_in_carbure = models.BooleanField(default=True)
    carbure_vendor = models.ForeignKey(Entity, null=True, blank=True, on_delete=models.SET_NULL, related_name='vendor_transaction')
    unknown_vendor = models.CharField(max_length=64, blank=True, null=True, default='')

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
    champ_libre = models.CharField(max_length=64, blank=True, null=True, default='')
    # mise a consommation?
    is_mac = models.BooleanField(default=False)
    # this PoS is part of a multiple PoS batch 
    is_batch = models.BooleanField(default=False)

    def __str__(self):
        return str(self.id)

    def natural_key(self):
        return {'lot': self.lot.natural_key(), 'vendor_is_in_carbure': self.vendor_is_in_carbure, 'carbure_vendor': self.carbure_vendor.natural_key() if self.carbure_vendor else None,
        'unknown_vendor': self.unknown_vendor, 'dae': self.dae, 'client_is_in_carbure': self.client_is_in_carbure,
        'carbure_client': self.carbure_client.natural_key() if self.carbure_client else None,
        'unknown_client': self.unknown_client, 'delivery_date': self.delivery_date, 'delivery_site_is_in_carbure': self.delivery_site_is_in_carbure,
        'carbure_delivery_site': self.carbure_delivery_site.natural_key() if self.carbure_delivery_site else None, 'unknown_delivery_site': self.unknown_delivery_site,
        'unknown_delivery_site_country': self.unknown_delivery_site_country.natural_key() if self.unknown_delivery_site_country else None, 'delivery_status': self.delivery_status,
        'champ_libre': self.champ_libre, 'is_mac': self.is_mac, 'is_batch': self.is_batch,
        'id': self.id}

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
    rule_triggered = models.CharField(max_length=64, blank=True, null=True, default='')

    warning_to_user = models.BooleanField(default=False)
    warning_to_admin = models.BooleanField(default=False)
    block_validation = models.BooleanField(default=False)
    message = models.TextField(blank=True, null=True, default='')
    details = models.TextField(blank=True, null=True, default='')

    def __str__(self):
        return self.rule_triggered

    def natural_key(self):
        return {'lot_id': self.lot.id, 'error': self.message, 'details': self.details, 'is_blocking': self.block_validation, 'is_warning': self.warning_to_user}

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


class EntityISCCTradingCertificate(models.Model):
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE)
    certificate = models.ForeignKey(ISCCCertificate, on_delete=models.CASCADE)
    has_been_updated = models.BooleanField(default=False)

    def __str__(self):
        return self.certificate.certificate_id

    def natural_key(self):
        data = self.certificate.natural_key()
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
        return self.certificate.certificate_id

    def natural_key(self):
        data = self.certificate.natural_key()
        data['has_been_updated'] = self.has_been_updated
        return data

    class Meta:
        db_table = 'entity_2bs_trading_certificates'
        verbose_name = 'Certificat de Trading 2BS'
        verbose_name_plural = 'Certificats de Trading 2BS'


class ProductionSiteCertificate(models.Model):
    CERTIFICATE_TYPE = [("ISCC", "ISCC"), ("2BS", "2BS")]
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE)
    production_site = models.ForeignKey(ProductionSite, null=True, on_delete=models.CASCADE)
    type = models.CharField(max_length=32, choices=CERTIFICATE_TYPE, default="Pending")
    
    certificate_iscc = models.ForeignKey(EntityISCCTradingCertificate, null=True, blank=True, on_delete=models.CASCADE)
    certificate_2bs = models.ForeignKey(EntityDBSTradingCertificate, null=True, blank=True, on_delete=models.CASCADE)

    def natural_key(self):
        return {'type': self.type, 'certificate_id': self.certificate_iscc.certificate.certificate_id if self.type == 'ISCC' else self.certificate_2bs.certificate.certificate_id}

    class Meta:
        db_table = 'production_sites_certificates'
        verbose_name = 'Certificat de site de production'
        verbose_name_plural = 'Certificats de sites de productions'

        