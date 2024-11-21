# Generated by Django 5.0.6 on 2024-09-30 07:23

from django.db import migrations, transaction


def create_sites_and_update_related_content(apps, schema_editor):
    ContentToUpdate = apps.get_model("transactions", "ContentToUpdate")
    Site = apps.get_model("transactions", "Site")
    ProductionSite = apps.get_model("producers", "ProductionSite")
    Depot = apps.get_model("core", "Depot")
    EntitySite = apps.get_model("transactions", "EntitySite")
    EntityDepot = apps.get_model("core", "EntityDepot")

    models_mapping = {
        "CarbureLot": apps.get_model("core", "CarbureLot"),
        "CarbureStock": apps.get_model("core", "CarbureStock"),
        "DoubleCountingApplication": apps.get_model("doublecount", "DoubleCountingApplication"),
        "DoubleCountingRegistration": apps.get_model("certificates", "DoubleCountingRegistration"),
        "ProductionSiteCertificate": apps.get_model("certificates", "ProductionSiteCertificate"),
        "ProductionSiteInput": apps.get_model("producers", "ProductionSiteInput"),
        "ProductionSiteOutput": apps.get_model("producers", "ProductionSiteOutput"),
        "SafTicket": apps.get_model("saf", "SafTicket"),
        "SafTicketSource": apps.get_model("saf", "SafTicketSource"),
    }

    @transaction.atomic
    def create_site_and_update_related_content(entity, filter_column_name, site_type, created_by):
        print(f"Creating site for {entity.name}")
        site = Site.objects.create(
            name=entity.name,
            site_siret=getattr(entity, "site_id", "") or "",
            city=entity.city if entity.city else "",
            customs_id=getattr(entity, "depot_id", "") or "",
            site_type=site_type,
            country=entity.country,
            postal_code=entity.postal_code,
            address=entity.address,
            gps_coordinates=entity.gps_coordinates,
            accise=getattr(entity, "accise", "") or "",
            electrical_efficiency=getattr(entity, "electrical_efficiency", None),
            thermal_efficiency=getattr(entity, "thermal_efficiency", None),
            useful_temperature=getattr(entity, "useful_temperature", None),
            ges_option=getattr(entity, "ges_option", "") or "",
            eligible_dc=getattr(entity, "eligible_dc", False),
            dc_number=getattr(entity, "dc_number", "") or "",
            dc_reference=getattr(entity, "dc_reference", "") or "",
            manager_name=getattr(entity, "manager_name", "") or "",
            manager_phone=getattr(entity, "manager_phone", "") or "",
            manager_email=getattr(entity, "manager_email", "") or "",
            private=getattr(entity, "private", False),
            is_enabled=getattr(entity, "is_enabled", True),
            date_mise_en_service=getattr(entity, "date_mise_en_service", None),
            created_by=created_by,
        )

        # Update all related content of old entity
        related_content = ContentToUpdate.objects.filter(**{filter_column_name: entity.id})

        for content in related_content:
            Model = models_mapping.get(content.model)
            if Model is not None:
                update_data = {content.field: site.id}
                filter_data = {"id": content.content_id}
                Model.objects.filter(**filter_data).update(**update_data)
            else:
                print(f"Model {content.model} not found")

        # Create an EntitySite relation
        if isinstance(entity, Depot):
            entity_depots = EntityDepot.objects.filter(depot=entity)
            for entity_depot in entity_depots:
                EntitySite.objects.create(
                    site=site,
                    entity=entity_depot.entity,
                    ownership_type=entity_depot.ownership_type,
                    blending_is_outsourced=entity_depot.blending_is_outsourced,
                    blender=entity_depot.blender,
                )
        else:
            EntitySite.objects.create(
                site=site,
                entity=entity.producer,
                ownership_type="THIRD_PARTY",
            )

    production_sites = ProductionSite.objects.all()
    for production_site in production_sites:
        create_site_and_update_related_content(
            entity=production_site,
            filter_column_name="production_site_id",
            site_type="PRODUCTION SITE",
            created_by=production_site.producer,
        )

    depots = Depot.objects.all()
    for depot in depots:
        create_site_and_update_related_content(
            entity=depot,
            filter_column_name="depot_id",
            site_type=depot.depot_type,
            created_by=depot.entitydepot_set.first().entity if depot.entitydepot_set.exists() else None,
        )


def reverse_migration(apps, schema_editor):
    # Truncate table sites and entity_sites
    Site = apps.get_model("transactions", "Site")
    Site.objects.all().delete()
    EntitySite = apps.get_model("transactions", "EntitySite")
    EntitySite.objects.all().delete()


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ("transactions", "0005_move_data_to_site_model_backup"),
        ("certificates", "0006_alter_doublecountingregistration_production_site_and_more"),
        ("core", "0035_alter_carburelot_carbure_delivery_site_and_more"),
        ("doublecount", "0016_alter_doublecountingapplication_production_site"),
        ("producers", "0005_alter_productionsiteinput_production_site_and_more"),
        ("saf", "0021_alter_safticket_carbure_production_site_and_more"),
    ]

    operations = [
        migrations.RunPython(create_sites_and_update_related_content, reverse_code=reverse_migration),
    ]
