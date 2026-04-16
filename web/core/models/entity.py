import datetime
import hashlib

from django.db import models
from django.db.models import Q

from .geography import Department, Pays
from .user import UserRights


class EntityManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(closed_at__isnull=True)


class Entity(models.Model):
    PRODUCER = "Producteur"
    OPERATOR = "Opérateur"
    TRADER = "Trader"
    ADMIN = "Administration"
    AUDITOR = "Auditor"
    EXTERNAL_ADMIN = "Administration Externe"
    AIRLINE = "Compagnie aérienne"
    UNKNOWN = "Unknown"
    CPO = "Charge Point Operator"
    POWER_OR_HEAT_PRODUCER = "Power or Heat Producer"
    SAF_TRADER = "SAF Trader"
    BIOMETHANE_PRODUCER = "Producteur de biométhane"
    BIOMETHANE_PROVIDER = "Fournisseur de biométhane"
    ENTITY_TYPES = (
        (PRODUCER, "Producteur"),
        (OPERATOR, "Opérateur"),
        (ADMIN, "Administration"),
        (TRADER, "Trader"),
        (AUDITOR, "Auditeur"),
        (EXTERNAL_ADMIN, EXTERNAL_ADMIN),
        (CPO, CPO),
        (AIRLINE, AIRLINE),
        (UNKNOWN, "Unknown"),
        (POWER_OR_HEAT_PRODUCER, "Producteur d'électricité ou de chaleur"),
        (SAF_TRADER, "Trader de SAF"),
        (BIOMETHANE_PRODUCER, "Producteur de biométhane"),
        (BIOMETHANE_PROVIDER, "Fournisseur de biométhane"),
    )
    UNIT_CHOICE = (("l", "litres"), ("kg", "kg"), ("MJ", "MJ"))

    name = models.CharField(max_length=64, unique=True)
    date_added = models.DateTimeField(auto_now_add=True)
    entity_type = models.CharField(max_length=64, choices=ENTITY_TYPES, default="Unknown")
    parent_entity = models.ForeignKey("self", null=True, blank=True, on_delete=models.CASCADE)

    has_mac = models.BooleanField(default=False)
    has_trading = models.BooleanField(default=False)
    has_stocks = models.BooleanField(default=False)
    has_direct_deliveries = models.BooleanField(default=False)
    has_elec = models.BooleanField(default=False)

    legal_name = models.CharField(max_length=128, blank=True, default="")
    registration_id = models.CharField(max_length=64, blank=True, default="")
    sustainability_officer_phone_number = models.CharField(max_length=32, blank=True, default="")
    sustainability_officer_email = models.CharField(max_length=254, blank=True, default="")

    sustainability_officer = models.CharField(max_length=256, blank=True, default="")
    registered_address = models.CharField(max_length=256, blank=True, default="")
    registered_zipcode = models.CharField(max_length=64, blank=True, default="")
    registered_city = models.CharField(max_length=64, blank=True, default="")
    registered_country = models.ForeignKey(Pays, null=True, blank=True, on_delete=models.CASCADE)

    is_enabled = models.BooleanField(default=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    is_tiruert_liable = models.BooleanField(default=False)

    # Biomethane
    is_red_ii = models.BooleanField(default=False)

    # Qualicharge
    is_master = models.BooleanField(
        default=False, help_text="Indique si l'entité est maître (dans le cas de plusieurs CPO avec le même SIREN)"
    )

    hash = models.CharField(max_length=32, null=True, blank=True, default="")
    default_certificate = models.CharField(max_length=64, null=True, blank=True, default="")
    notifications_enabled = models.BooleanField(default=False)
    preferred_unit = models.CharField(max_length=64, choices=UNIT_CHOICE, default="l")
    has_saf = models.BooleanField(default=False)  # flag to tell if an operator or an airline can trade SAF
    activity_description = models.TextField(blank=True, default="")
    website = models.URLField(blank=True, default="")
    vat_number = models.CharField(max_length=32, blank=True, default="")
    accise_number = models.CharField(max_length=32, blank=True, default="")

    def __str__(self):
        return self.name

    def natural_key(self):
        d = {
            "name": self.name,
            "id": self.id,
            "entity_type": self.entity_type,
            "has_mac": self.has_mac,
            "has_trading": self.has_trading,
            "has_direct_deliveries": self.has_direct_deliveries,
            "has_stocks": self.has_stocks,
            "legal_name": self.legal_name,
            "registration_id": self.registration_id,
            "sustainability_officer": self.sustainability_officer,
            "sustainability_officer_phone_number": self.sustainability_officer_phone_number,
            "sustainability_officer_email": self.sustainability_officer_email,
            "registered_address": self.registered_address,
            "registered_zipcode": self.registered_zipcode,
            "registered_city": self.registered_city,
            "registered_country": self.registered_country.natural_key() if self.registered_country else None,
            "default_certificate": self.default_certificate,
            "preferred_unit": self.preferred_unit,
            "has_saf": self.has_saf,
            "has_elec": self.has_elec,
            "activity_description": self.activity_description,
            "website": self.website,
            "vat_number": self.vat_number,
            "is_enabled": self.is_enabled,
            "is_tiruert_liable": self.is_tiruert_liable,
            "is_red_ii": self.is_red_ii,
            "accise_number": self.accise_number,
        }
        if self.entity_type == Entity.EXTERNAL_ADMIN:
            d["ext_admin_pages"] = [e.right for e in self.externaladminrights_set.all()]
        return d

    def url_friendly_name(self):
        return self.name.replace(" ", "").upper()

    def slugify(self):
        from core.common import normalize  # noqa: E402

        return normalize(self.name).replace(" ", "_")

    def has_external_admin_right(self, right):
        return self.entity_type == Entity.EXTERNAL_ADMIN and right in self.externaladminrights_set.values_list(
            "right", flat=True
        )

    def save(self, *args, **kwargs):
        date_added = self.date_added
        if not date_added:
            date_added = datetime.date.today()
        data = self.name + self.entity_type + date_added.strftime("%Y%m%d")
        hash = hashlib.md5(data.encode("utf-8")).hexdigest()
        self.hash = hash
        super(Entity, self).save(*args, **kwargs)

    def get_accessible_departments(self):
        """
        Returns the departments accessible by this entity.
        """
        from entity.models import EntityScopeDepartment

        dept_ids = EntityScopeDepartment.objects.filter(entity=self).values_list("object_id", flat=True)
        return Department.objects.filter(id__in=dept_ids)

    def get_accessible_depots(self):
        """
        Returns the depots accessible by this entity.
        """
        from entity.models import EntityScopeDepot
        from transactions.models import Depot

        depot_ids = EntityScopeDepot.objects.filter(entity=self).values_list("object_id", flat=True)
        return Depot.objects.filter(id__in=depot_ids)

    def get_managing_external_admins(self):
        """
        For a biomethane producer, returns a list of the EXTERNAL_ADMIN entities (e.g. DREAL)
        that manages the department of the production unit, or None.
        For other entity types, returns None.
        """
        if self.entity_type != Entity.BIOMETHANE_PRODUCER:
            return None
        from biomethane.models.biomethane_production_unit import BiomethaneProductionUnit
        from entity.models import EntityScopeDepartment

        production_unit = BiomethaneProductionUnit.objects.filter(producer=self).first()
        if not production_unit or not production_unit.department:
            return None
        department = production_unit.department
        entity_ids = EntityScopeDepartment.objects.filter(object_id=department.id).values_list("entity_id", flat=True)

        return list(Entity.objects.filter(id__in=entity_ids, entity_type=Entity.EXTERNAL_ADMIN))

    def get_users_emails(self, **filters):
        filter_result = UserRights.objects.filter(entity=self, user__is_active=True, **filters)
        return filter_result.values_list("user__email", flat=True)

    def get_admin_users_emails(self, **filters):
        return self.get_users_emails(role=UserRights.ADMIN, **filters)

    # Return the entities that are allowed to be accessed by this entity
    def get_allowed_entities(self):
        entities = Entity.objects.all()
        filter_condition = Q()

        if self.has_external_admin_right(ExternalAdminRights.AIRLINE):
            filter_condition |= Q(entity_type=Entity.AIRLINE) | Q(entity_type=Entity.SAF_TRADER)
        if self.has_external_admin_right(ExternalAdminRights.ELEC):
            filter_condition |= Q(entity_type=Entity.CPO) | Q(entity_type=Entity.OPERATOR, has_elec=True)
        if self.has_external_admin_right(ExternalAdminRights.DOUBLE_COUNTING):
            filter_condition |= Q(entity_type=Entity.PRODUCER)
        if self.has_external_admin_right(ExternalAdminRights.TRANSFERRED_ELEC):
            filter_condition |= Q(entity_type=Entity.CPO) | Q(entity_type=Entity.OPERATOR)
        if self.has_external_admin_right(ExternalAdminRights.DREAL):
            accessible_dept_codes = self.get_accessible_departments().values_list("code_dept", flat=True)
            filter_condition |= Q(
                biomethane_production_unit__department__code_dept__in=accessible_dept_codes,
                entity_type=Entity.BIOMETHANE_PRODUCER,
            )

        return entities.filter(filter_condition)

    class Meta:
        db_table = "entities"
        verbose_name = "Entity"
        verbose_name_plural = "Entities"
        ordering = ["name"]

    objects = EntityManager()
    all_objects = models.Manager()


class ExternalAdminRights(models.Model):
    DOUBLE_COUNTING = "DCA"
    CUSTOM_STATS_AGRIMER = "AGRIMER"
    TIRIB_STATS = "TIRIB"
    AIRLINE = "AIRLINE"
    ELEC = "ELEC"
    TRANSFERRED_ELEC = "TRANSFERRED_ELEC"
    BIOFUEL = "BIOFUEL"
    DREAL = "DREAL"
    DGDDI = "DGDDI"

    RIGHTS = (
        (DOUBLE_COUNTING, DOUBLE_COUNTING),
        (CUSTOM_STATS_AGRIMER, CUSTOM_STATS_AGRIMER),
        (TIRIB_STATS, TIRIB_STATS),
        (AIRLINE, AIRLINE),
        (ELEC, ELEC),
        (TRANSFERRED_ELEC, TRANSFERRED_ELEC),
        (BIOFUEL, BIOFUEL),
        (DREAL, DREAL),
        (DGDDI, DGDDI),
    )
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE)
    right = models.CharField(max_length=32, choices=RIGHTS, default="", blank=False, null=False)

    class Meta:
        db_table = "ext_admin_rights"
        verbose_name = "External Admin Right"
        verbose_name_plural = "External Admin Rights"
