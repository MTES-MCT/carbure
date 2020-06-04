from django.db import models
from django.conf import settings
from django.utils import timezone


class Entity(models.Model):
    ENTITY_TYPES = (('Producteur', 'Producteur'), ('Opérateur', 'Opérateur'),
                    ('Administration', 'Administration'), ('Unknown', 'Unknown'))

    name = models.CharField(max_length=64)
    date_added = models.DateTimeField(auto_now_add=True)
    entity_type = models.CharField(max_length=64, choices=ENTITY_TYPES, default='Unknown')
    parent_entity = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    def natural_key(self):
        return self.name

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

    class Meta:
        db_table = 'users_rights'
        verbose_name = 'User Right'
        verbose_name_plural = 'Users Rights'


class Biocarburant(models.Model):
    name = models.CharField(max_length=64)
    description = models.CharField(max_length=128)
    date_added = models.DateField(default=timezone.now)
    code = models.CharField(max_length=16, unique=True)

    def __str__(self):
        return self.name

    def natural_key(self):
        return self.name

    class Meta:
        db_table = 'biocarburants'
        verbose_name = 'Biocarburant'
        verbose_name_plural = 'Biocarburants'


class MatierePremiere(models.Model):
    name = models.CharField(max_length=128)
    description = models.CharField(max_length=128)
    date_added = models.DateField(default=timezone.now)
    code = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return self.name

    def natural_key(self):
        return self.name

    class Meta:
        db_table = 'matieres_premieres'
        verbose_name = 'Matiere Premiere'
        verbose_name_plural = 'Matieres Premieres'


class Pays(models.Model):
    code_pays = models.CharField(max_length=64)
    name = models.CharField(max_length=128)
    date_added = models.DateField(default=timezone.now)

    def __str__(self):
        return self.name

    def natural_key(self):
        return self.name

    class Meta:
        db_table = 'pays'
        verbose_name = 'Pays'
        verbose_name_plural = 'Pays'


class Depot(models.Model):
    name = models.CharField(max_length=128, null=False, blank=False)
    city = models.CharField(max_length=128, null=True, blank=True)
    depot_id = models.CharField(max_length=32, null=False, blank=False)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'depots'
        verbose_name = 'Dépôt'
        verbose_name_plural = 'Dépôts'


from producers.models import ProductionSite


class Lot(models.Model):
    LOT_STATUS = (('Draft', 'Brouillon'), ('Validated', 'Validé'))
    DELIVERY_STATUS = (('N', 'En Attente'), ('A', 'Accepté'), ('R', 'Refusé'), ('AC', 'À corriger'), ('AA', 'Corrigé'))

    period = models.CharField(max_length=64, blank=True, default='')
    carbure_id = models.CharField(max_length=64, blank=True, default='')
    # producer
    producer = models.ForeignKey(Entity, null=True, blank=True, on_delete=models.SET_NULL, related_name='producer')
    production_site = models.ForeignKey(ProductionSite, null=True, blank=True, on_delete=models.SET_NULL)

    # client / delivery
    dae = models.CharField(max_length=64, blank=True, default='')
    ea_delivery_date = models.DateField(blank=True, null=True)
    ea_delivery_site = models.CharField(max_length=64, blank=True, default='')
    ea = models.ForeignKey(Entity, null=True, blank=True, on_delete=models.SET_NULL, related_name='ea')

    # lot details
    volume = models.IntegerField(default=0)
    matiere_premiere = models.ForeignKey(MatierePremiere, null=True, on_delete=models.SET_NULL)
    biocarburant = models.ForeignKey(Biocarburant, null=True, on_delete=models.SET_NULL)
    pays_origine = models.ForeignKey(Pays, null=True, on_delete=models.SET_NULL, related_name='pays_origine')

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
    client_id = models.CharField(max_length=64, blank=True, default='')
    status = models.CharField(max_length=64, choices=LOT_STATUS, default='Draft')

    # ea delivery confirmation
    ea_delivery_status = models.CharField(max_length=64, choices=DELIVERY_STATUS, default='N')

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'lots'
        verbose_name = 'Lot'
        verbose_name_plural = 'Lots'


