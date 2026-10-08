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

    def test_validates_registration_id_format(self):
        invalid_registration_ids = ["", "XXXXXXXXX", "12345678", "12345678990"]
        for ri in invalid_registration_ids:
            with self.assertRaises(ValueError):
                NationalTradeRegister("FR", ri)

    def test_send_explicit_error_message_on_invalid_registration_id(self):
        with self.assertRaises(ValueError) as context:
            NationalTradeRegister("FR", "XXX")

        self.assertEqual("Invalid format for registration id 'XXX'", context.exception.args[0])
