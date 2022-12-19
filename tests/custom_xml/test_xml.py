import pytest

from xeely.custom_xml.doctype import XMLDoctype
from xeely.custom_xml.errors import NotTextElement
from xeely.custom_xml.errors import XMLElementNotFound
from xeely.custom_xml.xml import get_custom_xml_tag
from xeely.custom_xml.xml import XML

xml_content = """<root>
    <prenom>Jean</prenom>
    <nom>PELOTTI</nom>
</root>"""


def test_parsing():
    xml = XML.parse_string(xml_content)
    root_name = xml.get_root_node_name()

    assert root_name == "root"


def test_get_text_elements():
    xml = XML.parse_string(xml_content)
    text_elements = xml.get_text_elements()

    assert len(text_elements) == 2
    assert text_elements[0].get_name() == "prenom"
    assert text_elements[1].get_name() == "nom"


def test_get_text_element_value():
    xml = XML.parse_string(xml_content)
    firstname = xml.get_text_element_value("prenom")

    assert firstname == "Jean"


def test_change_text_element_value():
    new_value = "Hugo"
    xml = XML.parse_string(xml_content)
    xml.change_text_element_value("prenom", new_value)
    firstname = xml.get_text_element_value("prenom")

    assert firstname == new_value


def test_raise_exception_if_element_not_found():
    xml = XML.parse_string(xml_content)

    with pytest.raises(XMLElementNotFound):
        xml.get_text_element_value("email")


def test_raise_exception_for_accessing_value_for_an_element_that_is_not_a_text_element():
    xml = XML.parse_string(xml_content)

    with pytest.raises(NotTextElement):
        xml.get_text_element_value("root")


def test_raise_exception_for_changing_value_of_an_element_that_is_not_a_text_element():
    xml = XML.parse_string(xml_content)

    with pytest.raises(NotTextElement):
        xml.change_text_element_value("root", "data")


def test_serialization():
    xml = XML.parse_string(xml_content)
    xml_str = xml.to_xml()

    assert xml_content in xml_str
    assert get_custom_xml_tag() in xml_str


def test_serialization_with_doctype():
    xml = XML.parse_string(xml_content)

    doctype = XMLDoctype("root", [])
    xml.set_doctype(doctype)

    xml_str = xml.to_xml()

    assert doctype.to_xml() in xml_str
