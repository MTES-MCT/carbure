from django.contrib import admin

from producers.models import ProductionSite, ProducerCertificate, ProductionSiteInput, ProductionSiteOutput


class ProductionSiteAdmin(admin.ModelAdmin):
    list_display = ('name', 'producer', 'country', 'date_mise_en_service', 'ges_option')
    search_fields = ('name', 'producer', 'country', 'ges_option')
    list_filter = ('producer', 'country', 'ges_option', 'eligible_dc')

admin.site.register(ProductionSite, ProductionSiteAdmin)


class ProducerCertificateAdmin(admin.ModelAdmin):
    list_display = ('producer', 'production_site', 'certificate', 'expiration', 'certificate_id')
    search_fields = ('producer','production_site', 'expiration', 'certificate_id')
    list_filter = ('producer', 'status')

admin.site.register(ProducerCertificate, ProducerCertificateAdmin)


class ProductionSiteInputAdmin(admin.ModelAdmin):
    list_display = ('production_site', 'matiere_premiere')
    search_fields = ('production_site', 'matiere_premiere')
    list_filter = ('matiere_premiere',)

admin.site.register(ProductionSiteInput, ProductionSiteInputAdmin)


class ProductionSiteOutputAdmin(admin.ModelAdmin):
    list_display = ('production_site', 'biocarburant',)
    search_fields = ('production_site', 'biocarburant',)
    list_filter = ('biocarburant',)

admin.site.register(ProductionSiteOutput, ProductionSiteOutputAdmin)

