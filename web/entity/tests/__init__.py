from django.test import TestCase as DjangoTestCase

class TestCase(DjangoTestCase):
    fixtures = [
        "json/countries.json",
    ]



