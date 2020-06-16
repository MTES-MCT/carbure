# Generated by Django 3.0.7 on 2020-06-16 15:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0057_auto_20200616_1558'),
    ]

    operations = [
        migrations.CreateModel(
            name='TransactionComment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comment', models.TextField()),
                ('entity', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.Entity')),
                ('tx', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.LotTransaction')),
            ],
            options={
                'verbose_name': 'TransactionComment',
                'verbose_name_plural': 'TransactionComments',
                'db_table': 'tx_comments',
            },
        ),
    ]
