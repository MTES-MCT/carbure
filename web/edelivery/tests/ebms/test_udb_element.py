from unittest import TestCase

from edelivery.ebms.udb_element import UDBElement


class UDBElementTest(TestCase):
    def test_knows_its_xml_string(self):
        element = UDBElement.from_xml("<SOME_UDB_ELEMENT>Some value</SOME_UDB_ELEMENT>")
        self.assertEqual("<SOME_UDB_ELEMENT>Some value</SOME_UDB_ELEMENT>", element.to_xml())
