from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from core.models import Entity, UserRights, Pays, MatierePremiere, Biocarburant, Depot, LotTransaction

from producers.models import ProductionSite


import datetime
import json


class TestProducer(TestCase):
    def setUp(self):
        user_model = get_user_model()
        # create a producer
        self.producer_user = user_model.objects.create_user(email='testproducer@almalexia.org', name='MP TEST', password='totopouet42')
        self.producer_entity, created = Entity.objects.update_or_create(name='BioRaf1', entity_type='Producteur')
        right, created = UserRights.objects.update_or_create(user=self.producer_user, entity=self.producer_entity)

        # create an operator
        self.operator_user = user_model.objects.create_user(email='testoperator@almalexia.org', name='MP TEST', password='totopouet42')
        self.operator_entity, created = Entity.objects.update_or_create(name='PETRO1', entity_type='Opérateur')
        right, created = UserRights.objects.update_or_create(user=self.operator_user, entity=self.operator_entity)

        # login with producer info
        self.client.login(username='testproducer@almalexia.org', password='totopouet42')

        # setup plenty of data to work with
        self.country, created = Pays.objects.update_or_create(code_pays='VTN', name='Voituristan')
        self.mp, created = MatierePremiere.objects.update_or_create(code='CA', name='CAILLOU')
        self.biocarburant, created = Biocarburant.objects.update_or_create(code='EL', name='Électricité')

        # create production site
        self.production_site, created = ProductionSite.objects.update_or_create(producer=self.producer_entity, name='production-site-test', country=self.country, defaults={'date_mise_en_service': datetime.date.today()})
        self.delivery_site, created = Depot.objects.update_or_create(depot_id=555, defaults={'name': 'Fake Depot', 'city': 'Jaxu'})

    def test_lot_lifecycle(self):
        # 1 create a draft with invalid data
        # 2 try to validate - fail
        # 3 edit and fix issues
        # 4 try to validate again

        # 1 (invalid country)
        postdata = {'producer_is_in_carbure':'yes', 'carbure_producer_id': self.producer_entity.id, 'unknown_producer': '',
                    'production_site_is_in_carbure': 'yes', 'carbure_production_site_id': self.production_site.id,
                    'unknown_production_site': '', 'unknown_production_site_country': '',
                    'unknown_production_site_com_date': '', 'unknown_production_site_reference': '',
                    'unknown_production_site_dbl_counting': '', 'volume':'1000',
                    'biocarburant_code':'EL', 'matiere_premiere_code':'CA', 'pays_origine_code': 'TOTO', 'eec': 12.0, 'dae': 'FRTOTO123',
                    'client_is_in_carbure': 'yes', 'carbure_client_id': self.operator_entity.id, 'unknown_client':'', 'delivery_date': '2020-03-01',
                    'delivery_site_is_in_carbure': 'yes', 'carbure_delivery_site_id': self.delivery_site.depot_id, 'unknown_delivery_site': ''
                    }
        response = self.client.post(reverse('api-v2-producers-save-lot'), postdata)
        self.assertEqual(response.status_code, 200)
        # {"status": "success", "lot_id": 1, "": 1}
        res = json.loads(response.content)
        tx_id = res['transaction_id']
        lot_id = res['lot_id']

        # 2 try to validate
        response = self.client.post(reverse('api-v2-producers-validate-lots'), {'lots': tx_id})
        res = json.loads(response.content)
        lot = res['message'][0]
        self.assertEqual(lot['status'], 'error')

        # 3 edit and fix
        postdata['pays_origine_code'] = self.country.code_pays
        postdata['lot_id'] = lot_id
        postdata['tx_id'] = tx_id
        response = self.client.post(reverse('api-v2-producers-save-lot'), postdata)
        self.assertEqual(response.status_code, 200)

        # 4 validate again
        response = self.client.post(reverse('api-v2-producers-validate-lots'), {'lots': tx_id})
        res = json.loads(response.content)
        print(res)
        lot = res['message'][0]
        self.assertEqual(lot['status'], 'success')