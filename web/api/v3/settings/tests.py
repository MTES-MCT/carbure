import datetime
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from core.models import Entity, UserRights, Pays, MatierePremiere, Biocarburant, Depot, EntityDepot
from core.models import ISCCCertificate, DBSCertificate
from producers.models import ProductionSite, ProductionSiteInput, ProductionSiteOutput
from api.v3.admin.urls import urlpatterns


class SettingsAPITest(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user_email = 'testuser1@toto.com'
        self.user_password = 'totopouet'
        self.user1 = user_model.objects.create_user(email=self.user_email, name='Le Super Testeur 1', password=self.user_password)

        # a few entities
        self.entity1, _ = Entity.objects.update_or_create(name='Le Super Producteur 1', entity_type='Producteur')
        self.entity2, _ = Entity.objects.update_or_create(name='Le Super Operateur 1', entity_type='Opérateur')
        self.entity3, _ = Entity.objects.update_or_create(name='Le Super Trader 1', entity_type='Trader')

        # some rights
        UserRights.objects.update_or_create(user=self.user1, entity=self.entity1)
        UserRights.objects.update_or_create(user=self.user1, entity=self.entity2)         

        loggedin = self.client.login(username=self.user_email, password=self.user_password)
        self.assertTrue(loggedin)

    def test_get_settings(self):
        url = 'api-v3-settings-get'
        response = self.client.get(reverse(url))
        # api works
        self.assertEqual(response.status_code, 200)
        data = response.json()['data']
        self.assertIn('rights', data)
        self.assertIn('email', data)
        self.assertIn('requests', data)

    def test_mac_option(self):
        url_enable = 'api-v3-settings-enable-mac'
        url_disable = 'api-v3-settings-disable-mac'

        # wrongly formatted
        response = self.client.post(reverse(url_enable), {'entity_id':'blablabla'})
        self.assertEqual(response.status_code, 400)
        # no entity_id
        response = self.client.post(reverse(url_enable))
        self.assertEqual(response.status_code, 400)
        # entity I do not belong to
        response = self.client.post(reverse(url_enable), {'entity_id': self.entity3.id})
        self.assertEqual(response.status_code, 403)
        # should pass
        response = self.client.post(reverse(url_enable), {'entity_id': self.entity2.id})
        self.assertEqual(response.status_code, 200)
        entity = Entity.objects.get(id=self.entity2.id)
        self.assertEqual(entity.has_mac, True)

        # disable:
        # wrongly formatted
        response = self.client.post(reverse(url_disable), {'entity_id':'blablabla'})
        self.assertEqual(response.status_code, 400)
        # no entity_id
        response = self.client.post(reverse(url_disable))
        self.assertEqual(response.status_code, 400)
        # entity I do not belong to
        response = self.client.post(reverse(url_disable), {'entity_id': self.entity3.id})
        self.assertEqual(response.status_code, 403)
        # should pass
        response = self.client.post(reverse(url_disable), {'entity_id': self.entity2.id})
        self.assertEqual(response.status_code, 200)
        entity = Entity.objects.get(id=self.entity2.id)
        self.assertEqual(entity.has_mac, False)        

        # revert
        response = self.client.post(reverse(url_enable), {'entity_id': self.entity2.id})
        self.assertEqual(response.status_code, 200)
        entity = Entity.objects.get(id=self.entity2.id)
        self.assertEqual(entity.has_mac, True)

    def test_trading_option(self):
        url_enable = 'api-v3-settings-enable-trading'
        url_disable = 'api-v3-settings-disable-trading'

        # wrongly formatted
        response = self.client.post(reverse(url_enable), {'entity_id':'blablabla'})
        self.assertEqual(response.status_code, 400)
        # no entity_id
        response = self.client.post(reverse(url_enable))
        self.assertEqual(response.status_code, 400)
        # entity I do not belong to
        response = self.client.post(reverse(url_enable), {'entity_id': self.entity3.id})
        self.assertEqual(response.status_code, 403)
        # should pass
        response = self.client.post(reverse(url_enable), {'entity_id': self.entity1.id})
        self.assertEqual(response.status_code, 200)
        entity = Entity.objects.get(id=self.entity1.id)
        self.assertEqual(entity.has_trading, True)

        # disable:
        # wrongly formatted
        response = self.client.post(reverse(url_disable), {'entity_id':'blablabla'})
        self.assertEqual(response.status_code, 400)
        # no entity_id
        response = self.client.post(reverse(url_disable))
        self.assertEqual(response.status_code, 400)
        # entity I do not belong to
        response = self.client.post(reverse(url_disable), {'entity_id': self.entity3.id})
        self.assertEqual(response.status_code, 403)
        # should pass
        response = self.client.post(reverse(url_disable), {'entity_id': self.entity1.id})
        self.assertEqual(response.status_code, 200)
        entity = Entity.objects.get(id=self.entity1.id)
        self.assertEqual(entity.has_trading, False)        

        # revert
        response = self.client.post(reverse(url_enable), {'entity_id': self.entity1.id})
        self.assertEqual(response.status_code, 200)
        entity = Entity.objects.get(id=self.entity1.id)
        self.assertEqual(entity.has_trading, True)

        # should not work on Operator
        response = self.client.post(reverse(url_enable), {'entity_id': self.entity2.id})
        self.assertEqual(response.status_code, 400)

    def test_set_national_system_certificate(self):
        url = 'api-v3-settings-set-national-system-certificate'
        certificate_id = 'SV-BLABLABLA'

        # wrongly formatted arg
        response = self.client.post(reverse(url), {'entity_id': 'TOTO', 'national_system_certificate': certificate_id})
        self.assertEqual(response.status_code, 400)        
        # missing arguments
        response = self.client.post(reverse(url), {'entity_id': self.entity2.id})
        self.assertEqual(response.status_code, 400)
        response = self.client.post(reverse(url), {'national_system_certificate': certificate_id})
        self.assertEqual(response.status_code, 400)

        # reject if trader
        response = self.client.post(reverse(url), {'entity_id': self.entity3.id, 'national_system_certificate': certificate_id})
        self.assertEqual(response.status_code, 403)        

        # should pass
        response = self.client.post(reverse(url), {'entity_id': self.entity2.id, 'national_system_certificate': certificate_id})
        self.assertEqual(response.status_code, 200)
        # check
        entity = Entity.objects.get(id=self.entity2.id)
        self.assertEqual(entity.national_system_certificate, certificate_id)


    def test_production_sites_settings(self):
        url_get = 'api-v3-settings-get-production-sites'
        url_add = 'api-v3-settings-add-production-site'
        url_update = 'api-v3-settings-update-production-site'
        url_delete = 'api-v3-settings-delete-production-site'
        url_set_mps = 'api-v3-settings-set-production-site-matieres-premieres'
        url_set_bcs = 'api-v3-settings-set-production-site-biocarburants'

        # get - 0 sites
        response = self.client.get(reverse(url_get), {'entity_id': self.entity1.id})
        self.assertEqual(response.status_code, 200)
        data = response.json()['data']
        self.assertEqual(len(data), 0)
        # add 1
        france, _ = Pays.objects.update_or_create(code_pays='FR', name='France')
        psite = {'country_code':'FR', 'name':'Site prod 1', 
                 'date_mise_en_service': '2020-12-01', 'ges_option': 'ACTUAL', 
                 'entity_id': self.entity1.id, 'eligible_dc': 'true', 
                 'dc_reference': 'DC-FR-12-493', 'site_id': 'FR0001', 
                 'city':'Seynod', 'postal_code':'74600', 
                 'manager_name':'Gaston Gasoil', 'manager_phone': '0145247000', 
                 'manager_email':'g.gasoil@superpetrole.com'}
        response = self.client.post(reverse(url_add), psite)
        self.assertEqual(response.status_code, 200)        
        # check in db
        site = ProductionSite.objects.get(site_id='FR0001')
        # update 
        psite['postal_code'] = '75018'
        psite['production_site_id'] = site.id
        response = self.client.post(reverse(url_update), psite)
        self.assertEqual(response.status_code, 200)   
        site = ProductionSite.objects.get(site_id='FR0001')
        self.assertEqual(site.postal_code, '75018')
        # set mps/bcs
        MatierePremiere.objects.update_or_create(code='COLZA', name='Colza')
        MatierePremiere.objects.update_or_create(code='BEETROOT', name='Betterave')
        Biocarburant.objects.update_or_create(code='ETH', name='Ethanol')
        Biocarburant.objects.update_or_create(code='HVO', name='HVO')

        response = self.client.post(reverse(url_set_mps), {'production_site_id': site.id, 'matiere_premiere_codes': ['COLZA', 'BEETROOT']})
        self.assertEqual(response.status_code, 200)   
        response = self.client.post(reverse(url_set_bcs), {'production_site_id': site.id, 'biocarburant_codes': ['ETH', 'HVO']})
        self.assertEqual(response.status_code, 200)   
        # check
        inputs = ProductionSiteInput.objects.filter(production_site=site)
        outputs = ProductionSiteOutput.objects.filter(production_site=site)
        self.assertEqual(len(inputs), 2)
        self.assertEqual(len(outputs), 2)

        # delete
        response = self.client.post(reverse(url_delete), psite)
        self.assertEqual(response.status_code, 200)   
        # get - 0 sites
        response = self.client.get(reverse(url_get), {'entity_id': self.entity1.id})
        self.assertEqual(response.status_code, 200)
        data = response.json()['data']
        self.assertEqual(len(data), 0)

    def test_delivery_sites_settings(self):
        url_get = 'api-v3-settings-get-delivery-sites'
        url_add = 'api-v3-settings-add-delivery-site'
        url_delete = 'api-v3-settings-delete-delivery-site'
        # get 0
        response = self.client.get(reverse(url_get), {'entity_id': self.entity1.id})
        self.assertEqual(response.status_code, 200)
        data = response.json()['data']
        self.assertEqual(len(data), 0)
        # add
        france, _ = Pays.objects.update_or_create(code_pays='FR', name='France')
        depot, _ = Depot.objects.update_or_create(depot_id='TEST', name='toto', city='paris', country=france)
        postdata = {'entity_id': self.entity1.id, 'delivery_site_id': depot.depot_id, 'ownership_type': 'OWN'}
        response = self.client.post(reverse(url_add), postdata)
        self.assertEqual(response.status_code, 200)
        # get 1
        response = self.client.get(reverse(url_get), {'entity_id': self.entity1.id})
        self.assertEqual(response.status_code, 200)
        data = response.json()['data']
        self.assertEqual(len(data), 1)
        # delete
        response = self.client.post(reverse(url_delete), {'entity_id': self.entity1.id, 'delivery_site_id':depot.depot_id})
        self.assertEqual(response.status_code, 200)        
        # get 0
        response = self.client.get(reverse(url_get), {'entity_id': self.entity1.id})
        self.assertEqual(response.status_code, 200)
        data = response.json()['data']
        self.assertEqual(len(data), 0)

    def test_iscc_certificates(self):
        url_get = 'api-v3-settings-get-iscc-certificates'
        url_add = 'api-v3-settings-add-iscc-certificate'
        url_delete = 'api-v3-settings-delete-iscc-certificate'
        # get 0
        response = self.client.get(reverse(url_get), {'entity_id': self.entity1.id})
        self.assertEqual(response.status_code, 200)
        data = response.json()['data']
        self.assertEqual(len(data), 0)        
        # add 1
        certid = 'ISCC-TEST-01'
        today = datetime.date.today()
        crtdata = {'certificate_holder': 'MTES Robot', 'addons':'', 
        'valid_from':today, 'valid_until':today, 'issuing_cb':'veritas', 
        'location':'paris', 'download_link':'http://localhost/test.pdf'}
        crt, _ = ISCCCertificate.objects.update_or_create(certificate_id=certid, defaults=crtdata)
        postdata = {'entity_id': self.entity1.id, 'certificate_id': certid}
        response = self.client.post(reverse(url_add), postdata)
        self.assertEqual(response.status_code, 200)        
        # get 1
        response = self.client.get(reverse(url_get), {'entity_id': self.entity1.id})
        self.assertEqual(response.status_code, 200)
        data = response.json()['data']
        self.assertEqual(len(data), 1)            
        # delete 1
        postdata = {'entity_id': self.entity1.id, 'certificate_id': certid}
        response = self.client.post(reverse(url_delete), postdata)
        self.assertEqual(response.status_code, 200)
        # get 0
        response = self.client.get(reverse(url_get), {'entity_id': self.entity1.id})
        self.assertEqual(response.status_code, 200)
        data = response.json()['data']
        self.assertEqual(len(data), 0)

    def test_2bs_certificates(self):
        url_get = 'api-v3-settings-get-2bs-certificates'
        url_add = 'api-v3-settings-add-2bs-certificate'
        url_delete = 'api-v3-settings-delete-2bs-certificate'
        # get 0
        response = self.client.get(reverse(url_get), {'entity_id': self.entity1.id})
        self.assertEqual(response.status_code, 200)
        data = response.json()['data']
        self.assertEqual(len(data), 0)        
        # add 1
        certid = '2BS-TEST-01'
        today = datetime.date.today()
        crtdata = {'certificate_holder': 'MTES Robot', 
        'valid_from':today, 'valid_until':today, 'holder_address':'paris france', 
        'certification_type':'TST TST', 'download_link':'http://localhost/test.pdf'}
        crt, _ = DBSCertificate.objects.update_or_create(certificate_id=certid, defaults=crtdata)
        postdata = {'entity_id': self.entity1.id, 'certificate_id': certid}
        response = self.client.post(reverse(url_add), postdata)
        self.assertEqual(response.status_code, 200)        
        # get 1
        response = self.client.get(reverse(url_get), {'entity_id': self.entity1.id})
        self.assertEqual(response.status_code, 200)
        data = response.json()['data']
        self.assertEqual(len(data), 1)            
        # delete 1
        postdata = {'entity_id': self.entity1.id, 'certificate_id': certid}
        response = self.client.post(reverse(url_delete), postdata)
        self.assertEqual(response.status_code, 200)
        # get 0
        response = self.client.get(reverse(url_get), {'entity_id': self.entity1.id})
        self.assertEqual(response.status_code, 200)
        data = response.json()['data']
        self.assertEqual(len(data), 0)           

    def test_advanced_certificates_behaviour(self):
        # get my certificates 0
        url_get_crts = 'api-v3-settings-get-my-certificates'
        response = self.client.get(reverse(url_get_crts), {'entity_id': self.entity1.id})
        self.assertEqual(response.status_code, 200)
        data = response.json()['data']
        self.assertEqual(len(data), 0)           
        # add 1 iscc and 1 2bs certificate
        ## start by creating iscc cert
        certid1 = 'ISCC-TEST-01'
        today = datetime.date.today()
        crtdata = {'certificate_holder': 'MTES Robot', 'addons':'', 
        'valid_from':today, 'valid_until':today, 'issuing_cb':'veritas', 
        'location':'paris', 'download_link':'http://localhost/test.pdf'}
        crt, _ = ISCCCertificate.objects.update_or_create(certificate_id=certid1, defaults=crtdata)
        ## then 2bs
        certid2 = '2BS-TEST-01'
        crtdata = {'certificate_holder': 'MTES Robot', 
        'valid_from':today, 'valid_until':today, 'holder_address':'paris france', 
        'certification_type':'TST TST', 'download_link':'http://localhost/test.pdf'}
        crt, _ = DBSCertificate.objects.update_or_create(certificate_id=certid2, defaults=crtdata)        
        ## add those certificates to my company
        postdata = {'entity_id': self.entity1.id, 'certificate_id': certid1}
        response = self.client.post(reverse('api-v3-settings-add-iscc-certificate'), postdata)
        self.assertEqual(response.status_code, 200)     
        postdata = {'entity_id': self.entity1.id, 'certificate_id': certid2}
        response = self.client.post(reverse('api-v3-settings-add-2bs-certificate'), postdata)
        self.assertEqual(response.status_code, 200)             
        ## and a production site
        france, _ = Pays.objects.update_or_create(code_pays='FR', name='France')
        psite = {'country_code':'FR', 'name':'Site prod 1', 
                 'date_mise_en_service': '2020-12-01', 'ges_option': 'ACTUAL', 
                 'entity_id': self.entity1.id, 'eligible_dc': 'true', 
                 'dc_reference': 'DC-FR-12-493', 'site_id': 'FR0001', 
                 'city':'Seynod', 'postal_code':'74600', 
                 'manager_name':'Gaston Gasoil', 'manager_phone': '0145247000', 
                 'manager_email':'g.gasoil@superpetrole.com'}
        ## add the production site to my company
        response = self.client.post(reverse('api-v3-settings-add-production-site'), psite)
        self.assertEqual(response.status_code, 200)        
        site = ProductionSite.objects.get(site_id='FR0001')
        # set iscc certificate and 2bs certificate to production site
        postdata = {'entity_id': self.entity1.id, 'production_site_id': site.id, 'certificate_ids': [certid1, certid2]}
        response = self.client.post(reverse('api-v3-settings-set-production-site-certificates'), postdata)
        self.assertEqual(response.status_code, 200)        
        # get my certificates 2
        response = self.client.get(reverse(url_get_crts), {'entity_id': self.entity1.id})
        self.assertEqual(response.status_code, 200)
        data = response.json()['data']
        self.assertEqual(len(data), 2)
        # get-production sites, check if they contain the certificates
        response = self.client.get(reverse('api-v3-settings-get-production-sites'), {'entity_id': self.entity1.id})
        self.assertEqual(response.status_code, 200)
        data = response.json()['data']
        self.assertEqual(len(data), 1)
        psite = data[0]
        self.assertEqual(len(psite['certificates']), 2)
        # update-iscc certificate
        ## start by creating a new certificate
        certid1bis = 'ISCC-TEST-02'
        crtdata = {'certificate_holder': 'MTES Robot', 'addons':'', 
        'valid_from':today, 'valid_until':today, 'issuing_cb':'veritas', 
        'location':'paris', 'download_link':'http://localhost/test.pdf'}
        crt, _ = ISCCCertificate.objects.update_or_create(certificate_id=certid1bis, defaults=crtdata)        
        ## then call update method
        postdata = {'entity_id': self.entity1.id, 'old_certificate_id': certid1, 'new_certificate_id': certid1bis}
        response = self.client.post(reverse('api-v3-settings-update-iscc-certificate'), postdata)
        self.assertEqual(response.status_code, 200)    

        # update 2bs certificate
        ## start by creating a new certificate
        certid2bis = '2BS-TEST-02'
        crtdata = {'certificate_holder': 'MTES Robot', 
        'valid_from':today, 'valid_until':today, 'holder_address':'paris france', 
        'certification_type':'TST TST', 'download_link':'http://localhost/test.pdf'}
        crt, _ = DBSCertificate.objects.update_or_create(certificate_id=certid2bis, defaults=crtdata)          
        ## then call update method
        postdata = {'entity_id': self.entity1.id, 'old_certificate_id': certid2, 'new_certificate_id': certid2bis}
        response = self.client.post(reverse('api-v3-settings-update-2bs-certificate'), postdata)
        self.assertEqual(response.status_code, 200)    
        # get-production sites, check if they contain the updated certificates
        response = self.client.get(reverse('api-v3-settings-get-production-sites'), {'entity_id': self.entity1.id})
        self.assertEqual(response.status_code, 200)
        data = response.json()['data']
        self.assertEqual(len(data), 1)
        psite = data[0]
        self.assertEqual(len(psite['certificates']), 2)
        for c in psite['certificates']:
            if c['type'] == 'ISCC':
                self.assertEqual(c['certificate_id'], certid1bis)
            if c['type'] == '2BS':
                self.assertEqual(c['certificate_id'], certid2bis)


    def test_entity_access_request(self):
        # get settings - 0 pending requests
        url = 'api-v3-settings-get'
        response = self.client.get(reverse(url))
        self.assertEqual(response.status_code, 200)
        data = response.json()['data']
        self.assertIn('requests', data)
        prev_len = len(data['requests'])

        e, _ = Entity.objects.update_or_create(name='Entity test', entity_type='Producteur')
        postdata = {'entity_id': e.id, 'comment': ''}
        response = self.client.post(reverse('api-v3-settings-request-entity-access'), postdata)
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse(url))
        self.assertEqual(response.status_code, 200)
        data = response.json()['data']
        new_len = len(data['requests'])
        self.assertEqual(prev_len + 1, new_len)

