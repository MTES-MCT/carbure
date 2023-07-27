# https://django-authtools.readthedocs.io/en/latest/how-to/invitation-email.html
# allows a manual user creation by an admin, without setting a password

from django.contrib import admin
from .models import DoubleCountingApplication, DoubleCountingDocFile, DoubleCountingSourcing, DoubleCountingProduction


@admin.register(DoubleCountingApplication)
class DoubleCountingApplicationAdmin(admin.ModelAdmin):
    list_display = (
        "producer",
        "production_site",
        "period_start",
        "period_end",
        "dgec_validated",
        "dgddi_validated",
        "dgpe_validated",
    )
    list_filter = (
        "producer",
        "period_start",
    )


@admin.register(DoubleCountingSourcing)
class DoubleCountingSourcingAdmin(admin.ModelAdmin):
    list_display = (
        "dca",
        "year",
        "feedstock",
        "origin_country",
        "metric_tonnes",
    )
    list_filter = ("year", "feedstock", "origin_country")


@admin.register(DoubleCountingProduction)
class DoubleCountingProductionAdmin(admin.ModelAdmin):
    list_display = (
        "dca",
        "year",
        "biofuel",
        "feedstock",
        "max_production_capacity",
        "estimated_production",
        "requested_quota",
        "approved_quota",
    )
    list_filter = ("year", "biofuel", "feedstock")


@admin.register(DoubleCountingDocFile)
class DoubleCountingDocFileAdmin(admin.ModelAdmin):
    list_display = ("dca", "url", "file_name")
