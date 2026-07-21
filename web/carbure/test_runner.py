"""Custom Django test runner.

Site.save() resolves GPS coordinates via entity.services.geolocation.get_coordinates,
which calls the api-adresse.data.gouv.fr HTTP API. Most factories set address fields,
so unrelated tests would hit the network on every Site/Depot create.

This runner patches get_coordinates globally for the whole test suite. Individual tests
can still override the mock with @patch("entity.services.geolocation.get_coordinates").
Activated in settings when TEST=1.
"""

from unittest.mock import patch

from django.test.runner import DiscoverRunner

DEFAULT_TEST_COORDINATES = (2.3522, 48.8566)


class CarbureTestRunner(DiscoverRunner):
    def setup_test_environment(self, **kwargs):
        super().setup_test_environment(**kwargs)
        self._get_coordinates_patcher = patch(
            "entity.services.geolocation.get_coordinates",
            return_value=DEFAULT_TEST_COORDINATES,
        )
        self._get_coordinates_patcher.start()

    def teardown_test_environment(self, **kwargs):
        self._get_coordinates_patcher.stop()
        super().teardown_test_environment(**kwargs)
