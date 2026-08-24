from django.contrib import admin

from h2.models.h2_station import H2Station


@admin.register(H2Station)
class H2StationAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "distributed_pressure",
        # "get_owner",
        # "city",
        # "country",
        # "is_enabled",
    ]
    search_fields = ["name"]
    list_filter = ["country"]
