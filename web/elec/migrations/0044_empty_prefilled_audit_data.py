# Generated by Django 5.0.6 on 2024-09-18 15:38

from django.db import migrations


def empty_prefilled_audit_data(apps, schema_editor):
    ElecAuditChargePoint = apps.get_model("elec", "ElecAuditChargePoint")
    charge_point_audits = ElecAuditChargePoint.objects.filter(audit_sample__status="IN_PROGRESS")
    charge_point_audits.update(is_auditable=None, observed_energy_reading=None, has_dedicated_pdl=None)


class Migration(migrations.Migration):
    dependencies = [
        ("elec", "0043_elecchargepoint_is_deleted"),
    ]

    operations = [
        migrations.RunPython(empty_prefilled_audit_data),
    ]