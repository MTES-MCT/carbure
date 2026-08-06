from unittest import TestCase

from edelivery.ebms.ntr import NationalTradeRegister


class NationalTradeRegisterTest(TestCase):
    def test_knows_its_country_code(self):
        ntr = NationalTradeRegister.from_id("FR_SIREN_CD123456789")
        self.assertEqual("FR", ntr.country_code)

    def test_knows_its_registration_id(self):
        ntr = NationalTradeRegister.from_id("FR_SIREN_CD123456789")
        self.assertEqual("123456789", ntr.registration_id)

    def test_produces_ntr_id(self):
        ntr = NationalTradeRegister("FR", "123456789")
        self.assertEqual("FR_SIREN_CD123456789", ntr.id())

    def test_ntr_id_raises_an_error_if_country_code_not_FR(self):
        ntr = NationalTradeRegister("DE", "123456789")
        with self.assertRaises(NotImplementedError):
            ntr.id()
