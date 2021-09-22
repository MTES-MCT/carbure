# Generated by Django 3.2.4 on 2021-09-22 12:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0184_auto_20210827_1026'),
    ]

    operations = [
        migrations.AlterField(
            model_name='entity',
            name='entity_type',
            field=models.CharField(choices=[('Producteur', 'Producteur'), ('Opérateur', 'Opérateur'), ('Administration', 'Administration'), ('Trader', 'Trader'), ('Auditor', 'Auditeur'), ('Administration Externe', 'Administration Externe'), ('Unknown', 'Unknown')], default='Unknown', max_length=64),
        ),
        migrations.CreateModel(
            name='ExternalAdminRights',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('right', models.CharField(choices=[('DCA', 'DCA'), ('AGRIMER', 'AGRIMER'), ('TIRIB', 'TIRIB')], default='', max_length=32)),
                ('entity', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.entity')),
            ],
            options={
                'verbose_name': 'External Admin Right',
                'verbose_name_plural': 'External Admin Rights',
                'db_table': 'ext_admin_rights',
            },
        ),
    ]
