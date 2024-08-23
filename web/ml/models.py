from django.db import models

from core.models import Biocarburant, MatierePremiere, Pays


class EECStats(models.Model):
    feedstock = models.ForeignKey(MatierePremiere, null=False, blank=False, on_delete=models.CASCADE)
    origin = models.ForeignKey(Pays, null=False, blank=False, on_delete=models.CASCADE)
    nb_lots = models.IntegerField(null=False, blank=False)
    default_value = models.FloatField(null=False, blank=False, default=0.0)
    stddev = models.FloatField(null=False, blank=False)
    average = models.FloatField(null=False, blank=False)

    class Meta:
        db_table = "ml_eec_stats"
        verbose_name = "ML EEC Stat"
        verbose_name_plural = "ML EEC Stats"


class EPStats(models.Model):
    feedstock = models.ForeignKey(MatierePremiere, null=False, blank=False, on_delete=models.CASCADE)
    biofuel = models.ForeignKey(Biocarburant, null=False, blank=False, on_delete=models.CASCADE)
    nb_lots = models.IntegerField(null=False, blank=False)
    default_value_min_ep = models.FloatField(null=False, blank=False, default=0.0)
    default_value_max_ep = models.FloatField(null=False, blank=False, default=0.0)
    stddev = models.FloatField(null=False, blank=False)
    average = models.FloatField(null=False, blank=False)

    class Meta:
        db_table = "ml_ep_stats"
        verbose_name = "ML EP Stat"
        verbose_name_plural = "ML EP Stats"


class ETDStats(models.Model):
    feedstock = models.ForeignKey(MatierePremiere, null=False, blank=False, on_delete=models.CASCADE)
    default_value = models.FloatField(null=False, blank=False, default=0.0)

    class Meta:
        db_table = "ml_etd_stats"
        verbose_name = "ML ETD Stat"
        verbose_name_plural = "ML ETD Stats"
