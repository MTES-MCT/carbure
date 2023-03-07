from api.v4.tests_utils import get_lot, setup_current_user
from core.models import CarbureLot, Entity, UserRights
from django.db.models import Count
from django.test import TestCase
from django.urls import reverse
from django_otp.plugins.otp_email.models import EmailDevice

from django.contrib.auth import get_user_model


class LotsCreateDraft(TestCase):
    fixtures = [
        "json/biofuels.json",
        "json/feedstock.json",
        "json/countries.json",
        "json/entities.json",
        'json/depots.json',

        "json/productionsites.json",
    ]

    def setUp(self):
        self.entity = Entity.objects.filter(entity_type=Entity.PRODUCER)[0]
        self.producer = Entity.objects.filter(entity_type=Entity.PRODUCER).annotate(psites=Count('productionsite')).filter(psites__gt=0)[0]
        self.user = setup_current_user(self, "tester@carbure.local", "Tester", "gogogo", [(self.entity, "ADMIN")])
        
        
        # user_model = get_user_model()
        # self.password = 'totopouet'

        # self.user1 = user_model.objects.create_user(email='testuser1@toto.com', name='Le Super Testeur 1', password=self.password)
        # loggedin = self.client.login(username=self.user1.email, password=self.password)
        # self.assertTrue(loggedin)

        # self.supplier = Entity.objects.filter(entity_type=Entity.OPERATOR)[1]

        # self.producer = Entity.objects.filter(entity_type=Entity.PRODUCER).annotate(psites=Count('productionsite')).filter(psites__gt=0)[0]
        # self.trader = Entity.objects.filter(entity_type=Entity.TRADER)[0]
        # self.trader.default_certificate = "TRADER_CERTIFICATE"
        # self.trader.save()
        # self.operator = Entity.objects.filter(entity_type=Entity.OPERATOR)[0]
        # UserRights.objects.update_or_create(entity=self.producer, user=self.user1, role=UserRights.RW)
        # UserRights.objects.update_or_create(entity=self.trader, user=self.user1, role=UserRights.RW)
        # UserRights.objects.update_or_create(entity=self.operator, user=self.user1, role=UserRights.RW)

        # # pass otp verification
        # response = self.client.post(reverse('api-v4-request-otp'))
        # self.assertEqual(response.status_code, 200)
        # device, created = EmailDevice.objects.get_or_create(user=self.user1)
        # response = self.client.post(reverse('api-v4-verify-otp'), {'otp_token': device.token})
        # self.assertEqual(response.status_code, 200)

    

    def test_create_draft(self):
        
        # query = {
        #     "entity_id": self.entity.id,
        #     "ticket_id": self.ticket.id,
        # }
        lot = self.create_draft()
        
        # self.assertEqual(lot.lot_status, CarbureLot.DRAFT)


        # response = self.client.post(reverse("api-v5-saf-airline-accept-ticket"), query)

        # self.assertEqual(response.status_code, 200)
        # self.assertEqual(response.json()["status"], "success")

        # self.assertEqual(SafTicket.objects.get(id=self.ticket.id).status, SafTicket.ACCEPTED)

    def create_draft(self, lot=None):
        if lot is None:
            lot = get_lot(self.producer)
        # # lot.update(kwargs)
        # response = self.client.post(reverse('api-v4-add-lots'), lot)
        # self.assertEqual(response.status_code, 200)
        # data = response.json()['data']
        # lot_id = data['id']
        # lot = CarbureLot.objects.get(id=lot_id)
        return lot
    