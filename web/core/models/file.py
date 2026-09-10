from pathlib import Path
from uuid import uuid4

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from core import private_storage

DEFAULT_UPLOAD_DIR = "files"
ENTITY_REQUIRED = _("Une entité est requise pour enregistrer un fichier.")


def stored_file_upload_to(instance, filename):
    """Build a collision-free private-storage path.

    Layout: ``{directory}/{entity_id}/{uuid}{ext}``.

    ``directory`` defaults to ``files`` and can be overridden per instance via
    the non-persisted ``upload_to_dir`` attribute, e.g. ``traceability/actions``.
    The original filename is stored on ``StoredFile.name``, not in the object key.
    """
    if not instance.entity_id:
        raise ValidationError({"entity": ENTITY_REQUIRED})

    directory = getattr(instance, "upload_to_dir", None) or DEFAULT_UPLOAD_DIR
    extension = Path(filename).suffix.lower()
    return f"{directory}/{instance.entity_id}/{uuid4().hex}{extension}"


class StoredFile(models.Model):
    name = models.CharField(max_length=255)
    url = models.FileField(storage=private_storage, upload_to=stored_file_upload_to, max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="stored_files",
    )
    entity = models.ForeignKey(
        "core.Entity",
        on_delete=models.PROTECT,
        related_name="stored_files",
    )

    class Meta:
        db_table = "file"
        verbose_name = "Fichier"
        verbose_name_plural = "Fichiers"
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    def clean(self):
        super().clean()
        if not self.entity_id:
            raise ValidationError({"entity": ENTITY_REQUIRED})

    def save(self, *args, **kwargs):
        if not self.entity_id:
            raise ValidationError({"entity": ENTITY_REQUIRED})
        if not self.name and self.url:
            self.name = Path(self.url.name).name
        super().save(*args, **kwargs)
