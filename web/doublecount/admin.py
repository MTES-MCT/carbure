# https://django-authtools.readthedocs.io/en/latest/how-to/invitation-email.html
# allows a manual user creation by an admin, without setting a password

from django.contrib import admin
from .models import DoubleCountingAgreement, DoubleCountingSourcing, DoubleCountingProduction

@admin.register(DoubleCountingAgreement)
class DoubleCountingAgreementAdmin(admin.ModelAdmin):
    list_display = ('producer', 'production_site', 'period_start', 'period_end', 'dgec_validated', 'dgddi_validated', 'dgpe_validated')
    list_filter = ('producer', 'period_start',)

@admin.register(DoubleCountingSourcing)
class DoubleCountingSourcingAdmin(admin.ModelAdmin):
    list_display = ('dca', 'year', 'feedstock', 'origin_country', 'metric_tonnes',)
    list_filter = ('year', 'feedstock', 'origin_country')

@admin.register(DoubleCountingProduction)
class DoubleCountingProductionAdmin(admin.ModelAdmin):
    list_display = ('dca', 'year', 'biofuel', 'feedstock', 'metric_tonnes')
    list_filter = ('year', 'biofuel', 'feedstock')
