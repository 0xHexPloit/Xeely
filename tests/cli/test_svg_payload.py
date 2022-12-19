import os
from pathlib import Path

from typer.testing import CliRunner

from xeely import cli

runner = CliRunner()


def test_svg_payload_creation():
    saving_path = Path(__file__).parent.resolve()
    runner.invoke(cli.app, ["svg", "--file", "/etc/passwd", "--out", f"{saving_path}"])

    expected_data = """<svg>
&xxe;
</svg>"""

    svg_file_path = saving_path / "xxe.svg"

    assert svg_file_path.exists()

    with open(svg_file_path) as file:
        data = file.read()

        assert expected_data in data

    os.remove(svg_file_path)
