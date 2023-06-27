from django.contrib import admin

from elec.models.elec_provision_certificate import ElecProvisionCertificate


@admin.register(ElecProvisionCertificate)
class ElecProvisionCertificateAdmin(admin.ModelAdmin):
    list_display = (
        "entity",
        "quarter",
        "year",
        "operating_unit",
        "energy_amount",
        "remaining_energy_amount",
    )
    list_filter = (
        "entity",
        "quarter",
        "year",
        "operating_unit",
    )
