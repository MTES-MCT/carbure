# Generated by Django 3.0.7 on 2020-11-09 13:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0085_auto_20201109_1444'),
    ]

    operations = [
        migrations.CreateModel(
            name='DBSCertificateScope',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('certificate', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.DBSCertificate')),
                ('scope', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.DBSScope')),
            ],
            options={
                'verbose_name': '2BS Certificate Scope',
                'verbose_name_plural': '2BS Certificate Scopes',
                'db_table': 'dbs_certificates_scopes',
            },
        ),
    ]
