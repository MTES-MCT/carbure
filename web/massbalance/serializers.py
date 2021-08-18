from rest_framework import serializers

from massbalance.models import OutTransaction


class OutTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = OutTransaction
        fields = ['id', 'vendor', 'dae', 'carbure_storage_site', 
                'client_is_in_carbure', 'carbure_client', 'unknown_client',
                'dispatch_date', 'delivery_date',
                'delivery_site_is_in_carbure', 'carbure_delivery_site', 'unknown_delivery_site', 'unknown_delivery_site_country',
                'volume', 'biofuel_category', 
                'dt_created', 'dt_updated', 'creation_method', 'created_by_entity', 'created_by_user',
                'is_sent']
