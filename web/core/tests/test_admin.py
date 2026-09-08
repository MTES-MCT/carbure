from unittest import TestCase
from unittest.mock import patch

from django.core.exceptions import ValidationError

from core.admin import GenericCertificateResource


class GenericCertificateResourceTest(TestCase):
    @patch("core.admin.valid_certificate_scope")
    def test_validates_scope_at_import(self, patched_valid_certificate_scope):
        patched_valid_certificate_scope.return_value = False
        resource = GenericCertificateResource()
        patched_valid_certificate_scope.assert_not_called()

        row = {"certificate_id": "some_id", "certificate_type": "some_type", "scope": "invalid scope"}
        with self.assertRaises(ValidationError) as context:
            resource.before_import_row(row)

        patched_valid_certificate_scope.assert_called_with("some_type", "invalid scope")
        self.assertEqual("Scope 'invalid scope' for certificate 'some_id' has an invalid format", context.exception.message)
