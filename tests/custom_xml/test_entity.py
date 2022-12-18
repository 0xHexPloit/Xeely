from xeely.custom_xml.entity import XMLEntity


def test_basic_serialization():
    entity = XMLEntity("entity", "test")
    entity_str = entity.to_xml()

    assert entity_str == '<!ENTITY entity "test">'


def test_serialization_with_parameter_entity():
    entity = XMLEntity("entity", "test", is_parameter=True)
    entity_str = entity.to_xml()

    assert entity_str == '<!ENTITY % entity "test">'


def test_serialization_with_external_entity():
    entity = XMLEntity("entity", "test", is_external=True)
    entity_str = entity.to_xml()

    assert entity_str == '<!ENTITY entity SYSTEM "test">'
