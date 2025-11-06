from unittest.mock import patch

from django.test import TestCase
from web.core.utils import CarbureEnv


class CarbureEnvTest(TestCase):
    @patch.dict("os.environ", {"IMAGE_TAG": "local"})
    def test_get_base_url_local_without_public_url(self):
        """Test que get_base_url retourne l'URL locale quand IMAGE_TAG=local et PUBLIC_URL n'est pas défini"""

        base_url = CarbureEnv.get_base_url()
        self.assertEqual(base_url, "http://carbure.local:8090")

    @patch.dict("os.environ", {"IMAGE_TAG": "local", "PUBLIC_URL": "https://custom.local.url"})
    def test_get_base_url_local_with_public_url(self):
        """Test que get_base_url retourne PUBLIC_URL quand IMAGE_TAG=local et PUBLIC_URL est défini"""
        base_url = CarbureEnv.get_base_url()

        self.assertEqual(base_url, "https://custom.local.url")

    @patch.dict("os.environ", {"IMAGE_TAG": "prod"})
    def test_get_base_url_default_without_public_url(self):
        """Test que get_base_url retourne l'URL par défaut quand PUBLIC_URL n'est pas défini"""
        base_url = CarbureEnv.get_base_url()

        self.assertEqual(base_url, "https://carbure.beta.gouv.fr")

    @patch.dict("os.environ", {"IMAGE_TAG": "prod", "PUBLIC_URL": "https://prod.carbure.beta.gouv.fr"})
    def test_get_base_url_prod_with_public_url(self):
        """Test que get_base_url retourne PUBLIC_URL quand PUBLIC_URL est défini"""
        base_url = CarbureEnv.get_base_url()

        self.assertEqual(base_url, "https://prod.carbure.beta.gouv.fr")
