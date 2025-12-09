from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("elec", "0060_elecmeterreadingvirtual_and_more"),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
                UPDATE elec_meter_reading emr
                INNER JOIN year_config yc ON yc.year = YEAR(emr.reading_date)
                SET emr.enr_ratio = yc.renewable_share / 100;
            """,
            reverse_sql="""
                UPDATE elec_meter_reading
                SET enr_ratio = NULL;
            """,
        )
    ]
