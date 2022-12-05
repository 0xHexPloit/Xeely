from xeely.custom_xml.doctype import XMLDoctype
from xeely.custom_xml.entity import XMLEntity


def test_empty_doctype():
    doctype = XMLDoctype("root", [])
    doctype_str = doctype.to_xml()

    assert doctype_str == "<!DOCTYPE root [\n]>\n"


def test_doctype_with_entities():
    entity = XMLEntity("test", "value")
    entities = [entity, "test_str"]
    doctype = XMLDoctype("root", entities)
    doctype_str = doctype.to_xml()

    expected_str = f"<!DOCTYPE root [\n {entity.to_xml()}\n {entities[1]}\n]>\n"
    assert doctype_str == expected_str
