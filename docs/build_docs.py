from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
SRC = ROOT / "src" / "pydpeet"
AUTOGEN = DOCS / "api" / "_autogen"
EXAMPLES = DOCS / "examples"
NOTEBOOKS = EXAMPLES / "notebooks"
NOTEBOOK_INDEX = NOTEBOOKS / "index.rst"
DOCTREES = DOCS / "build" / "doctrees"
HTML = DOCS / "build" / "html"


def run(cmd: list[str]):
    print(">", " ".join(map(str, cmd)))
    subprocess.check_call(cmd)


def add_conda_pandoc_to_path():
    candidates = [
        Path(sys.prefix) / "Library" / "bin",
        Path(sys.executable).resolve().parent.parent / "Library" / "bin",
    ]

    current_path = os.environ.get("PATH", "")
    for candidate in candidates:
        if not candidate.exists():
            continue
        if shutil.which("pandoc"):
            return
        os.environ["PATH"] = str(candidate) + os.pathsep + current_path
        return


def ensure_pandoc_available():
    add_conda_pandoc_to_path()

    if shutil.which("pandoc"):
        return

    message = """
Pandoc is required to build the documentation because nbsphinx parses Jupyter notebooks.

Install pandoc first, then rerun this script.

Recommended options:
- conda: conda install -c conda-forge pandoc
- Windows installer: https://pandoc.org/installing.html

After that, run:
- python -m pip install -e .[docs]
- python docs/build_docs.py
""".strip()

    raise SystemExit(message)


def main():
    AUTOGEN.mkdir(parents=True, exist_ok=True)
    DOCTREES.mkdir(parents=True, exist_ok=True)
    HTML.mkdir(parents=True, exist_ok=True)
    ensure_pandoc_available()

    # 1) Generate API stubs
    run(
        [
            sys.executable,
            "-m",
            "sphinx.ext.apidoc",
            "-f",  # overwrite
            "-e",  # output one file per module
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
