from django.db import migrations


def delete_legacy_ml_errors(apps, schema_editor):
    GenericError = apps.get_model("core", "GenericError")
    GenericError.objects.using(schema_editor.connection.alias).filter(
        error__in=[
            "EEC_ANORMAL_LOW",
            "EEC_ANORMAL_HIGH",
            "EP_ANORMAL_LOW",
            "EP_ANORMAL_HIGH",
            "ETD_ANORMAL_HIGH",
            "ETD_NO_EU_TOO_LOW",
            "ETD_EU_DEFAULT_VALUE",
            "ETD_HIGHER_THAN_DEFAULT",
        ],
    ).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0088_alter_externaladminrights_right"),
    ]

    operations = [
        migrations.RunPython(delete_legacy_ml_errors, migrations.RunPython.noop),
    ]
