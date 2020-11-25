from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

import datetime
from core.models import Entity, UserRights, ISCCCertificate, DBSCertificate, Pays, EntityISCCTradingCertificate, EntityDBSTradingCertificate, ProductionSiteCertificate
from producers.models import ProductionSite
from api.v3.admin.urls import urlpatterns


class SettingsAPITest(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user1 = user_model.objects.create_user(email='testuser1@toto.com', name='Le Super Testeur 1', password='toto')

        # a few entities
        self.entity1, _ = Entity.objects.update_or_create(name='Le Super Producteur 1', entity_type='Producteur')
        self.entity2, _ = Entity.objects.update_or_create(name='Le Super Administrateur 1', entity_type='Administrateur')
        self.entity3, _ = Entity.objects.update_or_create(name='Le Super Operateur 1', entity_type='Opérateur')
        self.entity4, _ = Entity.objects.update_or_create(name='Le Super Trader 1', entity_type='Trader')        

        # some rights
        UserRights.objects.update_or_create(user=self.user1, entity=self.entity1)
        UserRights.objects.update_or_create(user=self.user1, entity=self.entity2)
        UserRights.objects.update_or_create(user=self.user1, entity=self.entity3)
        UserRights.objects.update_or_create(user=self.user1, entity=self.entity4)

    def test_certificates(self):
        # 1 create two iscc certificates and two 2bs certificates (one active, one expired)
        # 2 create a production site
        # 3 add expired certificates to your profile
        # 4 add those certificates to the production site
        # 5 update the certificates for the new ones

        # 1
        today = datetime.date.today()
        last_month = today - datetime.timedelta(days=30)
        ISCCCertificate.objects.update_or_create(certificate_id='ISCC-CERT-01', defaults={'valid_until':last_month, 'valid_from': last_month})
        ISCCCertificate.objects.update_or_create(certificate_id='ISCC-CERT-02', defaults={'valid_until':today, 'valid_from': last_month})
        DBSCertificate.objects.update_or_create(certificate_id='DBS-CERT-01', defaults={'valid_until':last_month, 'valid_from': last_month})
        DBSCertificate.objects.update_or_create(certificate_id='DBS-CERT-02', defaults={'valid_until':today, 'valid_from': last_month})

        # 2
        france, _ = Pays.objects.update_or_create(code_pays='FR', name='Frankreich')
        site, _ = ProductionSite.objects.update_or_create(producer=self.entity1, name='Usine Test', country=france, defaults={'date_mise_en_service': last_month})

        # 3
        self.client.login(username='testuser1@toto.com', password='toto')
        response = self.client.post(reverse('api-v3-settings-add-iscc-certificate'), {'entity_id': self.entity1.id, 'certificate_id': 'ISCC-CERT-01'})
        self.assertEqual(response.status_code, 200)        
        response = self.client.post(reverse('api-v3-settings-add-2bs-certificate'), {'entity_id': self.entity1.id, 'certificate_id': 'DBS-CERT-01'})
        self.assertEqual(response.status_code, 200)
        # check that they are indeed assigned to me
        response = self.client.post(reverse('api-v3-settings-get-iscc-certificates'), {'entity_id': self.entity1.id})
        self.assertEqual(response.status_code, 200)
        data = response.json()['data']
        self.assertEqual(len(data), 1)
        response = self.client.post(reverse('api-v3-settings-get-2bs-certificates'), {'entity_id': self.entity1.id})
        self.assertEqual(response.status_code, 200)
        data = response.json()['data']
        self.assertEqual(len(data), 1)


        # 4
        response = self.client.post(reverse('api-v3-settings-set-production-site-certificates'), {'entity_id': self.entity1.id, 'production_site_id': site.id, 'certificate_ids': ['ISCC-CERT-01', 'DBS-CERT-01']})
        self.assertEqual(response.status_code, 200)

        # check
        response = self.client.post(reverse('api-v3-settings-get-production-sites'), {'entity_id': self.entity1.id})
        self.assertEqual(response.status_code, 200)

        # 5 update
        response = self.client.post(reverse('api-v3-settings-update-iscc-certificate'), {'entity_id': self.entity1.id, 'old_certificate_id': 'ISCC-CERT-01', 'new_certificate_id': 'ISCC-CERT-02'})
        self.assertEqual(response.status_code, 200)
        response = self.client.post(reverse('api-v3-settings-update-2bs-certificate'), {'entity_id': self.entity1.id, 'old_certificate_id': 'DBS-CERT-01', 'new_certificate_id': 'DBS-CERT-02'})
        self.assertEqual(response.status_code, 200)        

        # check if certificates have been updated
        iscc_old_crt = ISCCCertificate.objects.get(certificate_id='ISCC-CERT-01')
        entity_old_iscc_crt = EntityISCCTradingCertificate.objects.get(certificate=iscc_old_crt)
        self.assertEqual(entity_old_iscc_crt.has_been_updated, True)
        dbs_old_crt = DBSCertificate.objects.get(certificate_id='DBS-CERT-01')
        entity_old_2bs_crt = EntityDBSTradingCertificate.objects.get(certificate=dbs_old_crt)
        self.assertEqual(entity_old_2bs_crt.has_been_updated, True)        

        # check if old production sites certificates have been removed
        old_iscc = ProductionSiteCertificate.objects.filter(entity=self.entity1, production_site=site, certificate_iscc=entity_old_iscc_crt)
        self.assertEqual(old_iscc.count(), 0)
        old_2bs = ProductionSiteCertificate.objects.filter(entity=self.entity1, production_site=site, certificate_2bs=entity_old_2bs_crt)
        self.assertEqual(old_2bs.count(), 0)        

        # check if new certificates are saved in profile
        iscc_new_crt = ISCCCertificate.objects.get(certificate_id='ISCC-CERT-02')
        entity_new_iscc_crt = EntityISCCTradingCertificate.objects.get(certificate=iscc_new_crt)
        self.assertEqual(entity_new_iscc_crt.has_been_updated, False)
        dbs_new_crt = DBSCertificate.objects.get(certificate_id='DBS-CERT-02')
        entity_new_2bs_crt = EntityDBSTradingCertificate.objects.get(certificate=dbs_new_crt)
        self.assertEqual(entity_new_2bs_crt.has_been_updated, False)      

        # check if new certificates are linked with production sites
        new_iscc = ProductionSiteCertificate.objects.filter(entity=self.entity1, production_site=site, certificate_iscc=entity_new_iscc_crt)
        self.assertEqual(new_iscc.count(), 1)
        new_2bs = ProductionSiteCertificate.objects.filter(entity=self.entity1, production_site=site, certificate_2bs=entity_new_2bs_crt)
        self.assertEqual(new_2bs.count(), 1)

