from xeely.xxe import cdata


def test_cdata_entities():
    resource = "file:///etc/passwd"

    entities = cdata.get_cdata_entities(resource)

    assert len(entities) == 3
    assert entities[0].to_xml() == '<!ENTITY % begin "<![CDATA[">'
    assert entities[1].to_xml() == f'<!ENTITY % file SYSTEM "{resource}">'
    assert entities[2].to_xml() == '<!ENTITY % end "]]>">'


def test_content_cdata_dtd_file():
    expected_content = '<!ENTITY joined "%begin;%file;%end;">\n'
    cdata.create_cdata_dtd_file()

    with open(cdata.CDATA_FILE_PATH) as file:
        data = file.read()
        assert data == expected_content


def test_remove_cdata_dtd_file():
    cdata.create_cdata_dtd_file()
    cdata.delete_cdata_dtd_file()

    assert not cdata.CDATA_FILE_PATH.exists()
