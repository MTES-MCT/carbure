from unittest.mock import MagicMock, patch

import requests
from django.test import TestCase
from django.urls import reverse

from carbure.api.metabase_status import is_metabase_available


class MetabaseStatusViewTest(TestCase):
    def setUp(self):
        self.url = reverse("carbure-metabase-status")

    @patch("carbure.api.metabase_status.is_metabase_available", return_value=True)
    def test_returns_available_true(self, _mock):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"available": True})

    @patch("carbure.api.metabase_status.is_metabase_available", return_value=False)
    def test_returns_available_false(self, _mock):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"available": False})


class IsMetabaseAvailableTest(TestCase):
    @patch("carbure.api.metabase_status.requests.get")
    def test_true_when_metabase_returns_200(self, mock_get):
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        self.assertTrue(is_metabase_available())
        mock_get.assert_called_once()

    @patch("carbure.api.metabase_status.requests.get")
    def test_false_when_metabase_returns_503(self, mock_get):
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = requests.HTTPError()
        mock_get.return_value = mock_response

        self.assertFalse(is_metabase_available())
