from django.contrib import admin

from producers.models import AttestationProducer, ProductionSite


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
