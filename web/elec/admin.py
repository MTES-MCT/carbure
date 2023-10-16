from django.contrib import admin

from elec.models import ElecProvisionCertificate, ElecTransferCertificate


@admin.register(ElecProvisionCertificate)
class ElecProvisionCertificateAdmin(admin.ModelAdmin):
    list_display = (
        "cpo",
        "quarter",
        "year",
        "operating_unit",
        "energy_amount",
        "remaining_energy_amount",
    )
    list_filter = (
        "cpo",
        "quarter",
        "year",
        "operating_unit",
    )


@admin.register(ElecTransferCertificate)
class ElecTransferCertificateAdmin(admin.ModelAdmin):
    list_display = (
        "certificate_id",
        "status",
        "supplier",
        "client",
        "transfer_date",
        "energy_amount",
    )
    list_filter = (
        "status",
        "supplier",
        "client",
    )
