# https://django-authtools.readthedocs.io/en/latest/how-to/invitation-email.html
# allows a manual user creation by an admin, without setting a password

from django.contrib import admin
from django.db.models import Q
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordResetForm
from django.utils.crypto import get_random_string
from django_admin_listfilter_dropdown.filters import (
    DropdownFilter,
    RelatedOnlyDropdownFilter,
)
from django.utils.translation import gettext_lazy as _
from django.db.models import Sum
from django.db import transaction
from django.contrib import messages

from authtools.admin import NamedUserAdmin
from authtools.forms import UserCreationForm
from core.models import (
    CarbureLot,
    CarbureLotComment,
    CarbureLotEvent,
    CarbureStock,
    CarbureStockTransformation,
    Entity,
    EntityCertificate,
    ExternalAdminRights,
    GenericCertificate,
    UserRights,
    UserPreferences,
    Biocarburant,
    MatierePremiere,
    Pays,
    UserRightsRequests,
)
from core.models import Depot, GenericError
from core.models import SustainabilityDeclaration, EntityDepot
from core.models import TransactionDistance
from core.models import CarbureNotification
from entity.helpers import enable_entity
from transactions.sanity_checks.helpers import get_prefetched_data
from entity.services import enable_depot


def custom_titled_filter(title):
    class Wrapper(admin.FieldListFilter):
        def __new__(cls, *args, **kwargs):
            instance = admin.FieldListFilter.create(*args, **kwargs)
            instance.title = title
            return instance

    return Wrapper


class EntityAdmin(admin.ModelAdmin):
    list_display = ("entity_type", "name", "parent_entity", "is_enabled")
    search_fields = ("entity_type", "name")
    list_filter = ["entity_type"]
    readonly_fields = ["is_enabled"]

    actions = ["enable_entity"]

    def enable_entity(self, request, queryset):
        for entity in queryset:
            enable_entity(entity)

    enable_entity.short_description = "Activer les sociétés sélectionnées"


class UserRightsAdmin(admin.ModelAdmin):
    list_display = ("user", "entity", "role")
    search_fields = ("user__name", "entity__name")


class UserRightsRequestsAdmin(admin.ModelAdmin):
    list_display = ("user", "entity", "status", "role")
    search_fields = ("user__name", "entity__name", "status")


class UserPreferencesAdmin(admin.ModelAdmin):
    list_display = ("user", "default_entity")
    search_fields = ("user__name", "default_entity__name")


class BiocarburantAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "name",
        "description",
        "is_alcool",
        "is_graisse",
        "is_displayed",
        "compatible_essence",
        "compatible_diesel",
    )
    search_fields = ("name",)
    readonly_fields = ("code",)
    list_filter = ("is_alcool", "is_graisse", "is_displayed")


class MatierePremiereAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "name",
        "description",
        "compatible_alcool",
        "compatible_graisse",
        "is_double_compte",
        "is_huile_vegetale",
        "is_displayed",
    )
    search_fields = ("name",)
    readonly_fields = ("code",)
    list_filter = (
        "compatible_alcool",
        "compatible_graisse",
        "is_double_compte",
        "is_huile_vegetale",
        "is_displayed",
    )


class PaysAdmin(admin.ModelAdmin):
    list_display = ("name", "code_pays", "is_in_europe")
    search_fields = (
        "name",
        "code_pays",
    )
    list_filter = ("is_in_europe",)


class DepotAdmin(admin.ModelAdmin):
    list_display = ("name", "depot_id", "city", "depot_type", "gps_coordinates", "private", "is_enabled")
    search_fields = ("name", "city", "depot_id")
    list_filter = ("depot_type",)
    readonly_fields = ("is_enabled",)
    actions = ["enable_depot"]

    def enable_depot(self, request, queryset):
        for depot in queryset:
            response = enable_depot.enable_depot(depot)
            messages.add_message(request, messages.SUCCESS, response)

    enable_depot.short_description = "Valider les dépôts sélectionnés"


class GenericErrorAdmin(admin.ModelAdmin):
    list_display = (
        "lot",
        "error",
        "is_blocking",
        "display_to_creator",
        "display_to_recipient",
        "field",
        "fields",
        "value",
        "extra",
    )
    search_fields = ("error", "field", "extra")
    list_filter = (
        "error",
        "is_blocking",
    )
    raw_id_fields = ("lot",)


