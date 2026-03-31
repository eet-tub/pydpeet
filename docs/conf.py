from __future__ import annotations

import sys
from pathlib import Path

# --- Paths -----------------------------------------------------------------
DOCS_DIR = Path(__file__).resolve().parent
REPO_ROOT = DOCS_DIR.parent
SRC_DIR = REPO_ROOT / "src"

# src-layout: enables `import pydpeet` for autodoc/autosummary
sys.path.insert(0, str(SRC_DIR))

# --- Project information ----------------------------------------------------
project = "PyDPEET"
author = "The PyDPEET Team"
copyright = "2026, The PyDPEET Team"

# Optional (only if you want version shown):
# import importlib.metadata
# release = importlib.metadata.version("pydpeet")
# version = ".".join(release.split(".")[:2])

# --- General configuration --------------------------------------------------
extensions = [
    "myst_parser",
    "nbsphinx",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx_copybutton",
]

# If you set source_suffix, include all you use. Leave .ipynb out (nbsphinx handles it)
source_suffix = {
    ".md": "markdown",
    ".rst": "restructuredtext",
}

master_doc = "index"

exclude_patterns = [
    "build",
    "build/**",
    "_build",
    "_build/**",
    "**/.ipynb_checkpoints",
]

# --- MyST (Markdown) --------------------------------------------------------
myst_enable_extensions = ["colon_fence", "deflist"]

autodoc_default_options = {
    "members": True,
    "undoc-members": False,
    "show-inheritance": True,
    "member-order": "bysource",
}

autodoc_typehints = "description"
autodoc_type_aliases = {
    "DataFrame": "pandas.DataFrame",
    "ConfigLike": "pydpeet.settings.ConfigLike",  # adjust if different
}

# --- Napoleon (NumPy/Google docstrings) -------------------------------------
napoleon_numpy_docstring = True
napoleon_google_docstring = True
napoleon_use_param = True
napoleon_use_rtype = True

# --- nbsphinx ---------------------------------------------------------------
nbsphinx_execute = "never"
nbsphinx_output_folder = "_nbsphinx"


extensions.append("sphinx.ext.intersphinx")

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "numpy": ("https://numpy.org/doc/stable", None),
    "pandas": ("https://pandas.pydata.org/docs", None),
}

# --- HTML theme -------------------------------------------------------------
html_theme = "pydata_sphinx_theme"
html_theme_options = {
    "navbar_align": "content",
    "show_nav_level": 4,
    "navigation_with_keys": True,
    "icon_links": [
        {
            "name": "GitLab",
            "url": "https://git.tu-berlin.de/eet_public/pydpeet/",
            "icon": "fa-brands fa-gitlab",
        },
        {
            "name": "GitHub",
            "url": "https://github.com/eet-tub",
            "icon": "fa-brands fa-github",
        },
    ],
}

# Controls the sidebar components. `sidebar-nav-bs.html` renders the project tree.
html_sidebars = {
    "**": [
        "sidebar-nav-bs.html",  # left navigation tree
        "sidebar-ethical-ads.html",
        "searchbox.html",
    ],
}

# autosummary Enables generation of separate pages for modules/functions via autosummary.
autosummary_generate = True

