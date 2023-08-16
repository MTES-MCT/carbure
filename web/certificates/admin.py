from django.contrib import admin

from certificates.models import ProductionSiteCertificate
from certificates.models import DoubleCountingRegistration, DoubleCountingRegistrationInputOutput


class ProductionSiteCertificateAdmin(admin.ModelAdmin):
    list_display = ("production_site", "get_certificate_type", "certificate")
    search_fields = ("production_site__name",)

    def get_certificate_type(self, obj):
        return obj.certificate.certificate.certificate_type

    get_certificate_type.short_description = "Type"


admin.site.register(ProductionSiteCertificate, ProductionSiteCertificateAdmin)


@admin.register(DoubleCountingRegistration)
class DoubleCountingRegistrationAdmin(admin.ModelAdmin):
    list_display = ("certificate_id", "production_site", "valid_from", "valid_until", "certificate_holder")
    search_fields = (
        "certificate_id",
        "certificate_holder",
    )


@admin.register(DoubleCountingRegistrationInputOutput)
class DoubleCountingRegistrationAdmin(admin.ModelAdmin):
    list_display = ("get_certid", "get_holder", "biofuel", "feedstock")
    search_fields = (
        "certificate__certificate_id",
        "certificate__certificate_holder",
    )

    def get_certid(self, obj):
        return obj.certificate.certificate_id

    get_certid.short_description = "ID"

    def get_holder(self, obj):
        return obj.certificate.certificate_holder

    get_holder.short_description = "Holder"
