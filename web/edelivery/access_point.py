class AccessPoint:
    def __init__(self, access_point_id, role):
        self.id = access_point_id
        self.type = "urn:oasis:names:tc:ebcore:partyid-type:unregistered:UDB"
        self.role = role

    def to_XML(self):
        return f"""\
<eb:PartyId type="{self.type}">{self.id}</eb:PartyId>
<eb:Role>{self.role}</eb:Role>"""


class Initiator(AccessPoint):
    def __init__(self, access_point_id):
        super().__init__(access_point_id, "http://docs.oasis-open.org/ebxml-msg/ebms/v3.0/ns/core/200704/initiator")


class Responder(AccessPoint):
    def __init__(self, access_point_id):
        super().__init__(access_point_id, "http://docs.oasis-open.org/ebxml-msg/ebms/v3.0/ns/core/200704/responder")
