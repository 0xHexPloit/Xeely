from xeely import __app_name__
from xeely import __app_version__
from xeely import __author__
from xeely import cli
from xeely import console


def print_banner():
    banner = f"""
$$\\   $$\\                     $$\
$$ |  $$ |                    $$ |
\\$$\\ $$  | $$$$$$\\   $$$$$$\\  $$ |$$\\   $$\
 \\$$$$  / $$  __$$\\ $$  __$$\\ $$ |$$ |  $$ |
 $$  $$<  $$$$$$$$ |$$$$$$$$ |$$ |$$ |  $$ |
$$  /\\$$\\ $$   ____|$$   ____|$$ |$$ |  $$ |
$$ /  $$ |\\$$$$$$$\\ \\$$$$$$$\\ $$ |\\$$$$$$$ |
\\__|  \\__| \\_______| \\_______|\\__| \\____$$ |
                                  $$\\   $$ |
                                  \\$$$$$$  |
                                   \\______/


by {__author__} v{__app_version__}
    """
    print(banner)


def main():
    cli.app(prog_name=__app_name__)


if __name__ == "__main__":
    try:
        print_banner()
        # main()
    except Exception as e:
        console.print_error(str(e))
