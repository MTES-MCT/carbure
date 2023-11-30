from django.contrib import admin

from elec.models import ElecProvisionCertificate, ElecTransferCertificate, ElecChargePoint, ElecChargePointApplication


@admin.register(ElecProvisionCertificate)
class ElecProvisionCertificateAdmin(admin.ModelAdmin):
    list_display = [
        "cpo",
        "quarter",
        "year",
        "operating_unit",
        "energy_amount",
        "remaining_energy_amount",
    ]
    list_filter = [
        "cpo",
        "quarter",
        "year",
        "operating_unit",
    ]


@admin.register(ElecTransferCertificate)
class ElecTransferCertificateAdmin(admin.ModelAdmin):
    list_display = [
        "certificate_id",
        "status",
        "supplier",
        "client",
        "transfer_date",
        "energy_amount",
    ]
    list_filter = [
        "status",
        "supplier",
        "client",
    ]


@admin.register(ElecChargePointApplication)
class ElecChargePointApplicationAdmin(admin.ModelAdmin):
    list_display = [
        "status",
        "created_at",
        "cpo",
    ]
    list_filter = [
        "status",
        "cpo",
    ]


@admin.register(ElecChargePoint)
class ElecChargePointAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "cpo",
        "charge_point_id",
        "current_type",
        "installation_date",
        "lne_id",
        "measure_date",
        "measure_energy",
        "is_article_2",
        "is_auto_consumption",
        "is_article_4",
        "measure_reference_point_id",
        "station_name",
        "station_id",
    ]
    list_filter = [
        "application",
        "current_type",
        "cpo",
        "is_article_2",
        "is_auto_consumption",
        "is_article_4",
        "station_name",
        "station_id",
    ]
