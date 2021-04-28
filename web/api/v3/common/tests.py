import datetime
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from core.models import MatierePremiere, Biocarburant, Pays, Entity, ProductionSite, Depot
from certificates.models import ISCCCertificate, DBSCertificate
from api.v3.common.urls import urlpatterns
from django_otp.plugins.otp_email.models import EmailDevice


class CommonAPITest(TestCase):
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
       

    def test_get_mps(self):
        # create matieres premieres
        MatierePremiere.objects.update_or_create(name='MAT1', code='M1')        
        MatierePremiere.objects.update_or_create(name='MAT2', code='M2')        
        MatierePremiere.objects.update_or_create(name='MAT3', code='M3')        
        MatierePremiere.objects.update_or_create(name='BLE', code='BLE')

        url = 'api-v3-public-matieres-premieres'
        response = self.client.get(reverse(url))
        # api works
        self.assertEqual(response.status_code, 200)
        # and returns 4 entries
        self.assertGreaterEqual(len(response.json()['data']), 4)
        # check if querying works
        response = self.client.get(reverse(url) + '?query=bl')
        self.assertEqual(response.status_code, 200)
        # and returns filtered data
        data = response.json()['data']
        self.assertEqual(len(data), 1)

    def test_get_bcs(self):
        # create biocarburants
        Biocarburant.objects.update_or_create(name='BC1', code='BC1')
        Biocarburant.objects.update_or_create(name='BC2', code='BC2')
        Biocarburant.objects.update_or_create(name='BC3', code='BC3')
        Biocarburant.objects.update_or_create(name='Ethanol', code='ETH')

        url = 'api-v3-public-biocarburants'
        response = self.client.get(reverse(url))
        # api works
        self.assertEqual(response.status_code, 200)
        # and returns 4 entries
        self.assertGreaterEqual(len(response.json()['data']), 4)
        # check if querying works
        response = self.client.get(reverse(url) + '?query=anol')
        self.assertEqual(response.status_code, 200)
        # and returns filtered data
        data = response.json()['data']
        self.assertEqual(len(data), 1)
    
    def test_get_countries(self):
        # create countries
        Pays.objects.update_or_create(name='Honduras', code_pays='HONDA')
        Pays.objects.update_or_create(name='Voituristan', code_pays='VTN')
        Pays.objects.update_or_create(name='Rose Island', code_pays='RS')
        Pays.objects.update_or_create(name='Catalogne', code_pays='CAT')

        url = 'api-v3-public-countries'
        response = self.client.get(reverse(url))
        # api works
        self.assertEqual(response.status_code, 200)
        # and returns 4 entries
        self.assertGreaterEqual(len(response.json()['data']), 4)
        # check if querying works
        response = self.client.get(reverse(url) + '?query=isl')
        self.assertEqual(response.status_code, 200)
        # and returns filtered data
        data = response.json()['data']
        self.assertEqual(len(data), 1)

    def test_get_ges(self):
        pass

    def test_get_entities(self):
        # create entities
        Entity.objects.update_or_create(name='Prod1', entity_type='Producteur')
        Entity.objects.update_or_create(name='op1', entity_type='Opérateur')
        Entity.objects.update_or_create(name='tr1', entity_type='Trader')
        Entity.objects.update_or_create(name='adm1', entity_type='Administration')

        url = 'api-v3-public-get-entities'
        response = self.client.get(reverse(url))
        # api works
        self.assertEqual(response.status_code, 200)
        # and returns 4 entries
        self.assertGreaterEqual(len(response.json()['data']), 4)
        # check if querying works
        response = self.client.get(reverse(url) + '?query=op')
        self.assertEqual(response.status_code, 200)
        # and returns filtered data
        data = response.json()['data']
        self.assertEqual(len(data), 1)

    def test_get_producers(self):
        # create entities
        Entity.objects.update_or_create(name='Prod1', entity_type='Producteur')
        Entity.objects.update_or_create(name='Prod2', entity_type='Producteur')
        Entity.objects.update_or_create(name='op1', entity_type='Opérateur')
        Entity.objects.update_or_create(name='tr1', entity_type='Trader')
        Entity.objects.update_or_create(name='adm1', entity_type='Administration')

        url = 'api-v3-public-get-producers'
        response = self.client.get(reverse(url))
        # api works
        self.assertEqual(response.status_code, 200)
        # and returns 4 entries
        self.assertGreaterEqual(len(response.json()['data']), 2)
        # check if querying works
        response = self.client.get(reverse(url) + '?query=od2')
        self.assertEqual(response.status_code, 200)
        # and returns filtered data
        data = response.json()['data']
        self.assertEqual(len(data), 1)

    def test_get_operators(self):
        # create entities
        Entity.objects.update_or_create(name='Prod1', entity_type='Producteur')
        Entity.objects.update_or_create(name='Prod2', entity_type='Producteur')
        Entity.objects.update_or_create(name='op1', entity_type='Opérateur')
        Entity.objects.update_or_create(name='op2', entity_type='Opérateur')
        Entity.objects.update_or_create(name='tr1', entity_type='Trader')
        Entity.objects.update_or_create(name='adm1', entity_type='Administration')

        url = 'api-v3-public-get-operators'
        response = self.client.get(reverse(url))
        # api works
        self.assertEqual(response.status_code, 200)
        # and returns 4 entries
        self.assertGreaterEqual(len(response.json()['data']), 2)
        # check if querying works
        response = self.client.get(reverse(url) + '?query=op2')
        self.assertEqual(response.status_code, 200)
        # and returns filtered data
        data = response.json()['data']
        self.assertEqual(len(data), 1)

    def test_get_traders(self):
        # create entities
        Entity.objects.update_or_create(name='Prod1', entity_type='Producteur')
        Entity.objects.update_or_create(name='Prod2', entity_type='Producteur')
        Entity.objects.update_or_create(name='op1', entity_type='Opérateur')
        Entity.objects.update_or_create(name='op2', entity_type='Opérateur')
        Entity.objects.update_or_create(name='tr1', entity_type='Trader')
        Entity.objects.update_or_create(name='tr2', entity_type='Trader')
        Entity.objects.update_or_create(name='adm1', entity_type='Administration')

        url = 'api-v3-public-get-traders'
        response = self.client.get(reverse(url))
        # api works
        self.assertEqual(response.status_code, 200)
        # and returns 4 entries
        self.assertGreaterEqual(len(response.json()['data']), 2)
        # check if querying works
        response = self.client.get(reverse(url) + '?query=tr1')
        self.assertEqual(response.status_code, 200)
        # and returns filtered data
        data = response.json()['data']
        self.assertEqual(len(data), 1)    

    def test_get_delivery_sites(self):
        # create delivery sites
        fr, _ = Pays.objects.update_or_create(name='France', code_pays='FR')
        Depot.objects.update_or_create(name='Depot1', depot_id='007', country=fr)
        Depot.objects.update_or_create(name='Gennevilliers', depot_id='042', country=fr)
        Depot.objects.update_or_create(name='Gennevilliers 2', depot_id='043', country=fr)
        Depot.objects.update_or_create(name='Carcassonne', depot_id='044', country=fr)

        url = 'api-v3-public-get-delivery-sites'
        response = self.client.get(reverse(url))
        # api works
        self.assertEqual(response.status_code, 200)
        # and returns 4 entries
        self.assertGreaterEqual(len(response.json()['data']), 2)
        # check if querying works
        response = self.client.get(reverse(url) + '?query=carca')
        self.assertEqual(response.status_code, 200)
        # and returns filtered data
        data = response.json()['data']
        self.assertEqual(len(data), 1)    

    def test_get_production_sites(self):
        # create production sites
        producer, _ = Entity.objects.update_or_create(name='toto', entity_type='Producteur')
        fr, _ = Pays.objects.update_or_create(name='France', code_pays='FR')
        today = datetime.date.today()
        ProductionSite.objects.update_or_create(name='Usine1', producer_id=producer.id, country=fr, date_mise_en_service=today)
        ProductionSite.objects.update_or_create(name='Usine2', producer_id=producer.id, country=fr, date_mise_en_service=today)
        ProductionSite.objects.update_or_create(name='Usine3', producer_id=producer.id, country=fr, date_mise_en_service=today)
        ProductionSite.objects.update_or_create(name='Usine4', producer_id=producer.id, country=fr, date_mise_en_service=today)

        url = 'api-v3-public-get-production-sites'
        response = self.client.get(reverse(url))
        # api works
        self.assertEqual(response.status_code, 200)
        # and returns 4 entries
        self.assertGreaterEqual(len(response.json()['data']), 2)
        # check if querying works
        response = self.client.get(reverse(url) + '?query=ne3')
        self.assertEqual(response.status_code, 200)
        # and returns filtered data
        data = response.json()['data']
        self.assertEqual(len(data), 1)    

    def test_get_iscc_certificates(self):
        # create iscc certificates
        today = datetime.date.today()
        ISCCCertificate.objects.update_or_create(certificate_id='ISCC-TEST-01', valid_from=today, valid_until=today)
        ISCCCertificate.objects.update_or_create(certificate_id='ISCC-TEST-02', valid_from=today, valid_until=today)
        ISCCCertificate.objects.update_or_create(certificate_id='ISCC-TEST-03', valid_from=today, valid_until=today)
        ISCCCertificate.objects.update_or_create(certificate_id='ISCC-TST-04', valid_from=today, valid_until=today)

        url = 'api-v3-public-search-iscc-certificates'
        response = self.client.get(reverse(url))
        # api works
        self.assertEqual(response.status_code, 200)
        # and returns 4 entries
        self.assertGreaterEqual(len(response.json()['data']), 2)
        # check if querying works
        response = self.client.get(reverse(url) + '?query=tst')
        self.assertEqual(response.status_code, 200)
        # and returns filtered data
        data = response.json()['data']
        self.assertEqual(len(data), 1)            

    def test_get_2bs_certificates(self):
        # create 2bs certificates
        today = datetime.date.today()
        DBSCertificate.objects.update_or_create(certificate_id='DBS-TEST-01', valid_from=today, valid_until=today)
        DBSCertificate.objects.update_or_create(certificate_id='DBS-TEST-02', valid_from=today, valid_until=today)
        DBSCertificate.objects.update_or_create(certificate_id='DBS-TEST-03', valid_from=today, valid_until=today)
        DBSCertificate.objects.update_or_create(certificate_id='DBS-TST-04', valid_from=today, valid_until=today)

        url = 'api-v3-public-search-2bs-certificates'
        response = self.client.get(reverse(url))
        # api works
        self.assertEqual(response.status_code, 200)
        # and returns 4 entries
        self.assertGreaterEqual(len(response.json()['data']), 2)
        # check if querying works
        response = self.client.get(reverse(url) + '?query=tst')
        self.assertEqual(response.status_code, 200)
        # and returns filtered data
        data = response.json()['data']
        self.assertEqual(len(data), 1)         


    def test_create_delivery_site(self):
        # check how many sites exist
        urlget = 'api-v3-public-get-delivery-sites'
        urlpost = 'api-v3-public-create-delivery-site'
        response = self.client.get(reverse(urlget))
        # api works
        self.assertEqual(response.status_code, 200)
        prev_len = len(response.json()['data'])

        # create a new one
        usa, _ = Pays.objects.update_or_create(name='USA', code_pays='US')
        response = self.client.post(reverse(urlpost), {'name': 'Hangar 18', 'city': 'Roswell', 'country_code': usa.code_pays,
        'depot_id': 'US666', 'depot_type': 'EFS', 'address': 'Route 66', 'postal_code': '91210'})
        # api works
        self.assertEqual(response.status_code, 200)

        # check that we have one more than before
        response = self.client.get(reverse(urlget))
        self.assertEqual(prev_len + 1, len(response.json()['data']))