class SustainabilityDeclarationAdmin(admin.ModelAdmin):
    date_hierarchy = "period"
    list_display = ("entity", "period", "declared", "checked", "deadline")
    search_fields = ("entity__name",)
    list_filter = (("period", DropdownFilter), "declared", "checked", "entity")
    actions = ["validate_declarations", "invalidate_declarations"]

    def validate_declarations(self, request, queryset):
        for declaration in queryset:
            period = declaration.period.year * 100 + declaration.period.month
            CarbureLot.objects.filter(period=period).filter(
                Q(carbure_client=declaration.entity) | Q(carbure_supplier=declaration.entity)
            ).exclude(lot_status__in=[CarbureLot.DRAFT, CarbureLot.DELETED]).update(lot_status=CarbureLot.FROZEN)
            declaration.declared = True
            declaration.save()

    validate_declarations.short_description = "Valider les déclarations"

    def invalidate_declarations(self, request, queryset):
        for declaration in queryset:
            period = declaration.period.year * 100 + declaration.period.month
            CarbureLot.objects.filter(period=period).filter(
                Q(carbure_client=declaration.entity) | Q(carbure_supplier=declaration.entity),
                lot_status=CarbureLot.FROZEN,
            ).update(lot_status=CarbureLot.ACCEPTED)
            declaration.declared = False
            declaration.checked = False
            declaration.save()

    invalidate_declarations.short_description = "Invalider les déclarations"


class EntityDepotAdmin(admin.ModelAdmin):
    list_display = (
        "entity",
        "depot",
        "blending_is_outsourced",
    )
    search_fields = (
        "entity__name",
        "depot__name",
    )
    list_filter = ("blending_is_outsourced",)


class TransactionDistanceAdmin(admin.ModelAdmin):
    list_display = ("starting_point", "delivery_point", "distance")
    search_fields = (
        "starting_point",
        "delivery_point",
    )


admin.site.register(Entity, EntityAdmin)
admin.site.register(UserRights, UserRightsAdmin)
admin.site.register(UserRightsRequests, UserRightsRequestsAdmin)
admin.site.register(UserPreferences, UserPreferencesAdmin)
admin.site.register(Biocarburant, BiocarburantAdmin)
admin.site.register(MatierePremiere, MatierePremiereAdmin)
admin.site.register(Pays, PaysAdmin)
admin.site.register(Depot, DepotAdmin)
admin.site.register(GenericError, GenericErrorAdmin)
admin.site.register(SustainabilityDeclaration, SustainabilityDeclarationAdmin)
admin.site.register(EntityDepot, EntityDepotAdmin)
admin.site.register(TransactionDistance, TransactionDistanceAdmin)


# authtool custom user model
User = get_user_model()


class UserCreationForm(UserCreationForm):
    """
    A UserCreationForm with optional password inputs.
    """

    def __init__(self, *args, **kwargs):
        super(UserCreationForm, self).__init__(*args, **kwargs)
        self.fields["password1"].required = False
        self.fields["password2"].required = False
        # If one field gets autocompleted but not the other, our 'neither
        # password or both password' validation will be triggered.
        self.fields["password1"].widget.attrs["autocomplete"] = "off"
        self.fields["password2"].widget.attrs["autocomplete"] = "off"

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = super(UserCreationForm, self).clean_password2()
        if bool(password1) ^ bool(password2):
            raise forms.ValidationError("Fill out both fields")
        return password2


class UserAdmin(NamedUserAdmin):
    """
    A UserAdmin that sends a password-reset email when creating a new user,
    unless a password was entered.
    """

    add_form = UserCreationForm
    add_fieldsets = (
        (
            None,
            {
                "description": (
                    "Enter the new user's name and email address and click save."
                    " The user will be emailed a link allowing them to login to"
                    " the site and set their password."
                ),
                "fields": (
                    "email",
                    "name",
                ),
            },
        ),
        (
            "Password",
            {
                "description": "Optionally, you may set the user's password here.",
                "fields": ("password1", "password2"),
                "classes": ("collapse", "collapse-closed"),
            },
        ),
    )

    def save_model(self, request, obj, form, change):
        if not change and not obj.has_usable_password():
            # Django's PasswordResetForm won't let us reset an unusable
            # password. We set it above super() so we don't have to save twice.
            obj.set_password(get_random_string())
            reset_password = True
        else:
            reset_password = False

        super(UserAdmin, self).save_model(request, obj, form, change)

        if reset_password:
            reset_form = PasswordResetForm({"email": obj.email})
            assert reset_form.is_valid()
            reset_form.save(
                subject_template_name="registration/account_creation_subject.txt",
                email_template_name="registration/account_creation_email.html",
            )


admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(ExternalAdminRights)
class ExtAdminRightsAdmin(admin.ModelAdmin):
    list_display = (
        "entity",
        "right",
    )


class NameSortedRelatedOnlyDropdownFilter(RelatedOnlyDropdownFilter):
    template = "django_admin_listfilter_dropdown/dropdown_filter.html"

    def choices(self, changelist):
        data = list(super(RelatedOnlyDropdownFilter, self).choices(changelist))
        # all elements except select-all
        tosort = [x for x in data if x["display"] != _("All")]
        sortedlist = sorted(tosort, key=lambda x: x["display"])
        selectall = data[0]
        sortedlist.insert(0, selectall)
        return sortedlist


@admin.register(CarbureLot)
class CarbureLotAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "carbure_id",
        "parent_lot",
        "parent_stock",
        "year",
        "period",
        "transport_document_reference",
        "get_producer",
        "get_production_site",
        "get_supplier",
        "get_client",
        "delivery_date",
        "get_delivery_site",
        "get_biofuel",
        "get_feedstock",
        "volume",
        "lot_status",
        "correction_status",
        "delivery_type",
    ]
    raw_id_fields = ["parent_lot", "parent_stock"]
    list_filter = (
        "year",
        ("period", DropdownFilter),
        "lot_status",
        "correction_status",
        ("biofuel", NameSortedRelatedOnlyDropdownFilter),
        ("feedstock", NameSortedRelatedOnlyDropdownFilter),
        ("carbure_supplier", NameSortedRelatedOnlyDropdownFilter),
        ("carbure_client", NameSortedRelatedOnlyDropdownFilter),
        "delivery_type",
        ("carbure_delivery_site", NameSortedRelatedOnlyDropdownFilter),
        ("carbure_production_site", NameSortedRelatedOnlyDropdownFilter),
        ("carbure_client__entity_type", custom_titled_filter("Type de client")),
    )
    search_fields = (
        "id",
        "transport_document_reference",
        "free_field",
        "carbure_id",
        "volume",
    )
    readonly_fields = ("created_at",)
    actions = [
        "regen_carbure_id",
        "send_to_pending",
        "send_to_draft",
        "recalc_score",
        "delete_lots",
    ]

    def has_delete_permission(self, request, obj=None):
        return False

    def send_to_pending(self, request, queryset):
        for lot in queryset:
            lot.lot_status = CarbureLot.PENDING
            lot.save()

    send_to_pending.short_description = "Renvoi en attente"

    def send_to_draft(self, request, queryset):
        for lot in queryset:
            lot.lot_status = CarbureLot.DRAFT
            lot.save()

    send_to_draft.short_description = "Renvoi en brouillons"

    @transaction.atomic
    def delete_lots(self, request, queryset):
        queryset.update(lot_status="DELETED")
        events = [CarbureLotEvent(lot=lot, user=request.user, event_type=CarbureLotEvent.DELETED_ADMIN) for lot in queryset]
        CarbureLotEvent.objects.bulk_create(events)

    delete_lots.short_description = "Changer le statut des lots en SUPRRIMÉ"

    def regen_carbure_id(self, request, queryset):
        for lot in queryset:
            lot.generate_carbure_id()
            lot.save()

    regen_carbure_id.short_description = "Regénérer CarbureID"

    def recalc_score(self, request, queryset):
        prefetched_data = get_prefetched_data()
        for lot in queryset:
            lot.recalc_reliability_score(prefetched_data)
            lot.save()

    recalc_score.short_description = "Recalculer Note"

    def get_producer(self, obj):
        return obj.carbure_producer.name if obj.carbure_producer else "U - " + str(obj.unknown_producer)

    get_producer.admin_order_field = "carbure_producer__name"
    get_producer.short_description = "Producer"

    def get_production_site(self, obj):
        return obj.carbure_production_site.name if obj.carbure_production_site else "U - %s" % (obj.unknown_production_site)

    get_production_site.admin_order_field = "carbure_production_site__name"
    get_production_site.short_description = "Production Site"

    def get_supplier(self, obj):
        return obj.carbure_supplier.name if obj.carbure_supplier else "U - %s" % (obj.unknown_supplier)

    get_supplier.admin_order_field = "carbure_supplier__name"
    get_supplier.short_description = "Supplier"

    def get_client(self, obj):
        return obj.carbure_client.name if obj.carbure_client else "U - %s" % (obj.unknown_client)

    get_client.admin_order_field = "carbure_client__name"
    get_client.short_description = "Client"

    def get_delivery_site(self, obj):
        return obj.carbure_delivery_site.name if obj.carbure_delivery_site else "U - %s" % (obj.unknown_delivery_site)

    get_delivery_site.admin_order_field = "carbure_delivery_site__name"
    get_delivery_site.short_description = "Delivery Site"

    def get_biofuel(self, obj):
        return obj.biofuel.code if obj.biofuel else ""

    get_biofuel.admin_order_field = "biofuel__code"
    get_biofuel.short_description = "Biofuel"

    def get_feedstock(self, obj):
        return obj.feedstock.code if obj.feedstock else ""

    get_feedstock.admin_order_field = "feedstock__code"
    get_feedstock.short_description = "Feedstock"


