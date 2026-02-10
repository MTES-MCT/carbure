from django.contrib import admin

from feedstocks.models import Classification


@admin.register(Classification)
class ClassificationAdmin(admin.ModelAdmin):
    search_fields = ["group", "category", "subcategory"]
    list_display = ["id", "group", "category", "subcategory"]
