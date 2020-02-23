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

    class Meta:
        db_table = 'entities'
        verbose_name = 'Entity'
        verbose_name_plural = 'Entities'


class UserRights(models.Model):
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '%s - %s' % (self.user.email, self.entity.name)

    class Meta:
        db_table = 'users_rights'
        verbose_name = 'User Right'
        verbose_name_plural = 'Users Rights'

class TypeBiocarburant(models.Model):
    name = models.CharField(max_length=64)
    description = models.CharField(max_length=128)
    date_added = models.DateField(default=timezone.now)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'type_biocarburants'
        verbose_name = 'Type de Biocarburant'
        verbose_name_plural = 'Types de Biocarburants'

class FiliereProduction(models.Model):
    name = models.CharField(max_length=64)
    description = models.CharField(max_length=128)
    date_added = models.DateField(default=timezone.now)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'filieres_production'
        verbose_name = 'Filiere de Production'
        verbose_name_plural = 'Filieres de Production'

class Pays(models.Model):
    code_pays = models.CharField(max_length=64)
    name = models.CharField(max_length=128)
    date_added = models.DateField(default=timezone.now)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'pays'
        verbose_name = 'Pays'
        verbose_name_plural = 'Pays'

class Lot(models.Model):
    LOT_STATUS = (('Draft', 'Draft'), ('Validated', 'Validated'), ('Declared', 'Declared'))

    depot = models.CharField(max_length=64, blank=True)
    num_dae = models.CharField(max_length=64, blank=True)
    date_entree = models.DateField(blank=True)
    volume = models.IntegerField(default=0)
    type_biocarburant = models.ForeignKey(TypeBiocarburant, null=True, on_delete=models.SET_NULL), 
    filiere_production = models.ForeignKey(FiliereProduction, null=True, on_delete=models.SET_NULL)
    categorie = models.CharField(max_length=64)
    systeme_fournisseur = models.CharField(max_length=64)
    pays_origine = models.ForeignKey(Pays, null=True, on_delete=models.SET_NULL, related_name='pays_origine')
    respect_crit_durabilite = models.BooleanField(default=False)
    ges_transport = models.FloatField(blank=True)
    ges_distribution = models.FloatField(blank=True)
    ges_fossile = models.FloatField(blank=True)
    pays_production = models.ForeignKey(Pays, null=True, on_delete=models.SET_NULL, related_name='pays_production')
    date_mise_en_service = models.DateField(blank=True)
    status = models.CharField(max_length=64, choices=LOT_STATUS, default='Draft')

    def __str__(self):
        return self.id

    class Meta:
        db_table = 'lots'
        verbose_name = 'Lot'
        verbose_name_plural = 'Lots'