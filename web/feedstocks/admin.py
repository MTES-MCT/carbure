from django.contrib import admin

from feedstocks.models import Classification, Feedstock


@admin.register(Feedstock)
class FeedstockAdmin(admin.ModelAdmin):
    search_fields = ["display_name", "classification", "matiere_premiere__name"]
    list_display = ["name", "matiere_premiere", "classification"]


@admin.register(Classification)
class ClassificationAdmin(admin.ModelAdmin):
    search_fields = ["group", "category", "subcategory"]
    list_display = ["id", "group", "category", "subcategory"]
