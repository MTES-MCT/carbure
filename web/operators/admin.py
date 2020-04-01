from django.contrib import admin

from operators.models import OperatorDeclaration


class OperatorDeclarationAdmin(admin.ModelAdmin):
    list_display = ('period', 'operator', 'deadline')
    search_fields = ('period', 'operator')
    list_filter = ('operator',)

admin.site.register(OperatorDeclaration, OperatorDeclarationAdmin)

