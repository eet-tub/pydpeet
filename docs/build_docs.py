from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
SRC = ROOT / "src" / "pydpeet"
AUTOGEN = DOCS / "api" / "_autogen"
DOCTREES = DOCS / "build" / "doctrees"
HTML = DOCS / "build" / "html"


def run(cmd: list[str]):
    print(">", " ".join(map(str, cmd)))
    subprocess.check_call(cmd)


def main():
    AUTOGEN.mkdir(parents=True, exist_ok=True)
    DOCTREES.mkdir(parents=True, exist_ok=True)
    HTML.mkdir(parents=True, exist_ok=True)

    # 1) Generate API stubs
    run(
        [
            sys.executable,
            "-m",
            "sphinx.ext.apidoc",
            "-f",  # overwrite
            "-M",  # module-first
            "-o",
            str(AUTOGEN),
            str(SRC),
        ]
    )

    # 2) Build docs
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