class LotV2(models.Model):
    LOT_STATUS = (('Draft', 'Brouillon'), ('Validated', 'Validé'))
    SOURCE_CHOICES = (('EXCEL', 'Excel'), ('MANUAL', 'Manual'))

    period = models.CharField(max_length=64, blank=True, default='')
    carbure_id = models.CharField(max_length=64, blank=True, default='')
    # producer
    producer_is_in_carbure = models.BooleanField(default=True)
    carbure_producer = models.ForeignKey(Entity, null=True, blank=True, on_delete=models.SET_NULL, related_name='producer')
    unknown_producer = models.CharField(max_length=64, blank=True, default='')

    production_site_is_in_carbure = models.BooleanField(default=True)
    carbure_production_site = models.ForeignKey(ProductionSite, null=True, blank=True, on_delete=models.SET_NULL)
    unknown_production_site = models.CharField(max_length=64, blank=True, default='')

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
    client_id = models.CharField(max_length=64, blank=True, default='')
    status = models.CharField(max_length=64, choices=LOT_STATUS, default='Draft')
    source = models.CharField(max_length=32, choices=SOURCE_CHOICES, default='Manual')

    # lot has been split into many sublots ?
    parent_lot = models.ForeignKey('self', null=True, blank=True)
    is_split = models.BooleanField(default=False)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'lots_v2'
        verbose_name = 'LotV2'
        verbose_name_plural = 'LotsV2'


class LotTransaction(models.Model):
    DELIVERY_STATUS = (('N', 'En Attente'), ('A', 'Accepté'), ('R', 'Refusé'), ('AC', 'À corriger'), ('AA', 'Corrigé'))
    lot = models.ForeignKey(LotV2, null=False, blank=False, on_delete=models.CASCADE)

    # vendor / producer
    vendor_is_in_carbure = models.BooleanField(default=True)
    carbure_vendor = models.ForeignKey(Entity, null=True, blank=True, on_delete=models.SET_NULL)
    unknown_vendor = models.CharField(max_length=64, blank=True, default='')

    # client / delivery
    dae = models.CharField(max_length=64, blank=True, default='')
    client_is_in_carbure = models.BooleanField(default=True)
    carbure_client = models.ForeignKey(Entity, null=True, blank=True, on_delete=models.SET_NULL)
    unknown_client = models.CharField(max_length=64, blank=True, default='')
    delivery_date = models.DateField(blank=True, null=True)
    delivery_site_is_in_carbure = models.BooleanField(default=True)
    carbure_delivery_site = models.ForeignKey(Depot, null=True, blank=True, on_delete=models.SET_NULL)
    undelivery_site = models.CharField(max_length=64, blank=True, default='')
    export_ue = models.BooleanField(default=False)
    export_hors_ue = models.BooleanField(default=False)
    delivery_status = models.CharField(max_length=64, choices=DELIVERY_STATUS, default='N')

    # ghg impact
    etd_impact = models.FloatField(default=0.0)
    ghg_total = models.FloatField(default=0.0)
    ghg_reduction = models.FloatField(default=0.0)

    champ_libre = models.CharField(max_length=64, blank=True, default='')

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'transactions'
        verbose_name = 'Transaction'
        verbose_name_plural = 'Transactions'


class LotComment(models.Model):
    entity = models.ForeignKey(Entity, null=True, blank=True, on_delete=models.SET_NULL)
    lot = models.ForeignKey(Lot, on_delete=models.CASCADE)
    comment = models.TextField()

    def __str__(self):
        return str(self.comment)

    class Meta:
        db_table = 'lots_comments'
        verbose_name = 'LotComment'
        verbose_name_plural = 'LotComments'


class LotError(models.Model):
    lot = models.ForeignKey(Lot, null=False, blank=False, on_delete=models.CASCADE)
    field = models.CharField(max_length=32, null=False, blank=False)
    value = models.CharField(max_length=128, null=True, blank=True)
    error = models.CharField(max_length=256, null=False, blank=False)

    def __str__(self):
        return self.error

    class Meta:
        db_table = 'lots_errors'
        verbose_name = 'LotError'
        verbose_name_plural = 'LotErrors'


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

