import pytest
from pytest_httpserver import HTTPServer

from xeely.custom_xml import XML
from xeely.xxe.attack.handler.direct import XXEDirectAttackHandler


@pytest.fixture
def base_xml():
    raw_xml = """
    <contact>
    <prenom>Jean</prenom>
    <nom>PERRI</nom>
    <email>jean.perri@gmail.com</email>
    </contact>
        """
    return XML.parse_string(raw_xml)


TARGET_URL = "http://localhost:8001/submitContact.php"


@pytest.mark.parametrize(
    "base64_encoding",
    [
        (False,),
        (True,),
    ],
)
def test_direct_attack_handler(httpserver: HTTPServer, base_xml, base64_encoding):
    httpserver.expect_oneshot_request(uri=TARGET_URL, method="POST").respond_with_data(
        f"Un email a été envoyé à: {base_xml.get_text_element_value('email')}"
    )
    attack_handler = XXEDirectAttackHandler(
        resource="/etc/hosts",
        xml=base_xml,
        target_url=TARGET_URL,
        should_apply_base64_encoding=base64_encoding,
    )
    data = attack_handler.run_attack()

    assert "localhost" in data


def test_failed_direct_attack_handler(httpserver: HTTPServer, base_xml):
    attack_handler = XXEDirectAttackHandler(
        resource="/etc/invalid",
        xml=base_xml,
        target_url=TARGET_URL,
        should_apply_base64_encoding=False,
    )
    data = attack_handler.run_attack()

    assert len(data) == 0
