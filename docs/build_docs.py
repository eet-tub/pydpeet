from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from generate_api import generate_api

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
SRC = ROOT / "src" / "pydpeet"
AUTOGEN = DOCS / "api" / "_autogen"
EXAMPLES = DOCS / "examples"
NOTEBOOKS = EXAMPLES / "notebooks"
NOTEBOOK_INDEX = NOTEBOOKS / "index.rst"
DOCTREES = DOCS / "_build" / "doctrees"
HTML = DOCS / "_build" / "html"


def run(cmd: list[str]):
    print(">", " ".join(map(str, cmd)))
    subprocess.check_call(cmd)


def main() -> None:
    generate_api()

    AUTOGEN.mkdir(parents=True, exist_ok=True)
    DOCTREES.mkdir(parents=True, exist_ok=True)
    HTML.mkdir(parents=True, exist_ok=True)

    run(
        [
            sys.executable,
            "-m",
            "sphinx",
            "-b",
            "html",
            "-E",
            "-a",
            "-d",
            str(DOCTREES),
            str(DOCS),
            str(HTML),
        ]
    )


if __name__ == "__main__":
    main()
