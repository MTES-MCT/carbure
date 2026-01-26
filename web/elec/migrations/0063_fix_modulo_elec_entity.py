from django.db import migrations

# Entity with name "Modulo (Mobilité durable locale)" has 2 elec_provision_certificate with source "MANUAL"
# and operating unit "FRS37" for quarter 1 and 2 of 2024.
# We need to change the source of these certificates to "METER_READINGS".


class Migration(migrations.Migration):
    dependencies = [
        ("elec", "0062_elec_meter_reading_virtual"),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
                UPDATE elec_provision_certificate
                INNER JOIN entities ON entities.id = elec_provision_certificate.cpo_id
                SET elec_provision_certificate.source = "METER_READINGS"
                WHERE entities.name = "Modulo (Mobilité durable locale)"
                AND elec_provision_certificate.operating_unit = "FRS37"
                AND elec_provision_certificate.year = 2024
                AND elec_provision_certificate.quarter IN (1, 2)
                AND elec_provision_certificate.source = "MANUAL";
            """,
            reverse_sql="""
                UPDATE elec_provision_certificate
                INNER JOIN entities ON entities.id = elec_provision_certificate.cpo_id
                SET elec_provision_certificate.source = "MANUAL"
                WHERE entities.name = "Modulo (Mobilité durable locale)"
                AND elec_provision_certificate.operating_unit = "FRS37"
                AND elec_provision_certificate.year = 2024
                AND elec_provision_certificate.quarter IN (1, 2)
                AND elec_provision_certificate.source = "METER_READINGS";
            """,
        )
    ]
