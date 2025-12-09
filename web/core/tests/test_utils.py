from unittest import TestCase
from unittest.mock import patch

from core.utils import CarbureEnv


class CarbureEnvTest(TestCase):
    @patch.dict("os.environ", {"PUBLIC_URL": "https://carbure.example.com"})
    def test_get_base_url_local_with_public_url(self):
        """Test that get_base_url returns PUBLIC_URL when IMAGE_TAG=local and PUBLIC_URL is defined"""
        base_url = CarbureEnv.get_base_url()

        self.assertEqual(base_url, "https://carbure.example.com")
