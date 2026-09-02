from django.contrib import admin

from traceability.models import Action, ActionStatus, Material


class ActionStatusInline(admin.TabularInline):
    model = ActionStatus
    extra = 0
    readonly_fields = ("created_at",)
    ordering = ("created_at", "id")


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ("id", "code", "name")
    search_fields = ("code", "name")


@admin.register(Action)
class ActionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "pos_id",
        "holder",
        "industry",
        "type",
        "material",
        "quantity",
        "site",
        "shipping_date",
        "working_date",
        "latest_status",
    )
    list_filter = ("industry", "type", "shipping_method", "working_date")
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

    @admin.display(description="Statut", ordering="status")
    def latest_status(self, obj):
        return obj.status
