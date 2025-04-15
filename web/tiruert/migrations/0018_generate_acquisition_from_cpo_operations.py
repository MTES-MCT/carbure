# Generated by Django 5.0.6 on 2025-04-08 12:38

from django.db import migrations, transaction
from django.db.models import Sum


@transaction.atomic
def create_new_elec_operations(apps, schema_editor):
    Entity = apps.get_model("core", "Entity")
    ElecTransferCertificate = apps.get_model("elec", "ElecTransferCertificate")
    ElecOperation = apps.get_model("tiruert", "ElecOperation")

    operators = Entity.objects.filter(entity_type="Opérateur", has_elec=True, is_tiruert_liable=True)

    for operator in operators:
        all_cpo_elec_certs = ElecTransferCertificate.objects.filter(
            supplier__entity_type="Charge Point Operator",
            status="ACCEPTED",
            client_id=operator.pk,
        )

        all_elec_operations = ElecOperation.objects.filter(
            type="ACQUISITION_FROM_CPO",
            status="ACCEPTED",
            credited_entity_id=operator.pk,
        )

        total_cpo_elec_certs = all_cpo_elec_certs.aggregate(Sum("energy_amount")).get("energy_amount__sum") or 0  # in MWh
        total_elec_operations = all_elec_operations.aggregate(Sum("quantity")).get("quantity__sum") or 0  # in MJ

        diff = (total_cpo_elec_certs * 3600) - total_elec_operations

        if diff > 0:
            ElecOperation.objects.create(
                type="ACQUISITION_FROM_CPO",
                status="ACCEPTED",
                quantity=diff,
                credited_entity_id=operator.pk,
            )


class Migration(migrations.Migration):
    dependencies = [
        ("tiruert", "0017_elecoperation"),
    ]

    operations = [
        migrations.RunPython(create_new_elec_operations, reverse_code=migrations.RunPython.noop),
    ]
