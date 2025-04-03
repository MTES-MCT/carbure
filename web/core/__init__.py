from django.conf import settings
from django.core.files.storage import get_storage_class

storage_class = get_storage_class(settings.STORAGES["private"]["BACKEND"])
private_storage = storage_class(**settings.STORAGES["private"].get("OPTIONS", {}))