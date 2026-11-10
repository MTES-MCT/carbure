from django.contrib.auth.hashers import make_password
from django.db import migrations
from django.db.models import Q


def set_unusable_password_on_pending_invites(apps, schema_editor):
    """Align accounts created by the old empty-name invitation signal.

    Pending invites used to be detected via a blank name. They now have no usable
    password, which is what activation and link resend rely on.
    """
    User = apps.get_model("authtools", "User")
    pending_invites = (
        User.objects.filter(is_active=False).filter(Q(name="") | Q(name__isnull=True)).filter(last_login__isnull=True)
    )
    for user in pending_invites.iterator():
        user.password = make_password(None)
        user.save(update_fields=["password"])


class Migration(migrations.Migration):
    dependencies = [
        ("user", "0001_initial"),
        ("authtools", "0003_auto_20160128_0912"),
    ]

    operations = [
        migrations.RunPython(set_unusable_password_on_pending_invites, migrations.RunPython.noop),
    ]
