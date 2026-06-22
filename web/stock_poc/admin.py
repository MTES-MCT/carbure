from django.contrib import admin

from stock_poc.models import Action


@admin.register(Action)
class ActionAdmin(admin.ModelAdmin):
    list_display = ["id", "type", "status", "quantity", "owner", "parent", "created_at"]
    list_filter = ["type", "status"]
    search_fields = ["owner__name"]
    raw_id_fields = ["owner", "parent"]
