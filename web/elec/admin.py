from django.contrib import admin

from elec.models import (
    ElecAuditChargePoint,
    ElecAuditSample,
    ElecChargePoint,
    ElecChargePointApplication,
    ElecMeter,
    ElecMeterReading,
    ElecMeterReadingApplication,
    ElecProvisionCertificate,
    ElecProvisionCertificateQualicharge,
    ElecTransferCertificate,
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
        "current_meter__mid_certificate",
    ]
    autocomplete_fields = ["current_meter"]


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
        "meter__charge_point__id",
        "cpo__name",
        "meter__charge_point__station_id",
        "meter__charge_point__station_name",
    ]
    autocomplete_fields = ["meter"]


@admin.register(ElecAuditSample)
class ElecAuditSampleAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "status",
    ]
    search_fields = [
        "id",
    ]


@admin.register(ElecAuditChargePoint)
class ElecAuditChargePointAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "charge_point",
        "meter_reading",
    ]

    search_fields = [
        "id",
    ]
    autocomplete_fields = [
        "charge_point",
        "meter_reading",
    ]


@admin.register(ElecMeter)
class ElecMeterAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "mid_certificate",
        "initial_index",
        "initial_index_date",
    ]

    search_fields = [
        "id",
        "mid_certificate",
        "charge_point__charge_point_id",
    ]
    list_filter = [
        "charge_point__cpo_name",
    ]
    autocomplete_fields = ["charge_point"]


@admin.register(ElecProvisionCertificateQualicharge)
class ElecProvisionCertificateQualichargeAdmin(admin.ModelAdmin):
    list_display = [
        "cpo",
        "year",
        "operating_unit",
        "station_id",
        "energy_amount",
        "validated_by",
    ]
    list_filter = [
        "validated_by",
    ]
    search_fields = [
        "cpo__name",
        "station_id",
        "operating_unit",
    ]
