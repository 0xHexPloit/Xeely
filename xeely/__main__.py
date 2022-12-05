from xeely import __app_name__
from xeely import cli
from xeely import console


def main():
    cli.app(prog_name=__app_name__)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        console.print_error(str(e))
