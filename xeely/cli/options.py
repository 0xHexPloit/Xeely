from typing import Optional
from typing import Tuple

import typer

from xeely.xxe.attack.mode import XXEAttackMode
from xeely.xxe.attack.type import XXEAttackType


def mutually_exclusive_group(size=2):
    group = set()

    def callback(ctx: typer.Context, param: typer.CallbackParam, value: str):
        # Add cli option to group if it was called with a value
        if value is not None and param.name not in group:
            group.add(param.name)
        if len(group) > size - 1:
            raise typer.BadParameter(f"{param.name} is mutually exclusive with {group.pop()}")
        return value

    return callback


exclusivity_callback = mutually_exclusive_group()


def get_attack_type_and_resource_from_options(
    file: Optional[str], dir_listing: Optional[str], ssrf: Optional[str], rce: Optional[str]
) -> Tuple[XXEAttackType, str]:
    if file is not None:
        return XXEAttackType.FILE_DISCLOSURE, file
    elif dir_listing is not None:
        return XXEAttackType.DIRECTORY_LISTING, dir_listing
    elif ssrf is not None:
        return XXEAttackType.SSRF, ssrf
    elif rce is not None:
        return XXEAttackType.RCE, rce
    else:
        raise typer.BadParameter("You forgot to specify the type of attack to perform")


file_option = typer.Option(
    None, help="The path to the the file to exfiltrate", callback=exclusivity_callback
)

dir_option = typer.Option(
    None, help="The path the directory to list", callback=exclusivity_callback
)

ssrf_option = typer.Option(
    None, help="The URL that the target server should use", callback=exclusivity_callback
)

rce_option = typer.Option(
    None, help="The command to perform on the target server", callback=exclusivity_callback
)

cdata_option = typer.Option(False, help="Use XML CDATA section to escape some characters")

base64_option = typer.Option(
    False,
    help="Use PHP filter to base64 encode target data",
)

mode_option = typer.Option(XXEAttackMode.DIRECT, help="The mode to use to perform the attack")

lhost_option = typer.Option(
    "", help="The IP address to use to setup the HTTP server when dealing with blind attacks"
)

lport_option = typer.Option(
    8000, help="The port to use to setup the HTTP server when dealing with blind attacks"
)
