from django.contrib import admin
from .models import LockedYear

@admin.register(LockedYear)
class LockedYearAdmin(admin.ModelAdmin):
    list_display = ('year', 'locked')
