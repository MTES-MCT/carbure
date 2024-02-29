from django.contrib import admin

from elec.models import (
    ElecProvisionCertificate,
    ElecTransferCertificate,
    ElecChargePoint,
    ElecChargePointApplication,
    ElecMeterReading,
    ElecMeterReadingApplication,
)


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
        "mid_id",
        "measure_date",
        "measure_energy",
        "is_article_2",
        "measure_reference_point_id",
        "station_name",
        "station_id",
        "nominal_power",
        "cpo_name",
        "cpo_siren",
        "latitude",
        "longitude",
    ]
    list_filter = [
        "current_type",
        "cpo",
        "is_article_2",
        "station_name",
        "station_id",
        "cpo_name",
        "cpo_siren",
    ]
    search_fields = [
        "id",
        "charge_point_id",
        "station_id",
        "station_name",
        "cpo__name",
        "mid_id",
    ]


@admin.register(ElecMeterReadingApplication)
class ElecMeterReadingApplicationAdmin(admin.ModelAdmin):
    list_display = [
        "status",
        "created_at",
        "cpo",
        "quarter",
        "year",
    ]
    list_filter = [
        "status",
        "cpo",
        "quarter",
        "year",
    ]


@admin.register(ElecMeterReading)
class ElecMeterReadingAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "cpo",
        "charge_point_id",
        "extracted_energy",
    ]
    list_filter = [
        "cpo",
    ]
    search_fields = [
        "id",
        "charge_point_id",
        "cpo__name",
        "charge_point__station_id",
        "charge_point__station_name",
    ]
