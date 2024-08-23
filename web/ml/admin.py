from django.contrib import admin

# Register your models here.
from ml.models import EECStats, EPStats, ETDStats


@admin.register(EECStats)
class EECStatsAdmin(admin.ModelAdmin):
    list_display = ('feedstock', 'origin', 'nb_lots', 'default_value', 'stddev', 'average')
    list_filter = ('feedstock', 'origin',)

@admin.register(EPStats)
class EPStatsAdmin(admin.ModelAdmin):
    list_display = ('feedstock', 'biofuel', 'nb_lots', 'default_value_min_ep', 'default_value_max_ep', 'stddev', 'average')
    list_filter = ('feedstock', 'biofuel',)

@admin.register(ETDStats)
class ETDStatsAdmin(admin.ModelAdmin):
    list_display = ('feedstock', 'default_value')
