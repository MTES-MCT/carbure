from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from core.models import Entity, UserRights


class AccountTest(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user_name = 'Jean Test'
        self.user_email = 'foobar@example.com'
        self.user_password = 'totopouet'

    def test_register(self):
        # go to register page
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        # send form with missing data
        response = self.client.post(reverse('register'), {'username': self.user_name, 'email': self.user_email, 'password1': self.user_password})
        self.assertEqual(response.status_code, 200)

        # send form normally
        response = self.client.post(reverse('register'), {'username': self.user_name, 'email': self.user_email, 'password1': self.user_password, 'password2': self.user_password})
        self.assertEqual(response.status_code, 200)

        # try to register an already existing user
        response = self.client.post(reverse('register'), {'username': self.user_name, 'email': self.user_email, 'password1': self.user_password, 'password2': self.user_password})
        self.assertEqual(response.status_code, 200)


        # submit wrong activation link
        # submit good activation link
        pass

    def test_login


        # try to login with non existant user
        # try to login with existing user but bad password
        # login
        # be redirected to otp_verify page
        # try to access another page -> redirect to otp_verify
        # submit wrong otp -> try to access another page -> redirect to otp_verify
        # submit good otp
        # check that we are logged in
        pass