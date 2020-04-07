from django.contrib import admin

from operators.models import OperatorDeclaration, AcceptedLot, OperatorDepot


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


class OperatorDepotAdmin(admin.ModelAdmin):
    list_display = ('operator', 'name', 'country')
    search_fields = ('operator', 'name', 'country')
    list_filter = ('operator',)

admin.site.register(OperatorDepot, OperatorDepotAdmin)