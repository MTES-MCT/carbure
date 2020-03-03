from django.contrib import admin

from producers.models import AttestationProducer, ProductionSite, ProducerCertificate


class AttestationProducerAdmin(admin.ModelAdmin):
    list_display = ('period', 'producer', 'deadline')
    search_fields = ('period', 'producer')
    list_filter = ('producer',)

admin.site.register(AttestationProducer, AttestationProducerAdmin)


class ProductionSiteAdmin(admin.ModelAdmin):
    list_display = ('name', 'identifiant', 'num_accise')
    search_fields = ('name', 'identifiant', 'num_accise', 'producer')
    list_filter = ('producer',)

admin.site.register(ProductionSite, ProductionSiteAdmin)


class ProducerCertificateAdmin(admin.ModelAdmin):
    list_display = ('producer', 'matiere_premiere', 'certificate', 'expiration')
    search_fields = ('producer', 'matiere_premiere', 'expiration')
    list_filter = ('producer',)

admin.site.register(ProducerCertificate, ProducerCertificateAdmin)