@admin.register(CarbureStock)
class CarbureStockAdmin(admin.ModelAdmin):
    list_display = [
        "parent_lot",
        "get_delivery_date",
        "carbure_id",
        "get_client",
        "get_depot",
        "get_biofuel",
        "get_feedstock",
        "get_orig_volume",
        "remaining_volume",
        "get_supplier",
    ]
    raw_id_fields = ["parent_lot", "parent_transformation"]
    list_filter = (
        ("parent_lot__period", DropdownFilter),
        ("biofuel", NameSortedRelatedOnlyDropdownFilter),
        ("feedstock", NameSortedRelatedOnlyDropdownFilter),
        ("carbure_supplier", NameSortedRelatedOnlyDropdownFilter),
        ("carbure_client", NameSortedRelatedOnlyDropdownFilter),
        ("depot", NameSortedRelatedOnlyDropdownFilter),
    )
    search_fields = (
        "id",
        "parent_lot__transport_document_reference",
        "parent_lot__free_field",
        "parent_lot__carbure_id",
        "carbure_id",
    )
    actions = ["regen_carbure_id", "recalc_stock"]

    def regen_carbure_id(self, request, queryset):
        for stock in queryset:
            stock.generate_carbure_id()
            stock.save()

    regen_carbure_id.short_description = "Regénérer CarbureID"

    def recalc_stock(self, request, queryset):
        for stock in queryset:
            child_volume = (
                CarbureLot.objects.filter(parent_stock=stock)
                .exclude(lot_status=CarbureLot.DELETED)
                .aggregate(child_volume=Sum("volume"))
            )
            vol = child_volume["child_volume"]
            if vol is None:
                vol = 0
            transformations_volume = CarbureStockTransformation.objects.filter(source_stock=stock).aggregate(
                vol=Sum("volume_deducted_from_source")
            )
            if transformations_volume["vol"] is not None:
                vol += transformations_volume["vol"]
            initial_volume = stock.parent_lot.volume if stock.parent_lot else stock.parent_transformation.volume_destination
            theo_remaining = initial_volume - vol
            diff = stock.remaining_volume - theo_remaining
            if abs(diff) > 0.1:
                stock.remaining_volume = round(theo_remaining, 2)
                stock.remaining_weight = stock.get_weight()
                stock.remaining_lhv_amount = stock.get_lhv_amount()
                stock.save()

    recalc_stock.short_description = "Recalculer stock restant"

    def get_delivery_date(self, obj):
        return obj.get_delivery_date()

    get_delivery_date.short_description = "Delivery Date"

    def get_supplier(self, obj):
        return obj.carbure_supplier.name if obj.carbure_supplier else "U - %s" % (obj.unknown_supplier)

    get_supplier.admin_order_field = "carbure_supplier__name"
    get_supplier.short_description = "Supplier"

    def get_client(self, obj):
        return obj.carbure_client.name if obj.carbure_client else "U - %s" % (obj.unknown_client)

    get_client.admin_order_field = "carbure_client__name"
    get_client.short_description = "Client"

    def get_depot(self, obj):
        return obj.depot.name if obj.depot else "UNKNOWN"

    get_depot.admin_order_field = "depot__name"
    get_depot.short_description = "Delivery Site"

    def get_biofuel(self, obj):
        return obj.biofuel.code if obj.biofuel else ""

    get_biofuel.admin_order_field = "biofuel__code"
    get_biofuel.short_description = "Biofuel"

    def get_feedstock(self, obj):
        return obj.feedstock.code if obj.feedstock else ""

    get_feedstock.admin_order_field = "feedstock__code"
    get_feedstock.short_description = "Feedstock"

    def get_orig_volume(self, obj):
        return obj.parent_lot.volume if obj.parent_lot else obj.parent_transformation.volume_destination

    get_orig_volume.admin_order_field = "parent_lot__volume"
    get_orig_volume.short_description = "Initial Volume"


