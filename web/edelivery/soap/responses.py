import xml.etree.ElementTree as ET


class AbstractEdeliveryResponse:
    def __init__(self, text):
        self.text = text
        self.parsed_XML = ET.fromstring(text)


class ListPendingMessagesResponse(AbstractEdeliveryResponse):
    def __init__(self, text):
        super().__init__(text)
        self.message_id_elements = self.parsed_XML.findall(".//messageID")

    def next_pending_message_id(self):
        ids = self.pending_message_ids()
        return ids[0]

    def pending_message_ids(self):
        return [e.text for e in self.message_id_elements]

    def pending_message_present(self):
        ids = self.pending_message_ids()
        return len(ids) > 0


class RetrieveMessageResponse(AbstractEdeliveryResponse):
    pass


class SubmitMessageResponse(AbstractEdeliveryResponse):
    def __init__(self, text):
        super().__init__(text)
