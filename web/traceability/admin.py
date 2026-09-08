from django.contrib import admin, messages

from traceability.models import Action, ActionStatus, Material
from traceability.services.valorize import NoEligibleActionError, valorize


class ActionStatusInline(admin.TabularInline):
    model = ActionStatus
    extra = 0
    readonly_fields = ("created_at",)
    ordering = ("created_at", "id")


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
    raw_id_fields = ("parent", "holder", "material", "site", "certificate")
    list_select_related = ("holder", "material", "site", "certificate")
    date_hierarchy = "working_date"
    inlines = (ActionStatusInline,)
    actions = [valorize_actions_into_certificates]

    @admin.display(description="Statut", ordering="status")
    def latest_status(self, obj):
        return obj.status
