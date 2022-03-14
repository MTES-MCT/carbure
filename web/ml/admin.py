from django.contrib import admin

# Register your models here.
from ml.models import EECStats, EPStats, ETDStats

@admin.register(EECStats)
class EECStatsAdmin(admin.ModelAdmin):
    list_display = ('feedstock', 'origin', 'nb_lots', 'default_value', 'stddev', 'average')

@admin.register(EPStats)
class EPStatsAdmin(admin.ModelAdmin):
    list_display = ('feedstock', 'biofuel', 'nb_lots', 'default_value_min_eec', 'default_value_max_eec', 'stddev', 'average')
    
@admin.register(ETDStats)
class ETDStatsAdmin(admin.ModelAdmin):
    list_display = ('feedstock', 'default_value')
