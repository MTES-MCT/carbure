import datetime
import os
import random
import time
import json

from django.test import TestCase
from django.test import TransactionTestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from core.models import Entity, Pays, Biocarburant, MatierePremiere, Depot, UserRights
from producers.models import ProductionSite
from doublecount.models import DoubleCountingAgreement, DoubleCountingSourcing, DoubleCountingProduction
from django_otp.plugins.otp_email.models import EmailDevice
from django.core.files.uploadedfile import SimpleUploadedFile

class DCAAPITest(TransactionTestCase):
    home = os.environ['CARBURE_HOME']
    fixtures = ['{home}/web/fixtures/json/countries.json'.format(home=home), 
    '{home}/web/fixtures/json/feedstock.json'.format(home=home), 
    '{home}/web/fixtures/json/biofuels.json'.format(home=home),
    '{home}/web/fixtures/json/depots.json'.format(home=home)]

    def setUp(self):
        user_model = get_user_model()
        self.user_email = 'testuser1@toto.com'
        self.user_password = 'totopouet'
        self.user1 = user_model.objects.create_user(email=self.user_email, name='Le Super Testeur 1', password=self.user_password)
        self.producer, _ = Entity.objects.update_or_create(name='Le Super Producteur 1', entity_type='Producteur')
        UserRights.objects.update_or_create(user=self.user1, entity=self.producer, role='RW')
        france = Pays.objects.get(code_pays='FR')
        today = datetime.date.today()
        d = {'country': france, 'date_mise_en_service': today, 'site_id':'SIRET XXX',
        'city': 'paris', 'postal_code': '75001', 'manager_name':'Guillaume Caillou', 
        'manager_phone':'0145247000', 'manager_email': 'test@test.net'}
        self.production_site, _ = ProductionSite.objects.update_or_create(producer=self.producer, name='PSITE1', defaults=d)
        Depot.objects.update_or_create(name='Depot Test', depot_id='001', country=france)

        loggedin = self.client.login(username=self.user_email, password=self.user_password)
        self.assertTrue(loggedin)          
        # pass otp verification
        response = self.client.get(reverse('otp-verify'))
        self.assertEqual(response.status_code, 200)
        device = EmailDevice.objects.get(user=self.user1)
        response = self.client.post(reverse('otp-verify'), {'otp_token': device.token})
        self.assertEqual(response.status_code, 302)

    def test_dca_sourcing(self):
        # download template sourcing
        response = self.client.get(reverse('api-v3-doublecount-get-template'), {'file_type':'SOURCING'})
        self.assertEqual(response.status_code, 200)        
        # upload template sourcing
        filepath = '%s/web/fixtures/csv/test_data/dca_sourcing.xlsx' % (os.environ['CARBURE_HOME'])
        fh = open(filepath, 'rb')
        data = fh.read()
        fh.close()
        f = SimpleUploadedFile("sourcing.xlsx", data)
        response = self.client.post(reverse('api-v3-doublecount-upload-file'), {'entity_id': self.producer.id, 'production_site_id': self.production_site.id, 'file_type': 'SOURCING', 'file': f})
        if response.status_code != 200:
            print('Failed to upload %s' % (filepath))
        self.assertEqual(response.status_code, 200)
        # check if it matches expectations
        dca = DoubleCountingAgreement.objects.get(producer=self.producer, production_site=self.production_site)
        self.assertEqual(8, DoubleCountingSourcing.objects.filter(dca=dca).count())


    def test_dca_production(self):
        response = self.client.get(reverse('api-v3-doublecount-get-template'), {'file_type':'PRODUCTION'})
        self.assertEqual(response.status_code, 200)        
        # upload template sourcing
        filepath = '%s/web/fixtures/csv/test_data/dca_production.xlsx' % (os.environ['CARBURE_HOME'])
        fh = open(filepath, 'rb')
        data = fh.read()
        fh.close()
        f = SimpleUploadedFile("sourcing.xlsx", data)
        response = self.client.post(reverse('api-v3-doublecount-upload-file'), {'entity_id': self.producer.id, 'production_site_id': self.production_site.id, 'file_type': 'PRODUCTION', 'file': f})
        if response.status_code != 200:
            print('Failed to upload %s' % (filepath))
        self.assertEqual(response.status_code, 200)
        dca = DoubleCountingAgreement.objects.get(producer=self.producer, production_site=self.production_site)
        self.assertEqual(4, DoubleCountingProduction.objects.filter(dca=dca).count())
