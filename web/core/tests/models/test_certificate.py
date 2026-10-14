from unittest import TestCase
from unittest.mock import MagicMock

from core.models.certificate import GenericCertificate, valid_certificate_scope


class ValidCertificateScopeTest(TestCase):
    national_scheme = GenericCertificate.SYSTEME_NATIONAL

    def test_returns_true_if_valid_scope_format(self):
        valid_scopes = ["BP", "EP", "ET", "FSP", "HEFA", "HVO", "PB", "TR", "TRS", "PB, FSP", "BP, EP, TRS"]
        for scope in valid_scopes:
            with self.subTest(scope):
                self.assertTrue(valid_certificate_scope(self.national_scheme, scope))

    def test_returns_false_if_valid_scope_format(self):
        invalid_scopes = ["", "None", "XX", "6a", "BP EP", "BP et EP", "BP, EP et TRS", "BP&EP", "BP,EP,TRS"]
        for scope in invalid_scopes:
            with self.subTest(scope):
                self.assertFalse(valid_certificate_scope(self.national_scheme, scope))

    def test_returns_false_if_not_national_scheme(self):
        self.assertFalse(valid_certificate_scope(GenericCertificate.ISCC, "FSP"))

class GenericCertificateTest(TestCase):
    def test_fetches_all_valid_national_scheme_certificates(self):
        query_result = MagicMock()
        patched_filter = GenericCertificate.objects.filter = MagicMock(return_value=query_result)

        certificates = GenericCertificate.all_valid_under_national_scheme()
        patched_filter.assert_called_with(
            certificate_type=GenericCertificate.SYSTEME_NATIONAL,
            status=GenericCertificate.VALID,
        )
        self.assertEqual(query_result, certificates)
