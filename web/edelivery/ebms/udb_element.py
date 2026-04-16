from xml.etree import ElementTree as ET


class UDBElement:
    @classmethod
    def from_xml(cls, xml_data):
        return cls(ET.fromstring(xml_data))

    def __init__(self, xml_root_element):
        self.xml_root_element = xml_root_element
