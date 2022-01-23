import datetime
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from core.models import MatierePremiere, Biocarburant, Pays, Entity, ProductionSite, Depot
from api.v3.common.urls import urlpatterns
from django_otp.plugins.otp_email.models import EmailDevice


class LotCorrectionTest(TestCase):
    def setUp(self):
        user_model = get_user_model()
        # let's create a user
        self.password = 'totopouet'
        self.user1 = user_model.objects.create_user(email='testuser1@toto.com', name='Le Super Testeur 1', password=self.password)
        loggedin = self.client.login(username=self.user1.email, password=self.password)
        self.assertTrue(loggedin)
        # pass otp verification
        response = self.client.get(reverse('otp-verify'))
        self.assertEqual(response.status_code, 200)
        device = EmailDevice.objects.get(user=self.user1)
        response = self.client.post(reverse('otp-verify'), {'otp_token': device.token})
        self.assertEqual(response.status_code, 302)
       