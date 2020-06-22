import datetime

from django.test import TestCase
from django.contrib.auth import get_user_model

from producers.models import ProductionSite, ProductionSiteInput, ProductionSiteOutput, ProducerCertificate
from core.models import Entity, Pays, MatierePremiere, Biocarburant
from django.core.files.base import ContentFile


class ProducersModelTest(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.producer = user_model.objects.create_user(email='testproducer@almalexia.org', name='MP TEST',
                                                       password='totopouet42')
        self.entity, created = Entity.objects.update_or_create(name='BioRaf1', entity_type='Producteur')
        self.country, created = Pays.objects.update_or_create(name='Jambon', code_pays='HAM')
        self.mp, created = MatierePremiere.objects.update_or_create(name='Gravier', code='GR', description='gravier fin')
        self.bc, created = Biocarburant.objects.update_or_create(name='BioKerosene', code='BKR')

    def test_production_site(self):
        ps = ProductionSite()
        ps.producer = self.entity
        ps.name = 'Test production site'
        ps.country = self.country
        ps.date_mise_en_service = datetime.date.today()
        ps.ges_option = 'Default'
        ps.eligible_dc = False
        ps.dc_reference = ''
        ps.save()
        self.production_site = ps

    def test_production_site_input(self):
        psi = ProductionSiteInput()
        psi.production_site = self.production_site
        psi.matiere_premiere = self.mp
        psi.save()

    def test_production_site_output(self):
        pso = ProductionSiteOutput()
        pso.production_site = self.production_site
        pso.biocarburant = self.bc
        pso.save()

    def test_producer_certificate(self):
        # create certificate
        c, created = ProducerCertificate.objects.update_or_create(producer=self.entity, production_site=self.production_site, certificate_id='TEST-CERTIF', defaults={'expiration':datetime.date.today()})
        c.certificate.save('django_test.txt', ContentFile(b'content'))
