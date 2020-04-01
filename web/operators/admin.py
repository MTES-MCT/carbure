from django.contrib import admin

from operators.models import OperatorDeclaration, AcceptedLot


class OperatorDeclarationAdmin(admin.ModelAdmin):
    list_display = ('period', 'operator', 'deadline')
    search_fields = ('period', 'operator')
    list_filter = ('operator',)

admin.site.register(OperatorDeclaration, OperatorDeclarationAdmin)

class AcceptedLotAdmin(admin.ModelAdmin):
    list_display = ('operator', 'declaration', 'lot')
    search_fields = ('operator', 'declaration', 'lot')
    list_filter = ('operator',)

admin.site.register(AcceptedLot, AcceptedLotAdmin)

