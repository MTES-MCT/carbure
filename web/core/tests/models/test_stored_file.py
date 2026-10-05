from datetime import datetime
from unittest.mock import patch
from uuid import UUID

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.test import TestCase

from core.models import Entity, StoredFile
from core.models.file import stored_file_upload_to

User = get_user_model()
FIXED_UPLOAD_AT = datetime(2026, 9, 22, 11, 54, 3)


class StoredFileUploadToTest(TestCase):
    fixtures = ["json/countries.json"]

    def test_upload_to_uses_entity_id_timestamp_and_uuid(self):
        stored_file = StoredFile(entity_id=42)

        with (
            patch("core.models.file.uuid4", return_value=UUID("123456781234123412341234567890ab")),
            patch("core.models.file.timezone.localtime", return_value=FIXED_UPLOAD_AT),
        ):
            path = stored_file_upload_to(stored_file, "Rapport.PDF")

        self.assertEqual(path, "files/42/20260922_115403_123456781234123412341234567890ab.pdf")

    def test_upload_to_requires_entity_id(self):
        with self.assertRaises(ValidationError) as context:
            stored_file_upload_to(StoredFile(), "report.pdf")

        self.assertIn("entity", context.exception.error_dict)

    def test_save_without_entity_does_not_upload(self):
        user = User.objects.create_user(email="no-entity@carbure.local", name="Uploader", password="password")
        stored_file = StoredFile(
            user=user,
            url=ContentFile(b"content", name="report.pdf"),
        )

        with patch("core.models.file.private_storage.save") as mock_save:
            with self.assertRaises(ValidationError) as context:
                stored_file.save()

        self.assertIn("entity", context.exception.error_dict)
        mock_save.assert_not_called()
        self.assertIsNone(stored_file.pk)

    def test_upload_to_dir_overrides_default_directory(self):
        stored_file = StoredFile(entity_id=7)
        stored_file.upload_to_dir = "traceability/actions"

        with (
            patch("core.models.file.uuid4", return_value=UUID("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")),
            patch("core.models.file.timezone.localtime", return_value=FIXED_UPLOAD_AT),
        ):
            path = stored_file_upload_to(stored_file, "import.xlsx")

        self.assertEqual(path, "traceability/actions/7/20260922_115403_aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa.xlsx")

    def test_save_fills_name_from_original_filename(self):
        entity = Entity.objects.create(name="HRS File", entity_type=Entity.HRS)
        user = User.objects.create_user(email="uploader@carbure.local", name="Uploader", password="password")

        stored_file = StoredFile(
            user=user,
            entity=entity,
            url=ContentFile(b"content", name="original-report.pdf"),
        )
        stored_file.save()

        self.assertEqual(stored_file.name, "original-report.pdf")
