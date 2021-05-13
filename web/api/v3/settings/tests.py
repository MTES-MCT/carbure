import datetime
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from core.models import Entity, UserRights, Pays, MatierePremiere, Biocarburant, Depot, EntityDepot
from certificates.models import ISCCCertificate, DBSCertificate
from producers.models import ProductionSite, ProductionSiteInput, ProductionSiteOutput
from api.v3.admin.urls import urlpatterns
from django_otp.plugins.otp_email.models import EmailDevice


class SettingsAPITest(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user_email = 'testuser1@toto.com'
        self.user_password = 'totopouet'
        self.user1 = user_model.objects.create_user(email=self.user_email, name='Le Super Testeur 1', password=self.user_password)
        self.user2 = user_model.objects.create_user(email="testuser2@toto.com", name='Le Super Testeur 2', password=self.user_password)

        # a few entities
        self.entity1, _ = Entity.objects.update_or_create(name='Le Super Producteur 1', entity_type='Producteur')
        self.entity2, _ = Entity.objects.update_or_create(name='Le Super Operateur 1', entity_type='Opérateur')
        self.entity3, _ = Entity.objects.update_or_create(name='Le Super Trader 1', entity_type='Trader')

        # some rights
        UserRights.objects.update_or_create(user=self.user1, entity=self.entity1, defaults={'role': UserRights.ADMIN})
        UserRights.objects.update_or_create(user=self.user1, entity=self.entity2, defaults={'role': UserRights.RW})

        loggedin = self.client.login(username=self.user_email, password=self.user_password)
        self.assertTrue(loggedin)
        # pass otp verification
        response = self.client.get(reverse('otp-verify'))
        self.assertEqual(response.status_code, 200)
        device = EmailDevice.objects.get(user=self.user1)
        response = self.client.post(reverse('otp-verify'), {'otp_token': device.token})
        self.assertEqual(response.status_code, 302)

        # some data
        fr, _ = Pays.objects.get_or_create(code_pays='FR', name='France')

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
        # should not pass (not admin)
        response = self.client.post(reverse(url_enable), {'entity_id': self.entity2.id})
        self.assertEqual(response.status_code, 403)
        entity = Entity.objects.get(id=self.entity2.id)
        self.assertEqual(entity.has_mac, False)        
        # should pass
        response = self.client.post(reverse(url_enable), {'entity_id': self.entity1.id})
        self.assertEqual(response.status_code, 200)        
        entity = Entity.objects.get(id=self.entity1.id)
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
        response = self.client.post(reverse(url_disable), {'entity_id': self.entity1.id})
        self.assertEqual(response.status_code, 200)
        entity = Entity.objects.get(id=self.entity1.id)
        self.assertEqual(entity.has_mac, False)        

        # revert
        response = self.client.post(reverse(url_enable), {'entity_id': self.entity1.id})
        self.assertEqual(response.status_code, 200)
        entity = Entity.objects.get(id=self.entity1.id)
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
        # first because we don't have the rights
        response = self.client.post(reverse(url_enable), {'entity_id': self.entity2.id})
        self.assertEqual(response.status_code, 403)
        UserRights.objects.update_or_create(user=self.user1, entity=self.entity2, defaults={'role': UserRights.ADMIN})
        # then because operators cannot trade
        response = self.client.post(reverse(url_enable), {'entity_id': self.entity2.id})
        self.assertEqual(response.status_code, 400)        


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
        response = self.client.post(reverse(url_update), psite)
        self.assertEqual(response.status_code, 400) # update without specifying site_id
        psite['production_site_id'] = site.id
        psite['country_code'] = 'WW'
        response = self.client.post(reverse(url_update), psite)
        self.assertEqual(response.status_code, 400) # unknown country code WW
        psite['country_code'] = 'FR'
        response = self.client.post(reverse(url_update), psite)
        self.assertEqual(response.status_code, 200)
        site = ProductionSite.objects.get(site_id='FR0001')
        self.assertEqual(site.postal_code, '75018')

        # set mps/bcs
        MatierePremiere.objects.update_or_create(code='COLZA', name='Colza')
        MatierePremiere.objects.update_or_create(code='BEETROOT', name='Betterave')
        Biocarburant.objects.update_or_create(code='ETH', name='Ethanol')
        Biocarburant.objects.update_or_create(code='HVO', name='HVO')

        response = self.client.post(reverse(url_set_mps), {'entity_id': self.entity1.id, 'production_site_id': site.id, 'matiere_premiere_codes': ['COLZA', 'BEETROOT']})
        self.assertEqual(response.status_code, 200)
        response = self.client.post(reverse(url_set_bcs), {'entity_id': self.entity1.id, 'production_site_id': site.id, 'biocarburant_codes': ['ETH', 'HVO']})
        self.assertEqual(response.status_code, 200)   
        # check
        inputs = ProductionSiteInput.objects.filter(production_site=site)
        outputs = ProductionSiteOutput.objects.filter(production_site=site)
        self.assertEqual(len(inputs), 2)
        self.assertEqual(len(outputs), 2)

        # delete
        post = {'entity_id': self.entity1.id}
        response = self.client.post(reverse(url_delete), post)
        self.assertEqual(response.status_code, 400)   # missing production_site_id

        post['production_site_id'] = site.id
        response = self.client.post(reverse(url_delete), post)
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
        postdata = {'entity_id': e.id, 'comment': '', 'role': 'RO'}
        response = self.client.post(reverse('api-v3-settings-request-entity-access'), postdata)
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse(url))
        self.assertEqual(response.status_code, 200)
        data = response.json()['data']
        new_len = len(data['requests'])
        self.assertEqual(prev_len + 1, new_len)


    def test_invites(self):
        # try invite/revoke as non-admin
        right = UserRights.objects.get(entity=self.entity1, user=self.user1)
        right.role = UserRights.RO
        right.save()

        url = 'api-v3-settings-invite-user'
        response = self.client.post(reverse(url), {'entity_id': self.entity1.id, 'email': self.user2.email, 'role': UserRights.RO})
        self.assertEqual(response.status_code, 403)        
        url = 'api-v3-settings-revoke-user'
        response = self.client.post(reverse(url), {'entity_id': self.entity1.id, 'email': self.user2.email})
        self.assertEqual(response.status_code, 403)

        UserRights.objects.filter(entity=self.entity1, user=self.user1).update(role=UserRights.ADMIN)
        #invite_nonexisting_user
        url = 'api-v3-settings-invite-user'
        response = self.client.post(reverse(url), {'entity_id': self.entity1.id, 'email': "totopouet@gmail.com", 'role': UserRights.RO})
        self.assertEqual(response.status_code, 400)          
        #test_invite_ro
        url = 'api-v3-settings-invite-user'
        response = self.client.post(reverse(url), {'entity_id': self.entity1.id, 'email': self.user2.email, 'role': UserRights.RO})
        self.assertEqual(response.status_code, 200)
        right = UserRights.objects.get(entity=self.entity1, user=self.user2)
        self.assertEqual(right.role, UserRights.RO)
        #test_invite_rw
        response = self.client.post(reverse(url), {'entity_id': self.entity1.id, 'email': self.user2.email, 'role': UserRights.RW})
        self.assertEqual(response.status_code, 200)
        right = UserRights.objects.get(entity=self.entity1, user=self.user2)
        self.assertEqual(right.role, UserRights.RW)
        #test_invite_admin
        response = self.client.post(reverse(url), {'entity_id': self.entity1.id, 'email': self.user2.email, 'role': UserRights.ADMIN})
        self.assertEqual(response.status_code, 200)
        right = UserRights.objects.get(entity=self.entity1, user=self.user2)
        self.assertEqual(right.role, UserRights.ADMIN)
        #test_invite_auditor (without expiration date)
        response = self.client.post(reverse(url), {'entity_id': self.entity1.id, 'email': self.user2.email, 'role': UserRights.AUDITOR})
        self.assertEqual(response.status_code, 400)
        #test_invite_auditor (with expiration date)
        response = self.client.post(reverse(url), {'entity_id': self.entity1.id, 'email': self.user2.email, 'role': UserRights.AUDITOR, 'expiration_date': '2021-12-01'}) 
        self.assertEqual(response.status_code, 200)
        right = UserRights.objects.get(entity=self.entity1, user=self.user2)
        self.assertEqual(right.role, UserRights.AUDITOR)        
        #test_invite_unknown_role
        response = self.client.post(reverse(url), {'entity_id': self.entity1.id, 'email': self.user2.email, 'role': "tougoudou"})
        self.assertEqual(response.status_code, 400)


    def test_update_entity(self):
        url = 'api-v3-settings-update-entity'
        response = self.client.post(reverse(url), {'entity_id': self.entity1.id, 'legal_name': "MA SOCIETE", "registration_id": "pouet", 
        "sustainability_officer_phone_number": "", "sustainability_officer": "", "registered_address": "24 avenue des Champs Élysées, 2ème étage gauche, 75000 Paris CEDEX 12, France"})
        self.assertEqual(response.status_code, 200)

    def test_add_production_site(self):
        postdata = {'entity_id': self.entity2.id}
        url = 'api-v3-settings-add-production-site'
        response = self.client.post(reverse(url), postdata)
        self.assertEqual(response.status_code, 400) 
        self.assertEqual(response.json()['message'], "SETTINGS_ADD_PRODUCTION_SITE_MISSING_COUNTRY_CODE")
        postdata['country_code'] = 'ZZ'
        response = self.client.post(reverse(url), postdata)
        self.assertEqual(response.status_code, 400) 
        self.assertEqual(response.json()['message'], "SETTINGS_ADD_PRODUCTION_SITE_MISSING_NAME")
        postdata['name'] = 'Site de production 007'
        response = self.client.post(reverse(url), postdata)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['message'], "SETTINGS_ADD_PRODUCTION_SITE_MISSING_COM_DATE")
        postdata['date_mise_en_service'] = '12/05/2007'
        response = self.client.post(reverse(url), postdata)
        self.assertEqual(response.status_code, 400) 
        self.assertEqual(response.json()['message'], "SETTINGS_ADD_PRODUCTION_SITE_MISSING_GHG_OPTION")        
        postdata['ges_option'] = 'DEFAULT'
        response = self.client.post(reverse(url), postdata)
        self.assertEqual(response.status_code, 400) 
        self.assertEqual(response.json()['message'], "SETTINGS_ADD_PRODUCTION_SITE_MISSING_ID")
        postdata['site_id'] = 'FR78895468'
        response = self.client.post(reverse(url), postdata)
        self.assertEqual(response.status_code, 400) 
        self.assertEqual(response.json()['message'], "SETTINGS_ADD_PRODUCTION_SITE_MISSING_ZIP_CODE")        
        postdata['postal_code'] = '64430'
        response = self.client.post(reverse(url), postdata)
        self.assertEqual(response.status_code, 400) 
        self.assertEqual(response.json()['message'], "SETTINGS_ADD_PRODUCTION_SITE_MISSING_MANAGER_NAME")   
        postdata['manager_name'] = 'William Rock'
        response = self.client.post(reverse(url), postdata)
        self.assertEqual(response.status_code, 400) 
        self.assertEqual(response.json()['message'], "SETTINGS_ADD_PRODUCTION_SITE_MISSING_MANAGER_PHONE")   
        postdata['manager_phone'] = '0145247000'
        response = self.client.post(reverse(url), postdata)
        self.assertEqual(response.status_code, 400) 
        self.assertEqual(response.json()['message'], "SETTINGS_ADD_PRODUCTION_SITE_MISSING_MANAGER_EMAIL")   
        postdata['manager_email'] = 'will.rock@example.com'
        response = self.client.post(reverse(url), postdata)
        self.assertEqual(response.status_code, 400) 
        self.assertEqual(response.json()['message'], "SETTINGS_ADD_PRODUCTION_SITE_MISSING_CITY")
        postdata['city'] = 'Guermiette'
        response = self.client.post(reverse(url), postdata)
        self.assertEqual(response.status_code, 400) 
        self.assertEqual(response.json()['message'], "SETTINGS_ADD_PRODUCTION_SITE_COM_DATE_WRONG_FORMAT")
        postdata['date_mise_en_service'] = '2007-05-12'
        response = self.client.post(reverse(url), postdata)
        self.assertEqual(response.status_code, 400) 
        self.assertEqual(response.json()['message'], "SETTINGS_ADD_PRODUCTION_SITE_UNKNOWN_COUNTRY_CODE")
        postdata['country_code'] = 'FR'
        response = self.client.post(reverse(url), postdata)
        self.assertEqual(response.status_code, 400) 
        self.assertEqual(response.json()['message'], "SETTINGS_ADD_PRODUCTION_SITE_UNKNOWN_PRODUCER")
        postdata['entity_id'] = self.entity1.id
        response = self.client.post(reverse(url), postdata)
        self.assertEqual(response.status_code, 200)