# Generated by Django 3.2.4 on 2021-06-23 15:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0168_auto_20210623_1556'),
    ]

    operations = [
        migrations.AddField(
            model_name='emailnotification',
            name='linked_declaration',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.sustainabilitydeclaration'),
        ),
    ]
