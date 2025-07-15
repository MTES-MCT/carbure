from unittest import TestCase

from edelivery.ebms.access_points import Initiator, Responder


class InitiatorTest(TestCase):
    def test_knows_its_XML_representation(self):
        initiator = Initiator("initiator_id")
        expected_XML = """\
<eb:PartyId type="urn:oasis:names:tc:ebcore:partyid-type:unregistered:UDB">initiator_id</eb:PartyId>
<eb:Role>http://docs.oasis-open.org/ebxml-msg/ebms/v3.0/ns/core/200704/initiator</eb:Role>"""
        self.assertEqual(expected_XML, initiator.to_XML())


class ResponderTest(TestCase):
    def test_knows_its_XML_representation(self):
        responder = Responder("responder_id")
        expected_XML = """\
<eb:PartyId type="urn:oasis:names:tc:ebcore:partyid-type:unregistered:UDB">responder_id</eb:PartyId>
<eb:Role>http://docs.oasis-open.org/ebxml-msg/ebms/v3.0/ns/core/200704/responder</eb:Role>"""
        self.assertEqual(expected_XML, responder.to_XML())
