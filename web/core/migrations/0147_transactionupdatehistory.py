# Generated by Django 3.2 on 2021-05-20 10:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0146_genericerror_fields'),
    ]

    operations = [
        migrations.CreateModel(
            name='TransactionUpdateHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('datetime', models.DateTimeField(auto_now_add=True)),
                ('update_type', models.CharField(choices=[('ADD', 'ADD'), ('REMOVE', 'REMOVE'), ('UPDATE', 'UPDATE')], default='ADD', max_length=32)),
                ('field', models.CharField(max_length=64)),
                ('value_before', models.TextField()),
                ('value_after', models.TextField()),
                ('tx', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.lottransaction')),
            ],
            options={
                'verbose_name': 'Transaction Update',
                'verbose_name_plural': 'Transaction Updates',
                'db_table': 'transactions_updates',
            },
        ),
    ]
