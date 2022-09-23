# Generated by Django 4.1.1 on 2022-09-13 10:47

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('producers', '0001_initial'),
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='carburestock',
            name='carbure_production_site',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='producers.productionsite'),
        ),
        migrations.AddField(
            model_name='carburestock',
            name='carbure_supplier',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='stock_carbure_supplier', to='core.entity'),
        ),
        migrations.AddField(
            model_name='carburestock',
            name='country_of_origin',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='stock_country_of_origin', to='core.pays'),
        ),
        migrations.AddField(
            model_name='carburestock',
            name='depot',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.depot'),
        ),
        migrations.AddField(
            model_name='carburestock',
            name='feedstock',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.matierepremiere'),
        ),
        migrations.AddField(
            model_name='carburestock',
            name='parent_lot',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.carburelot'),
        ),
        migrations.AddField(
            model_name='carburestock',
            name='parent_transformation',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.carburestocktransformation'),
        ),
        migrations.AddField(
            model_name='carburestock',
            name='production_country',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='stock_production_country', to='core.pays'),
        ),
        migrations.AddField(
            model_name='carburenotification',
            name='dest',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.entity'),
        ),
        migrations.AddField(
            model_name='carburelotreliabilityscore',
            name='lot',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.carburelot'),
        ),
        migrations.AddField(
            model_name='carburelotevent',
            name='lot',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.carburelot'),
        ),
        migrations.AddField(
            model_name='carburelotevent',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='carburelotcomment',
            name='entity',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.entity'),
        ),
        migrations.AddField(
            model_name='carburelotcomment',
            name='lot',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.carburelot'),
        ),
        migrations.AddField(
            model_name='carburelotcomment',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='carburelot',
            name='added_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.entity'),
        ),
        migrations.AddField(
            model_name='carburelot',
            name='biofuel',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.biocarburant'),
        ),
        migrations.AddField(
            model_name='carburelot',
            name='carbure_client',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='carbure_client', to='core.entity'),
        ),
        migrations.AddField(
            model_name='carburelot',
            name='carbure_delivery_site',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='carbure_delivery_site', to='core.depot'),
        ),
        migrations.AddField(
            model_name='carburelot',
            name='carbure_dispatch_site',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='carbure_dispatch_site', to='core.depot'),
        ),
        migrations.AddField(
            model_name='carburelot',
            name='carbure_producer',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='carbure_producer', to='core.entity'),
        ),
        migrations.AddField(
            model_name='carburelot',
            name='carbure_production_site',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='producers.productionsite'),
        ),
        migrations.AddField(
            model_name='carburelot',
            name='carbure_supplier',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='carbure_supplier', to='core.entity'),
        ),
        migrations.AddField(
            model_name='carburelot',
            name='carbure_vendor',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='carbure_vendor', to='core.entity'),
        ),
        migrations.AddField(
            model_name='carburelot',
            name='country_of_origin',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='country_of_origin', to='core.pays'),
        ),
        migrations.AddField(
            model_name='carburelot',
            name='delivery_site_country',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='delivery_site_country', to='core.pays'),
        ),
        migrations.AddField(
            model_name='carburelot',
            name='dispatch_site_country',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='dispatch_site_country', to='core.pays'),
        ),
        migrations.AddField(
            model_name='carburelot',
            name='feedstock',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.matierepremiere'),
        ),
        migrations.AddField(
            model_name='carburelot',
            name='parent_lot',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.carburelot'),
        ),
        migrations.AddField(
            model_name='carburelot',
            name='parent_stock',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.carburestock'),
        ),
        migrations.AddField(
            model_name='carburelot',
            name='production_country',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='production_country', to='core.pays'),
        ),
        migrations.AddIndex(
            model_name='genericerror',
            index=models.Index(fields=['lot'], name='generic_err_lot_id_be0e2d_idx'),
        ),
        migrations.AddIndex(
            model_name='genericerror',
            index=models.Index(fields=['lot', 'acked_by_admin', 'display_to_admin'], name='generic_err_lot_id_226bf8_idx'),
        ),
        migrations.AddIndex(
            model_name='genericerror',
            index=models.Index(fields=['lot', 'acked_by_creator', 'display_to_creator'], name='generic_err_lot_id_5144e1_idx'),
        ),
        migrations.AddIndex(
            model_name='genericerror',
            index=models.Index(fields=['lot', 'acked_by_recipient', 'display_to_recipient'], name='generic_err_lot_id_c3d7d6_idx'),
        ),
        migrations.AddIndex(
            model_name='genericerror',
            index=models.Index(fields=['lot', 'acked_by_auditor', 'display_to_auditor'], name='generic_err_lot_id_f3894c_idx'),
        ),
        migrations.AddIndex(
            model_name='entitycertificate',
            index=models.Index(fields=['entity'], name='carbure_ent_entity__461638_idx'),
        ),
        migrations.AddIndex(
            model_name='carburestocktransformation',
            index=models.Index(fields=['entity'], name='carbure_sto_entity__2e8758_idx'),
        ),
        migrations.AddIndex(
            model_name='carburestockevent',
            index=models.Index(fields=['stock'], name='carbure_sto_stock_i_d107a1_idx'),
        ),
        migrations.AddIndex(
            model_name='carburestock',
            index=models.Index(fields=['carbure_client'], name='carbure_sto_carbure_c4b133_idx'),
        ),
        migrations.AddIndex(
            model_name='carburestock',
            index=models.Index(fields=['carbure_client', 'depot'], name='carbure_sto_carbure_3458dd_idx'),
        ),
        migrations.AddIndex(
            model_name='carburenotification',
            index=models.Index(fields=['dest_id'], name='carbure_not_dest_id_4ac7b3_idx'),
        ),
        migrations.AddIndex(
            model_name='carburelotreliabilityscore',
            index=models.Index(fields=['lot'], name='carbure_lot_lot_id_e75cc9_idx'),
        ),
        migrations.AddIndex(
            model_name='carburelotevent',
            index=models.Index(fields=['lot'], name='carbure_lot_lot_id_2f39a7_idx'),
        ),
        migrations.AddIndex(
            model_name='carburelotcomment',
            index=models.Index(fields=['lot'], name='carbure_lot_lot_id_dcf25a_idx'),
        ),
        migrations.AddIndex(
            model_name='carburelot',
            index=models.Index(fields=['year'], name='carbure_lot_year_870bf1_idx'),
        ),
        migrations.AddIndex(
            model_name='carburelot',
            index=models.Index(fields=['period'], name='carbure_lot_period_03dfac_idx'),
        ),
        migrations.AddIndex(
            model_name='carburelot',
            index=models.Index(fields=['biofuel'], name='carbure_lot_biofuel_abbb0b_idx'),
        ),
        migrations.AddIndex(
            model_name='carburelot',
            index=models.Index(fields=['feedstock'], name='carbure_lot_feedsto_d8cad3_idx'),
        ),
        migrations.AddIndex(
            model_name='carburelot',
            index=models.Index(fields=['carbure_supplier'], name='carbure_lot_carbure_7a9f07_idx'),
        ),
        migrations.AddIndex(
            model_name='carburelot',
            index=models.Index(fields=['carbure_client'], name='carbure_lot_carbure_612b0b_idx'),
        ),
        migrations.AddIndex(
            model_name='carburelot',
            index=models.Index(fields=['carbure_delivery_site'], name='carbure_lot_carbure_a60b71_idx'),
        ),
        migrations.AddIndex(
            model_name='carburelot',
            index=models.Index(fields=['carbure_production_site'], name='carbure_lot_carbure_060fe8_idx'),
        ),
        migrations.AddIndex(
            model_name='carburelot',
            index=models.Index(fields=['year', 'carbure_client'], name='carbure_lot_year_a09da3_idx'),
        ),
        migrations.AddIndex(
            model_name='carburelot',
            index=models.Index(fields=['year', 'carbure_supplier'], name='carbure_lot_year_a3ccca_idx'),
        ),
        migrations.AddIndex(
            model_name='carburelot',
            index=models.Index(fields=['year', 'period'], name='carbure_lot_year_91dbd3_idx'),
        ),
        migrations.AddIndex(
            model_name='carburelot',
            index=models.Index(fields=['year', 'lot_status'], name='carbure_lot_year_26abfd_idx'),
        ),
        migrations.AddIndex(
            model_name='carburelot',
            index=models.Index(fields=['year', 'period', 'lot_status'], name='carbure_lot_year_636d7c_idx'),
        ),
        migrations.AddIndex(
            model_name='carburelot',
            index=models.Index(fields=['year', 'period', 'carbure_client'], name='carbure_lot_year_93dd77_idx'),
        ),
        migrations.AddIndex(
            model_name='carburelot',
            index=models.Index(fields=['year', 'period', 'carbure_supplier'], name='carbure_lot_year_2a6c87_idx'),
        ),
    ]