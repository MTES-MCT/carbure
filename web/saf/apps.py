from django.apps import AppConfig


class SafConfig(AppConfig):
    name = "saf"

    def ready(self):
        from . import hooks
