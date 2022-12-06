from pathlib import Path

from typer.testing import CliRunner

from xeely import __app_name__
from xeely import __app_version__
from xeely import cli

runner = CliRunner()

REQUEST_FILE_PATH = Path(__file__).parent.resolve() / "resources" / "valid_request_with_xml.txt"
PATH_TO_FILE_TO_EXTRACT = "/etc/passwd"


def test_app_version():
    result = runner.invoke(cli.app, ["-v"])

    assert result.exit_code == 0
    assert f"{__app_name__} v{__app_version__}\n" in result.stdout
