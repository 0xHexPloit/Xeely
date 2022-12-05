from rich.console import Console
from rich.table import Table

console = Console()


def print_message(message: str, *, message_type: str, message_color: str, bold: bool = False):
    console.print(
        f"[[{message_color}]{message_type}[/]] "
        + f"{'[bold]' if bold else ''}{message} {'[/]' if bold else ''}"
    )


def print_info(message: str, *, bold: bool = False):
    print_message(message, message_type="INFO", message_color="green", bold=bold)


def print_error(message: str, *, bold: bool = False):
    print_message(message, message_type="ERROR", message_color="red", bold=bold)


def print_warning(message: str, *, bold: bool = False):
    print_message(message, message_type="WARNING", message_color="orange3", bold=bold)


def show_exfiltrated_data_in_table(resource_name, data: str):
    table = Table()

    table.add_column(f"Content of {resource_name}", justify="left", no_wrap=False)
    table.add_row(data)

    console.print(table)
