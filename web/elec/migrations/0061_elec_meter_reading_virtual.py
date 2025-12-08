from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("elec", "0060_elecmeterreadingvirtual_and_more"),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
                CREATE OR REPLACE VIEW elec_meter_reading_virtual AS
                SELECT
                    emr.id AS reading_id,
                    emr.application_id,
                    emr.cpo_id,
                    ecp.id AS charge_point_id,
                    emr.meter_id,
                    emr.reading_date AS current_index_date,
                    COALESCE(
                        (
                            SELECT emr_prev.reading_date
                            FROM elec_meter_reading emr_prev
                            WHERE emr_prev.meter_id = emr.meter_id
                            AND emr_prev.id < emr.id
                            ORDER BY emr_prev.id DESC
                            LIMIT 1
                        ),
                        em.initial_index_date
                    ) AS prev_index_date,
                    emr.extracted_energy AS current_index,

                    COALESCE(
                        (
                            SELECT emr_prev.extracted_energy
                            FROM elec_meter_reading emr_prev
                            WHERE emr_prev.meter_id = emr.meter_id
                            AND emr_prev.id < emr.id
                            ORDER BY emr_prev.id DESC
                            LIMIT 1
                        ),
                        em.initial_index
                    ) AS prev_index,

                    (SELECT renewable_share / 100 FROM year_config WHERE year=emra.year) as enr_ratio

                FROM elec_meter_reading emr
                INNER JOIN elec_meter em ON em.id = emr.meter_id
                INNER JOIN elec_charge_point ecp ON ecp.id = em.charge_point_id
                WHERE
                    ecp.is_deleted = FALSE
                    AND ecp.is_article_2 = FALSE

                ORDER BY
                    emr.meter_id,
                    emr.reading_date;
            """,
            reverse_sql="""
                DROP VIEW IF EXISTS elec_meter_reading_virtual;
            """,
        )
    ]
