# from api.v4.tests_utils import get_lot, setup_current_user
# from core.models import CarbureLot, Entity, UserRights
# from django.db.models import Count
# from django.test import TestCase
# from django.urls import reverse
# from django_otp.plugins.otp_email.models import EmailDevice
# from transactions.models import LockedYear
# from core.carburetypes import CarbureError

# from django.contrib.auth import get_user_model


# #python web/manage.py test api.v5.transactions.lots.tests  --keepdb

# class LotsCreateDraft(TestCase):
#     fixtures = [
#         "json/biofuels.json",
#         "json/feedstock.json",
#         "json/countries.json",
#         "json/entities.json",
#         'json/depots.json',
#         "json/productionsites.json",
#     ]

#     def setUp(self):
#         self.producer = Entity.objects.filter(entity_type=Entity.PRODUCER).annotate(psites=Count('productionsite')).filter(psites__gt=0)[0]
#         self.entity = self.producer
#         self.user = setup_current_user(self, "tester@carbure.local", "Tester", "gogogo", [(self.entity, "ADMIN")])


#         # user_model = get_user_model()
#         # self.password = 'totopouet'

#         # self.user1 = user_model.objects.create_user(email='testuser1@toto.com', name='Le Super Testeur 1', password=self.password)
#         # loggedin = self.client.login(username=self.user1.email, password=self.password)
#         # self.assertTrue(loggedin)

#         # self.supplier = Entity.objects.filter(entity_type=Entity.OPERATOR)[1]

#         # self.producer = Entity.objects.filter(entity_type=Entity.PRODUCER).annotate(psites=Count('productionsite')).filter(psites__gt=0)[0]
#         # self.trader = Entity.objects.filter(entity_type=Entity.TRADER)[0]
#         # self.trader.default_certificate = "TRADER_CERTIFICATE"
#         # self.trader.save()
#         # self.operator = Entity.objects.filter(entity_type=Entity.OPERATOR)[0]
#         # UserRights.objects.update_or_create(entity=self.producer, user=self.user1, role=UserRights.RW)
#         # UserRights.objects.update_or_create(entity=self.trader, user=self.user1, role=UserRights.RW)
#         # UserRights.objects.update_or_create(entity=self.operator, user=self.user1, role=UserRights.RW)

#         # # pass otp verification
#         # response = self.client.post(reverse('auth-request-otp'))
#         # self.assertEqual(response.status_code, 200)
#         # device, created = EmailDevice.objects.get_or_create(user=self.user1)
#         # response = self.client.post(reverse('auth-verify-otp'), {'otp_token': device.token})
#         # self.assertEqual(response.status_code, 200)


#     def test_create_draft(self):
#         LockedYear.objects.create(year=2018, locked=True)

#         lot = get_lot(self.producer)
#         response = self.client.post(reverse('transactions-lots-add'), lot)

#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(response.json()["status"], "success")
#         data = response.json()['data']
#         lot_id = data['id']
#         lot = CarbureLot.objects.get(id=lot_id)

#         self.assertEqual(lot.lot_status, CarbureLot.DRAFT)


#     def test_create_draft_on_locked_year(self):
#         LockedYear.objects.create(year=2021, locked=True)
#         lot = get_lot(self.producer)
#         response = self.client.post(reverse('transactions-lots-add'), lot)
#         self.assertEqual(response.status_code, 400)
#         self.assertEqual(response.json()["status"], "error")
#         self.assertEqual(response.json()["error"], CarbureError.YEAR_LOCKED)
