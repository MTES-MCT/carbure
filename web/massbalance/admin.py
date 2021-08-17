from django.contrib import admin

from massbalance.models import OutTransaction, OutTransactionVolume

@admin.register(OutTransaction)
class OutTransactionAdmin(admin.ModelAdmin):
    list_display = ('vendor', 'dae', 'volume', 'carbure_client', 'unknown_client', 'carbure_delivery_site', 'unknown_delivery_site')
    list_filter = ('vendor', 'biofuel_category', )


@admin.register(OutTransactionVolume)
class OutTransactionVolumeAdmin(admin.ModelAdmin):
    list_display = ('get_vendor', 'get_out_transaction', 'related_stock_line', 'volume')

    def get_vendor(self):
        return self.out_transaction.vendor.name

    def get_out_transaction(self):
        return self.out_transaction.dae