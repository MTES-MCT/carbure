# Generated by Django 3.0.7 on 2020-09-07 12:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0070_auto_20200907_1311'),
    ]

    operations = [
        migrations.CreateModel(
            name='LotValidationError',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lot', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.LotV2')),
                ('rule', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.CheckRule')),
            ],
            options={
                'verbose_name': 'LotValidationError',
                'verbose_name_plural': 'LotValidationErrors',
                'db_table': 'validation_errors',
            },
        ),
    ]
