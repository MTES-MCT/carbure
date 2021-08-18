from django.db import models
from django.contrib.auth import get_user_model
usermodel = get_user_model()

from core.models import Entity, Depot, LotTransaction, Pays

class OutTransaction(models.Model):
    ETHANOL = 'ETHANOL'
    BIODIESEL = 'BIODIESEL'
    OTHER = 'OTHER'
    BIOFUEL_CATEGORIES = ((ETHANOL, ETHANOL), (BIODIESEL, BIODIESEL), (OTHER, OTHER))

    USER = 'USER'
    AUTO = 'AUTO'
    UNKNOWN = 'UNKNOWN'
    CREATION_METHOD_CHOICES = ((USER, USER), (AUTO, AUTO), (UNKNOWN, UNKNOWN))

    # source data
    vendor = models.ForeignKey(Entity, blank=False, null=False, on_delete=models.CASCADE, related_name='mb_pending_tx_vendor')
    dae = models.CharField(max_length=128, blank=True, default='')
    carbure_storage_site = models.ForeignKey(Depot, null=True, blank=True, on_delete=models.SET_NULL, related_name='mb_pending_tx_depot_source')

    # delivery
    client_is_in_carbure = models.BooleanField(default=True)
    carbure_client = models.ForeignKey(Entity, null=True, blank=True, on_delete=models.SET_NULL, related_name='mb_pending_tx_client')
    unknown_client = models.CharField(max_length=64, blank=True, default='')
    dispatch_date = models.DateField(blank=True, null=True)
    delivery_date = models.DateField(blank=True, null=True)
    delivery_site_is_in_carbure = models.BooleanField(default=True)
    carbure_delivery_site = models.ForeignKey(Depot, null=True, blank=True, on_delete=models.SET_NULL, related_name='mb_pending_tx_destination_depot')
    unknown_delivery_site = models.CharField(max_length=64, blank=True, default='')
    unknown_delivery_site_country = models.ForeignKey(Pays, null=True, blank=True, on_delete=models.SET_NULL)
    volume = models.FloatField(default=0.0)
    biofuel_category = models.CharField(max_length=32, choices=BIOFUEL_CATEGORIES, default=OTHER)

    # other
    dt_created = models.DateTimeField(auto_now_add=True)
    dt_updated = models.DateTimeField(auto_now=True)
    creation_method = models.CharField(max_length=32, choices=CREATION_METHOD_CHOICES, default='UNKNOWN')
    created_by = models.ForeignKey(usermodel, null=True, blank=True, on_delete=models.SET_NULL)

    is_sent = models.BooleanField(default=False)

    class Meta:
        db_table = 'massbalance_out_transactions'
        verbose_name = 'DAE à remplir'
        verbose_name_plural = 'DAE à remplir'
        indexes = [
            models.Index(fields=["vendor"]),
            models.Index(fields=["biofuel_category"]),
        ]


class OutTransactionVolume(models.Model):
    out_transaction = models.ForeignKey(OutTransaction, null=False, blank=False, on_delete=models.CASCADE)
    related_stock_line = models.ForeignKey(LotTransaction, null=False, blank=False, on_delete=models.CASCADE)
    volume = models.FloatField(default=0.0)

    class Meta:
        db_table = 'massbalance_out_transactions_lines'
        verbose_name = 'DAE - Ligne'
        verbose_name_plural = 'DAE - Lignes'
        indexes = [
            models.Index(fields=["out_transaction"]),
        ]
