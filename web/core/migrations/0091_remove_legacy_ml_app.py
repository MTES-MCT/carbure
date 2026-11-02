from django.db import migrations


def delete_legacy_content_types(apps, schema_editor):
    ContentType = apps.get_model("contenttypes", "ContentType")
    ContentType.objects.using(schema_editor.connection.alias).filter(app_label="ml").delete()


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ("core", "0090_remove_legacy_ml_lot_fields"),
        ("contenttypes", "0002_remove_content_type_name"),
        ("auth", "0012_alter_user_first_name_max_length"),
        ("admin", "0003_logentry_add_action_flag_choices"),
        ("entity", "0001_add_entityscope"),
    ]

    operations = [
        # The app is no longer installed, so its tables are absent on fresh installs.
        migrations.RunSQL("DROP TABLE IF EXISTS ml_eec_stats"),
        migrations.RunSQL("DROP TABLE IF EXISTS ml_ep_stats"),
        migrations.RunSQL("DROP TABLE IF EXISTS ml_etd_stats"),
        migrations.RunPython(delete_legacy_content_types, migrations.RunPython.noop),
    ]
