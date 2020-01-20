from django.contrib import admin

from core.models import *

class EntityAdmin(admin.ModelAdmin):
    list_display = ('entity_type', 'name', 'parent_entity')
    search_fields = ('entity_type', 'name')
    list_filter = ('entity_type',)
admin.site.register(Entity, EntityAdmin)

class UserAdmin(admin.ModelAdmin):
    list_display = ('user', 'entity')
    search_fields = ('user', 'entity')
admin.site.register(PlatformUser, UserAdmin)



