# test with : python web/manage.py test carbure.scripts.tests_scripts.ScriptsTest --keepdb
from carbure.scripts.update_iscc_certificates import update_iscc_certificates
from django.test import TestCase

# UNCOMMENT THIS TO TEST THE SCRIPTS
# class ScriptsTest(TestCase):
#     def test_update_iscc_certificates(self):
#         update_iscc_certificates(batch=1, test=True)
