import json
import random
import os
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django_otp.plugins.otp_email.models import EmailDevice

from core.models import Entity, UserRights


class MassBalanceAPITest(TestCase):
    home = os.environ['CARBURE_HOME']
    fixtures = ['{home}/web/fixtures/json/countries.json'.format(home=home), 
    '{home}/web/fixtures/json/feedstock.json'.format(home=home), 
    '{home}/web/fixtures/json/biofuels.json'.format(home=home),
    '{home}/web/fixtures/json/depots.json'.format(home=home)]

    def setUp(self):
        user_model = get_user_model()
        self.user_email = 'user@carbure.beta.gouv.fr'
        self.user_password = 'toto'
        self.user = user_model.objects.create_user(email=self.user_email, name='Super User', password=self.user_password)
        # create OTP devices
        for user in [self.user]:
            email_otp = EmailDevice()
            email_otp.user = user
            email_otp.name = 'email'
            email_otp.confirmed = True
            email_otp.email = user.email
            email_otp.save()

        self.entity1, _ = Entity.objects.update_or_create(name='Le Super Producteur 1', entity_type='Producteur')
        # some rights
        UserRights.objects.update_or_create(user=self.user, entity=self.entity1, role=UserRights.RW)
        # login as user
        loggedin = self.client.login(username=self.user_email, password=self.user_password)
        self.assertTrue(loggedin)
        # pass otp        
        device = EmailDevice.objects.get(user=self.user)
        device.generate_token()
        response = self.client.post(reverse('otp-verify'), {'otp_token': device.token})
        self.assertEqual(response.status_code, 302) #  redirected to home page

    def login_and_pass_otp(self, email, password):
        loggedin = self.client.login(username=email, password=password)
        self.assertTrue(loggedin)          
        response = self.client.get(reverse('otp-verify'))
        self.assertEqual(response.status_code, 200)
        usermodel = get_user_model()
        user = usermodel.objects.get(email=email)
        device = EmailDevice.objects.get(user=user)
        response = self.client.post(reverse('otp-verify'), {'otp_token': device.token})
        self.assertEqual(response.status_code, 302)   

    def create_lot(self, **kwargs):
        lot = {
            'supplier_certificate': 'ISCC-TOTO-02',
            'biocarburant_code': 'ETH',
            'matiere_premiere_code': 'BLE',
            'producer': self.entity1.name,
            'production_site': "PSITE1",
            'volume': 15000,
            'pays_origine_code': 'FR',
            'eec': 1,
            'ep': 5,
            'etd': 12,
            'dae': 'dpwqdkqpokd',
            'delivery_date': '2020-12-31',
            'client': self.entity1.name,
            'delivery_site': '001',
            'entity_id': self.entity1.id,
        }
        lot.update(kwargs)
        response = self.client.post(reverse('api-v3-add-lot'), lot)
        self.assertEqual(response.status_code, 200)
        data = response.json()['data']
        tx_id = data['id']
        lot_id = data['lot']['id']
        return tx_id, lot_id, lot

    def create_out_transaction(self, **kwards):
        today = datetime.date.today().strftime('%d/%m/%Y')
        now = datetime.datetime.now().strftime('%H%M%S%f')
        data = {
            'dae': 'DAETEST%s' % (now),
            'carbure_storage_site': '1676',
            'client': 'TMF',
            'delivery_date': today,
            'delivery_site': '1168',
            'volume': random.randrange(30000, 37000),
        }
        data.update(kwargs)
        response = self.client.post('/api/v3/massbalance/add-pending-transactions', {'transactions': [data]})
        self.assertEqual(response.status_code, 200)

    def test_create_dae(self):
        self.create_out_transaction()

    def test_update_dae(self):
        #self.create_out_transaction()
        pass

    def test_create_dae_rights():
        pass

    def test_mass_balance(self):
        # 1) create a lot and send it to stock
        # 2) create a pending DAE
        # 3) 
        pass

