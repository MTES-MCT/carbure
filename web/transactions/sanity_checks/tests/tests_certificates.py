from datetime import date

from django.test import TestCase

from transactions.factories import CarbureLotFactory
from transactions.factories.certificate import GenericCertificateFactory
from transactions.sanity_checks.certificates import check_certificate_validity

from ..helpers import get_prefetched_data


class BiofuelFeedstockSanityChecksTest(TestCase):
    fixtures = [
        "json/biofuels.json",
        "json/feedstock.json",
        "json/countries.json",
        "json/entities.json",
        "json/productionsites.json",
        "json/depots.json",
        "json/ml.json",
        "json/entities_sites.json",
    ]

    def setUp(self):
        self.certificate = GenericCertificateFactory(
            certificate_id="VALID",
            valid_from=date(2025, 1, 1),
            valid_until=date(2025, 12, 31),
        )

        self.prefetched_data = get_prefetched_data()

    def test_expired_certificate(self):
        lot = CarbureLotFactory(supplier_certificate="")
        error = check_certificate_validity(lot, self.prefetched_data)
        assert error is None

        lot.supplier_certificate = self.certificate.certificate_id
        lot.delivery_date = date(2025, 6, 1)
        error = check_certificate_validity(lot, self.prefetched_data)
        assert error is None

        lot.delivery_date = date(2024, 12, 31)
        error = check_certificate_validity(lot, self.prefetched_data)
        assert error.error == "INVALID_CERTIFICATE"

        lot.delivery_date = date(2026, 1, 1)
        error = check_certificate_validity(lot, self.prefetched_data)
        assert error.error == "INVALID_CERTIFICATE"
