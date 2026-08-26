from unittest import TestCase

from core.models.certificate import GenericCertificate, valid_certificate_scope


class ValidCertificateScopeTest(TestCase):
    national_scheme = GenericCertificate.SYSTEME_NATIONAL

    def test_returns_true_if_valid_scope_format(self):
        valid_scopes = ["1", "2", "3", "4", "5", "6", "6a", "6b", "7", "1, 2", "2, 5, 6a"]
        for scope in valid_scopes:
            with self.subTest(scope):
                self.assertTrue(valid_certificate_scope(self.national_scheme, scope))

    def test_returns_false_if_valid_scope_format(self):
        invalid_scopes = ["", "None", "8", "9", "4807", "1 2", "1 et 2", "1, 2 et 3", "2&3&4", "6c", "1,2,3"]
        for scope in invalid_scopes:
            with self.subTest(scope):
                self.assertFalse(valid_certificate_scope(self.national_scheme, scope))

    def test_returns_true_if_not_national_scheme(self):
        self.assertTrue(valid_certificate_scope(GenericCertificate.ISCC, "1 2"))
