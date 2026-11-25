from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("traceability", "0026_alter_action_type"),
        ("traceability", "0029_materialtag_unique"),
    ]

    operations = [
        migrations.AddField(
            model_name="material",
            name="is_active",
            field=models.BooleanField(default=True, verbose_name="Active"),
        ),
        migrations.AlterField(
            model_name="material",
            name="code",
            field=models.CharField(max_length=16, unique=True, verbose_name="Code"),
        ),
        migrations.AlterField(
            model_name="material",
            name="name",
            field=models.CharField(max_length=128, unique=True, verbose_name="Nom"),
        ),
        migrations.AlterField(
            model_name="material",
            name="description",
            field=models.CharField(blank=True, default="", max_length=512, verbose_name="Description"),
        ),
        migrations.AlterField(
            model_name="material",
            name="classification",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=models.SET_NULL,
                to="feedstocks.classification",
                verbose_name="Classification",
            ),
        ),
    ]
