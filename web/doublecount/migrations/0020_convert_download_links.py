from django.db import migrations


def convert_download_links(apps, schema_editor):
    DoubleCountingApplication = apps.get_model("doublecount", "DoubleCountingApplication")

    for app in DoubleCountingApplication.objects.all():
        if app.download_link and app.download_link.startswith("http"):
            try:
                # Check if the URL contains "doublecounting"
                if "doublecounting" in app.download_link:
                    # Find the index of "doublecounting"
                    index = app.download_link.find("doublecounting")
                    if index != -1:
                        # Extract the substring starting from "doublecounting"
                        s3_key = app.download_link[index:]
                        app.download_link = s3_key
                        app.save()
            except Exception as e:
                print(f"Erreur lors du traitement de l'URL {app.download_link}: {e}")
                pass


def reverse_convert_download_links(apps, schema_editor):
    DoubleCountingApplication = apps.get_model("doublecount", "DoubleCountingApplication")
    for app in DoubleCountingApplication.objects.all():
        if app.download_link and not app.download_link.startswith("http") and app.download_link.startswith("doublecounting"):
            app.download_link = f"https://oos.cloudgouv-eu-west-1.outscale.com/carbure/carbure-prod/{app.download_link}"
            app.save()


class Migration(migrations.Migration):
    dependencies = [
        ("doublecount", "0019_alter_doublecountingapplication_options"),
    ]

    operations = [
        migrations.RunPython(convert_download_links, reverse_convert_download_links),
    ]
