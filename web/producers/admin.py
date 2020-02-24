from django.contrib import admin

from producers.models import AttestationProducer


class AttestationProducerAdmin(admin.ModelAdmin):
    list_display = ('period', 'producer', 'deadline')
    search_fields = ('period', 'producer')
    list_filter = ('producer',)

admin.site.register(AttestationProducer, AttestationProducerAdmin)
