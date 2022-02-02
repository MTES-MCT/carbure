import json
import os
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django_otp.plugins.otp_email.models import EmailDevice

from core.models import Entity, UserRights


class AuditorAPITest(TestCase):
    home = os.environ['CARBURE_HOME']
    fixtures = ['{home}/web/fixtures/json/countries.json'.format(home=home),
    '{home}/web/fixtures/json/feedstock.json'.format(home=home),
    '{home}/web/fixtures/json/biofuels.json'.format(home=home),
    '{home}/web/fixtures/json/depots.json'.format(home=home)]

    def setUp(self):
        user_model = get_user_model()
        self.admin_email = 'superadmin@carbure.beta.gouv.fr'
        self.admin_password = 'toto'
        self.auditor_email = 'auditor@carbure.beta.gouv.fr'
        self.auditor_password = 'toto2'
        self.admin_user = user_model.objects.create_user(email=self.admin_email, name='Super Admin', password=self.admin_password, is_staff=True)
        self.auditor_user = user_model.objects.create_user(email=self.auditor_email, name='Super Auditor', password=self.auditor_password)
        # create OTP devices
        for user in [self.admin_user, self.auditor_user]:
            email_otp = EmailDevice()
            email_otp.user = user
            email_otp.name = 'email'
            email_otp.confirmed = True
            email_otp.email = user.email
            email_otp.save()

        # let's create a few users
        self.user1_email = 'testuser1@toto.com'
        self.user1_password = 'toto3'
        self.user1 = user_model.objects.create_user(email=self.user1_email, name='Le Super Testeur 1', password=self.user1_password)
        # a few entities
        self.entity1, _ = Entity.objects.update_or_create(name='Le Super Producteur 1', entity_type='Producteur')
        # some rights
        UserRights.objects.update_or_create(user=self.user1, entity=self.entity1, role=UserRights.RW)
        UserRights.objects.update_or_create(user=self.auditor_user, entity=self.entity1, role=UserRights.AUDITOR)
        # login as an admin
        loggedin = self.client.login(username=self.admin_email, password=self.admin_password)
        self.assertTrue(loggedin)
        # pass otp
        usermodel = get_user_model()
        user = usermodel.objects.get(email=self.admin_email)
        response = self.client.post(reverse('api-v4-request-otp'))
        self.assertEqual(response.status_code, 200)
        device, created = EmailDevice.objects.get_or_create(user=user)
        response = self.client.post(reverse('api-v4-verify-otp'), {'otp_token': device.token})
        self.assertEqual(response.status_code, 200)

    def login_and_pass_otp(self, email, password):
        loggedin = self.client.login(username=email, password=password)
        self.assertTrue(loggedin)
        usermodel = get_user_model()
        user = usermodel.objects.get(email=email)
        response = self.client.post(reverse('api-v4-request-otp'))
        self.assertEqual(response.status_code, 200)
        device, created = EmailDevice.objects.get_or_create(user=user)
        response = self.client.post(reverse('api-v4-verify-otp'), {'otp_token': device.token})
        self.assertEqual(response.status_code, 200)

    # def test_auditor_comments(self):
    #     # login as user
    #     # create and send lot
    #     self.login_and_pass_otp(self.user1_email, self.user1_password)
    #     tx_id, lot_id, lot = self.create_lot()

    #     # login as auditor
    #     # as auditor, write a comment
    #     # write other comment visible by admin
    #     self.login_and_pass_otp(self.auditor_email, self.auditor_password)
    #     response = self.client.post(reverse('api-v3-auditor-comment-transactions'), {'entity_id': self.entity1.id, 'tx_ids': [tx_id], 'comment': 'Test comment just for me'})
    #     self.assertEqual(response.status_code, 200)
    #     response = self.client.post(reverse('api-v3-auditor-comment-transactions'), {'entity_id': self.entity1.id, 'tx_ids': [tx_id], 'comment': 'Test comment for admin', 'is_visible_by_admin': 'true'})
    #     self.assertEqual(response.status_code, 200)
    #     # get_details, see two comments
    #     response = self.client.get(reverse('api-v3-auditor-lots-get-details'), {'entity_id': self.entity1.id, 'tx_id': tx_id})
    #     self.assertEqual(response.status_code, 200)
    #     data = json.loads(response.content)
    #     self.assertEqual(len(data['data']['admin_comments']), 2)

    #     # login as admin
    #     # get_details, see one comment
    #     # comment once
    #     # comment twice - visible by auditor
    #     self.login_and_pass_otp(self.admin_email, self.admin_password)
    #     response = self.client.get(reverse('api-v3-admin-get-lot-details'), {'tx_id': tx_id})
    #     self.assertEqual(response.status_code, 200)
    #     data = json.loads(response.content)
    #     self.assertEqual(len(data['data']['admin_comments']), 1)
    #     response = self.client.post(reverse('api-v3-admin-comment-transaction'), {'entity_id': self.entity1.id, 'tx_ids': [tx_id], 'comment': 'Test admin just for me'})
    #     self.assertEqual(response.status_code, 200)
    #     response = self.client.post(reverse('api-v3-admin-comment-transaction'), {'entity_id': self.entity1.id, 'tx_ids': [tx_id], 'comment': 'Test admin for auditor', 'is_visible_by_auditor': 'true'})
    #     self.assertEqual(response.status_code, 200)

    #     # login as auditor
    #     # get details, see 3 comments, one of which by admin
    #     self.login_and_pass_otp(self.auditor_email, self.auditor_password)
    #     response = self.client.get(reverse('api-v3-auditor-lots-get-details'), {'entity_id': self.entity1.id, 'tx_id': tx_id})
    #     self.assertEqual(response.status_code, 200)
    #     data = json.loads(response.content)
    #     self.assertEqual(len(data['data']['admin_comments']), 3)
