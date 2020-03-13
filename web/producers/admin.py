from django.contrib import admin

from producers.models import AttestationProducer, ProductionSite, ProducerCertificate, ProductionSiteInput, ProductionSiteOutput


class AttestationProducerAdmin(admin.ModelAdmin):
    list_display = ('period', 'producer', 'deadline')
    search_fields = ('period', 'producer')
    list_filter = ('producer',)

admin.site.register(AttestationProducer, AttestationProducerAdmin)


class ProductionSiteAdmin(admin.ModelAdmin):
    list_display = ('name', 'producer', 'country', 'date_mise_en_service', 'ges_option')
    search_fields = ('name', 'producer', 'country', 'ges_option')
    list_filter = ('producer', 'country', 'ges_option')

admin.site.register(ProductionSite, ProductionSiteAdmin)


class ProducerCertificateAdmin(admin.ModelAdmin):
    list_display = ('producer', 'production_site', 'certificate', 'expiration', 'certificate_id')
    search_fields = ('producer','production_site', 'expiration', 'certificate_id')
    list_filter = ('producer', 'status')

admin.site.register(ProducerCertificate, ProducerCertificateAdmin)


class ProductionSiteInputAdmin(admin.ModelAdmin):
    list_display = ('production_site', 'matiere_premiere', 'eligible_double_comptage',)
    search_fields = ('production_site', 'matiere_premiere', 'eligible_double_comptage')
    list_filter = ('matiere_premiere', 'eligible_double_comptage')

admin.site.register(ProductionSiteInput, ProductionSiteInputAdmin)


class ProductionSiteOutputAdmin(admin.ModelAdmin):
    list_display = ('production_site', 'biocarburant',)
    search_fields = ('production_site', 'biocarburant',)
    list_filter = ('biocarburant',)

admin.site.register(ProductionSiteOutput, ProductionSiteOutputAdmin)

