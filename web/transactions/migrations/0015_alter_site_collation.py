# Generated migration to improve site table collation for case-insensitive searches

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("transactions", "0014_delete_contenttoupdate"),
    ]

    operations = [
        migrations.RunSQL(
            sql=[
                # Change collation for entire sites table to case-insensitive, accent-insensitive
                "ALTER TABLE sites CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;",
            ],
            reverse_sql=[
                # Revert to original collation if needed
                "ALTER TABLE sites CONVERT TO CHARACTER SET utf8mb3 COLLATE utf8mb3_bin;",
            ],
        ),
    ]
