from django.db import migrations


def insert_data_into_temp_table(apps, schema_editor):
    ContentToUpdate = apps.get_model("transactions", "ContentToUpdate")
    CarbureLot = apps.get_model("core", "CarbureLot")
    CarbureStock = apps.get_model("core", "CarbureStock")
    DoubleCountingApplication = apps.get_model("doublecount", "DoubleCountingApplication")
    DoubleCountingRegistration = apps.get_model("certificates", "DoubleCountingRegistration")
    ProductionSiteCertificate = apps.get_model("certificates", "ProductionSiteCertificate")
    ProductionSiteInput = apps.get_model("producers", "ProductionSiteInput")
    ProductionSiteOutput = apps.get_model("producers", "ProductionSiteOutput")
    SafTicket = apps.get_model("saf", "SafTicket")
    SafTicketSource = apps.get_model("saf", "SafTicketSource")

    # Fill in _tmp_site_migration table with current data
    def create_content_to_update(model_name, field_name, queryset, field_type):
        print(f"Inserting bulk {model_name} start")

        batch_size = 1000
        content_to_insert_batch = []
        batch_count = 0

        for obj in queryset.iterator(chunk_size=batch_size):
            field_value = getattr(obj, field_name)
            if field_value:
                content_to_insert_batch.append(
                    ContentToUpdate(
                        model=model_name,
                        field=field_name,
                        content_id=obj.id,
                        **{field_type: field_value},
                    )
                )
            if len(content_to_insert_batch) >= batch_size:
                batch_count += batch_size
                print(f"Inserting bulk {model_name}: {len(content_to_insert_batch)} ({batch_count}/{queryset.count()})")
                ContentToUpdate.objects.bulk_create(content_to_insert_batch)
                content_to_insert_batch = []

        if content_to_insert_batch:
            print(f"Inserting last bulk {model_name}: {len(content_to_insert_batch)} ({batch_count}/{queryset.count()})")
            ContentToUpdate.objects.bulk_create(content_to_insert_batch)
            print(f"Inserting bulk {model_name} end")
            print("--------------------------------")

    models_to_update = [
        ("CarbureLot", CarbureLot, "carbure_delivery_site", "depot"),
        ("CarbureLot", CarbureLot, "carbure_dispatch_site", "depot"),
        ("CarbureStock", CarbureStock, "depot", "depot"),
        ("CarbureLot", CarbureLot, "carbure_production_site", "production_site"),
        ("CarbureStock", CarbureStock, "carbure_production_site", "production_site"),
        ("DoubleCountingApplication", DoubleCountingApplication, "production_site", "production_site"),
        ("DoubleCountingRegistration", DoubleCountingRegistration, "production_site", "production_site"),
        ("ProductionSiteCertificate", ProductionSiteCertificate, "production_site", "production_site"),
        ("ProductionSiteInput", ProductionSiteInput, "production_site", "production_site"),
        ("ProductionSiteOutput", ProductionSiteOutput, "production_site", "production_site"),
        ("SafTicket", SafTicket, "carbure_production_site", "production_site"),
        ("SafTicketSource", SafTicketSource, "carbure_production_site", "production_site"),
    ]

    for model_name, model, field_name, field_type in models_to_update:
        print(f"Selecting {model_name} with field {field_name}")
        queryset = model.objects.filter(**{f"{field_name}__isnull": False})
        print(f"Number of {model_name} selected: {queryset.count()}")

        create_content_to_update(model_name, field_name, queryset, field_type)

        print(f"Emptying '{field_name}' field from {model_name}")
        queryset.update(**{field_name: None})


def reverse_migration(apps, schema_editor):
    # Truncate table _tmp_site_migration
    ContentToUpdate = apps.get_model("transactions", "ContentToUpdate")
    ContentToUpdate.objects.all().delete()


class Migration(migrations.Migration):
    dependencies = [
        ("transactions", "0004_contenttoupdate_site_entitysite"),
        ("producers", "0004_alter_productionsiteinput_production_site_and_more"),
    ]

    operations = [
        migrations.RunPython(insert_data_into_temp_table, reverse_code=reverse_migration),
    ]
