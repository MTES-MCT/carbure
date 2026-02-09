from django.db import models


class ElecMeterReadingVirtual(models.Model):
    reading_id = models.IntegerField(primary_key=True)
    application = models.ForeignKey(
        "elec.ElecMeterReadingApplication",
        on_delete=models.DO_NOTHING,
        db_column="application_id",
        db_constraint=False,
        related_name="elec_meter_reading_virtual_set",
    )
    meter = models.ForeignKey(
        "elec.ElecMeter",
        on_delete=models.DO_NOTHING,
        db_column="meter_id",
        db_constraint=False,
        related_name="+",
    )
    cpo = models.ForeignKey(
        "core.Entity",
        on_delete=models.DO_NOTHING,
        db_column="cpo_id",
        db_constraint=False,
        related_name="+",
    )
    charge_point = models.ForeignKey(
        "elec.ElecChargePoint",
        on_delete=models.DO_NOTHING,
        db_column="charge_point_id",
        db_constraint=False,
        related_name="+",
    )
    current_index_date = models.DateField()
    prev_index_date = models.DateField()
    current_index = models.FloatField()
    prev_index = models.FloatField()
    enr_ratio = models.FloatField()

    class Meta:
        managed = False
        db_table = "elec_meter_reading_virtual"

    @property
    def renewable_energy(self):
        if self.current_index is None or self.prev_index is None or self.enr_ratio is None:
            return 0
        return (self.current_index - self.prev_index) * float(self.enr_ratio)
