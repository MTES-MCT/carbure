from django.db import migrations


def delete_obsolete_errors(apps, schema_editor):
    GenericError = apps.get_model("core", "GenericError")
    GenericError.objects.using(schema_editor.connection.alias).filter(
        error__in=["VOLUME_FAIBLE", "DEPOT_NOT_CONFIGURED"],
    ).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0089_auto_20261029_1751"),
    ]

    operations = [
        migrations.RunPython(delete_obsolete_errors, migrations.RunPython.noop),
    ]
