from pathlib import Path
from typing import Sequence

from xeely.custom_xml import XMLEntity


def write_doctype_content_to_disk(file_path: Path, content: Sequence[XMLEntity | str]):
    with open(file_path, "w") as file:
        for item in content:
            data = item if isinstance(item, str) else item.to_xml()
            file.write(f"{data}\n")
