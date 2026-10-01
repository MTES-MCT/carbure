from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("transactions", "0021_alter_site_site_type"),
        ("biomethane", "0056_merge_20260824_1016"),
    ]

    operations = [
        migrations.RunSQL(
            sql=[
                "ALTER TABLE sites_depots CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;",
                "ALTER TABLE sites_productionsites CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;",
                "ALTER TABLE sites_airports CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;",
                "ALTER TABLE sites_biomethaneproductionunits CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;",
            ],
            reverse_sql=[
                "ALTER TABLE sites_depots CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;",
                "ALTER TABLE sites_productionsites CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;",
                "ALTER TABLE sites_airports CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;",
                "ALTER TABLE sites_biomethaneproductionunits CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;",
            ],
        ),
    ]
