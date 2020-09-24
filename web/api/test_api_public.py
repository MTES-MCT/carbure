from django.test import TestCase
from django.urls import reverse

from core.models import Biocarburant, MatierePremiere, Pays, Entity, Depot
import json


class PublicApiTest(TestCase):
    def setUp(self):
        Biocarburant.objects.update_or_create(name="Biogaz", code="BG")
        Biocarburant.objects.update_or_create(name="Bioethanol", code="BE")

        MatierePremiere.objects.update_or_create(name="Colza", code="COLZA")
        MatierePremiere.objects.update_or_create(name="Maïs", code="MAIS")
        MatierePremiere.objects.update_or_create(name="Huiles végétales diverses", code="HVD")

        france, c = Pays.objects.update_or_create(name='France', code_pays='FR')
        Pays.objects.update_or_create(name='Portugal', code_pays='PO')

        Entity.objects.update_or_create(name="BIORAF1", entity_type="Producteur")
        Entity.objects.update_or_create(name="BIORAF2", entity_type="Producteur")
        Entity.objects.update_or_create(name="BIORAF3", entity_type="Producteur")

        Entity.objects.update_or_create(name="OP1", entity_type="Opérateur")
        Entity.objects.update_or_create(name="OP2", entity_type="Opérateur")
        Entity.objects.update_or_create(name="OP3", entity_type="Opérateur")

        Entity.objects.update_or_create(name="DGEC", entity_type="Administration")
        Entity.objects.update_or_create(name="Douane", entity_type="Administration")

        Depot.objects.update_or_create(name="DEPOTTEST", depot_id="111", city="Paris", country=france)

    def test_bc_autocomplete(self):
        base_url = reverse('api-biocarburant-autocomplete')
        url = base_url + "?query=W"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data, {'suggestions': []})

        url = base_url + "?query=B"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data, {'suggestions': [{"value": "Biogaz", "description": "", "data": "BG"},
                                                {"value": "Bioethanol", "description": "", "data": "BE"}]})

    def test_mp_autocomplete(self):
        base_url = reverse('api-matiere-premiere-autocomplete')
        url = base_url + "?query=W"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data, {'suggestions': []})

        url = base_url + "?query=A"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data, {'suggestions': [{'value': 'Colza', 'description': '', 'data': 'COLZA'},
                                                {'value': 'Maïs', 'description': '', 'data': 'MAIS'},
                                                {'value': 'Huiles végétales diverses', 'description': '', 'data': 'HVD'}
                                                ]})

    def test_country_autocomplete(self):
        base_url = reverse('api-country-autocomplete')
        url = base_url + "?query=W"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data, {'suggestions': []})

        url = base_url + "?query=A"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data, {'suggestions': [{'data': 'FR', 'value': 'France'},
                                                {'data': 'PO', 'value': 'Portugal'}]})

    def test_operators_autocomplete(self):
        base_url = reverse('api-operators-autocomplete')
        # test with no results
        url = base_url + "?query=W"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data, {'suggestions': []})

        # test with 3 results
        url = base_url + "?query=OP"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data['suggestions']), 3)

        # test pattern matching producers name that should return 0
        url = base_url + "?query=BIO"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data['suggestions']), 0)

    def test_depots_autocomplete(self):
        base_url = reverse('api-depots-autocomplete')
        # test with no results
        url = base_url + "?query=W"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data, {'suggestions': []})

        # test with a results
        url = base_url + "?query=DEP"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data['suggestions']), 1)

    def test_bc_csv(self):
        url = reverse('api-biocarburant-csv')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'biocarburant_code;biocarburant\r\nBG;Biogaz\r\nBE;Bioethanol\r\n')

    def test_mp_csv(self):
        url = reverse('api-matiere-premiere-csv')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'matiere_premiere_code;matiere_premiere\r\nCOLZA;Colza\r\nMAIS;\
Ma\xc3\xafs\r\nHVD;Huiles v\xc3\xa9g\xc3\xa9tales diverses\r\n')

    def test_country_csv(self):
        url = reverse('api-country-csv')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'code_pays;pays\r\nFR;France\r\nPO;Portugal\r\n')

    def test_operators_csv(self):
        url = reverse('api-operators-csv')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'ea\r\nOP1\r\nOP2\r\nOP3\r\n')

    def test_depots_csv(self):
        url = reverse('api-depots-csv')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'name;depot_id;city\r\nDEPOTTEST;111;Paris\r\n')