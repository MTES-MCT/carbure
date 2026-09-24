from django.contrib import admin, messages

from core.models import StoredFile
from traceability.exceptions import NoEligibleActionError
from traceability.models import Action, ActionStatus, Material
from traceability.services.refuse import refuse
from traceability.services.valorize import valorize


class ActionStatusInline(admin.TabularInline):
    model = ActionStatus
    extra = 0
    readonly_fields = ("created_at",)
    ordering = ("created_at", "id")


class StoredFileActionInline(admin.TabularInline):
    model = Action
    fk_name = "file"
    extra = 0
    show_change_link = True
    fields = ("pos_id", "industry", "type", "holder", "quantity", "working_date")
    readonly_fields = fields
    ordering = ("pos_id",)

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class LatestStatusFilter(admin.SimpleListFilter):
    title = "Statut"
    parameter_name = "status"

    def lookups(self, request, model_admin):
        return ActionStatus.STATUSES

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(status=self.value())
        return queryset


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ("id", "code", "name")
    search_fields = ("code", "name")


@admin.action(description="Valider les actions sélectionnées et créer les certificats")
def valorize_actions_into_certificates(modeladmin, request, queryset):
    try:
        created = valorize(queryset)
    except NoEligibleActionError:
        modeladmin.message_user(request, "Aucune action éligible à valoriser", messages.WARNING)
        return
    modeladmin.message_user(request, f"{len(created)} certificat(s) créé(s).")


@admin.action(description="Refuser les actions sélectionnées")
def refuse_selected_actions(modeladmin, request, queryset):
    try:
        refused = refuse(queryset)
    except NoEligibleActionError:
        modeladmin.message_user(request, "Aucune action éligible à refuser", messages.WARNING)
        return
    modeladmin.message_user(request, f"{len(refused)} action(s) refusée(s).")


@admin.register(Action)
class ActionAdmin(admin.ModelAdmin):
    list_display = (
        "pos_id",
        "industry",
        "type",
        "latest_status",
        "holder",
        "material__name",
        "quantity",
        "site",
        "shipping_date",
        "working_date",
    )
    list_filter = (
        "industry",
        "type",
        LatestStatusFilter,
        "material__name",
        "shipping_method",
    )
    search_fields = (
        "pos_id",
        "holder__name",
        "material__code",
        "material__name",
        "site__name",
        "certificate__certificate_id",
    )
    raw_id_fields = ("parent", "holder", "material", "site", "certificate", "file")
    list_select_related = ("holder", "material", "site", "certificate")
    date_hierarchy = "working_date"
    inlines = (ActionStatusInline,)
    actions = [valorize_actions_into_certificates, refuse_selected_actions]

    @admin.display(description="Statut", ordering="status")
    def latest_status(self, obj):
        return obj.status


@admin.register(StoredFile)
class StoredFileAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "entity", "user", "created_at")
    fields = ("entity", "user", "name", "url", "created_at")
    search_fields = ("name", "entity__name", "user__email", "actions__pos_id")
    raw_id_fields = ("user", "entity")
    readonly_fields = ("created_at",)
    list_select_related = ("entity", "user")
    inlines = (StoredFileActionInline,)