@admin.register(CarbureLotEvent)
class CarbureLotEventAdmin(admin.ModelAdmin):
    list_display = ["lot_id", "event_type", "event_dt", "user"]
    list_filter = ["event_type"]
    search_fields = ["lot__id"]


@admin.register(CarbureLotComment)
class CarbureLotCommentAdmin(admin.ModelAdmin):
    list_display = []


@admin.register(CarbureStockTransformation)
class CarbureStockTransformationAdmin(admin.ModelAdmin):
    list_display = [
        "transformation_type",
        "source_stock_id",
        "dest_stock_id",
        "entity",
        "transformation_dt",
    ]
    list_filter = ["transformation_type", "entity"]


@admin.register(CarbureNotification)
class CarbureNotificationAdmin(admin.ModelAdmin):
    list_display = ["dest", "datetime", "type", "acked", "send_by_email", "email_sent"]
    list_filter = ["acked", "send_by_email", "email_sent", "dest"]


@admin.register(GenericCertificate)
class GenericCertificateAdmin(admin.ModelAdmin):
    list_display = [
        "certificate_id",
        "certificate_type",
        "certificate_holder",
        "valid_from",
        "valid_until",
    ]
    list_filter = ["certificate_type"]
    search_fields = ("certificate_holder", "certificate_id")


@admin.register(EntityCertificate)
class EntityCertificateAdmin(admin.ModelAdmin):
    list_display = [
        "entity",
        "get_certificate_id",
        "get_certificate_type",
        "get_certificate_holder",
        "get_valid_from",
        "get_valid_until",
        "checked_by_admin",
        "rejected_by_admin",
    ]
    list_filter = [
        "certificate__certificate_type",
        "checked_by_admin",
        "rejected_by_admin",
    ]
    search_fields = (
        "entity__name",
        "certificate__certificate_holder",
        "certificate__certificate_id",
    )
    raw_id_fields = ["certificate", "entity"]

    def get_certificate_id(self, obj):
        return obj.certificate.certificate_id

    get_certificate_id.admin_order_field = "certificate__certificate_id"
    get_certificate_id.short_description = "Certificate ID"

    def get_certificate_type(self, obj):
        return obj.certificate.certificate_type

    get_certificate_type.admin_order_field = "certificate__certificate_type"
    get_certificate_type.short_description = "Certificate Type"

    def get_certificate_holder(self, obj):
        return obj.certificate.certificate_holder

    get_certificate_holder.admin_order_field = "certificate__certificate_holder"
    get_certificate_holder.short_description = "Certificate Holder"

    def get_valid_from(self, obj):
        return obj.certificate.valid_from

    get_valid_from.admin_order_field = "certificate__valid_from"
    get_valid_from.short_description = "Valid From"

    def get_valid_until(self, obj):
        return obj.certificate.valid_until

    get_valid_until.admin_order_field = "certificate__valid_until"
    get_valid_until.short_description = "Valid Until"
