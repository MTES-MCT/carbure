from django.test import TestCase
from django.urls import reverse
from producers.urls import urlpatterns
from django.contrib.auth import get_user_model

from core.models import Entity, UserRights
from producers.models import *

import datetime

class PublicUrlsTest(TestCase):
    def test_index(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)

    def test_stats(self):
        response = self.client.get(reverse('public-stats'))
        self.assertEqual(response.status_code, 200)