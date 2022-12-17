from pathlib import Path

import toml

root_dir = Path(__file__).parent.parent
project_file_path = root_dir / "pyproject.toml"

project_data = toml.load(str(project_file_path))

__app_name__ = project_data["tool"]["poetry"]["name"]
__app_version__ = project_data["tool"]["poetry"]["version"]
__author__ = project_data["tool"]["poetry"]["authors"][0].split(" ")[0]

RESOURCES_PATH = root_dir / "xeely" / "resources"
