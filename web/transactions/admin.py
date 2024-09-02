from django.contrib import admin

from .models import YearConfig


@admin.register(YearConfig)
class YearConfigAdmin(admin.ModelAdmin):
    list_display = ("year", "locked")
