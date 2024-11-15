from django.apps import AppConfig


class ApikeyConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apikey"

    def ready(self):
        # import above schema.py
        import apikey.extensions  # noqa: F401
