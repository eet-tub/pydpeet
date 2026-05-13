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
project = "PyDPEET"  # Project name shown in documentation
author = "The PyDPEET Team"  # Author name displayed in docs
copyright = "2026, The PyDPEET Team"  # Copyright string in footer


# --- General configuration --------------------------------------------------
extensions = [
    "myst_parser",  # Enables Markdown (.md) support via MyST
    "nbsphinx",  # Integrates Jupyter notebooks into documentation
    "sphinx_design",  # Provides design directives like cards, grids, and tabs
    "sphinx.ext.autodoc",  # Automatically generates docs from docstrings
    "sphinx.ext.autosummary",  # Creates summary tables and API pages
    "sphinx.ext.napoleon",  # Supports NumPy and Google style docstrings
    "sphinx.ext.viewcode",  # Adds links to highlighted source code
    "sphinx_copybutton",  # Adds copy button to code blocksF
]


source_suffix = {
    ".md": "markdown",  # Treat .md files as Markdown
    ".rst": "restructuredtext",  # Treat .rst files as reStructuredText
}

master_doc = "index"  # Entry point of documentation (main page)

exclude_patterns = [
    "build",  # Ignore build directory
    "build/**",  # Ignore all subfiles in build
    "_build",  # Ignore Sphinx build output
    "_build/**",  # Ignore everything inside _build
    "**/.ipynb_checkpoints",  # Ignore Jupyter notebook checkpoint files
]

# --- MyST (Markdown) --------------------------------------------------------
myst_enable_extensions = [
    "colon_fence",  # Enables ::: fenced blocks (e.g., for directives like :::note or :::code-block)
    "deflist",  # Enables definition lists (term : definition style in Markdown)
]


autodoc_default_options = {
    "members": True,  # Include documented public members of modules/classes
    "undoc-members": False,  # Exclude members without docstrings
    "show-inheritance": False,  # Do not show inheritance hierarchy for classes
    "member-order": "bysource",  # Preserve the order from the source code
    "imported-members": False,  # Do not document imported helper objects
}


autodoc_typehints = "description"  # Show type hints in parameter descriptions
autodoc_typehints_format = "short"  # Use shortened type names instead of full module paths

python_use_unqualified_type_names = True  # Prefer list[str] over typing.List[str]

autodoc_type_aliases = {
    "DataFrame": "pandas.DataFrame",  # Replace short alias with full reference
    "ConfigLike": "pydpeet.settings.ConfigLike",  # Custom alias for internal type
}

# --- Napoleon (NumPy/Google docstrings) -------------------------------------
napoleon_numpy_docstring = True  # Enable NumPy-style docstring parsing
napoleon_google_docstring = False  # Disable Google-style docstrings

napoleon_use_admonition_for_examples = True  # Render Examples sections as admonition blocks
napoleon_use_param = True  # Convert Parameters section to :param: fields
napoleon_use_rtype = True  # Convert return types to :rtype: fields

# --- nbsphinx ---------------------------------------------------------------
nbsphinx_execute = "never"  # Do not execute notebooks during build
nbsphinx_output_folder = "_nbsphinx"  # Folder where processed notebooks are stored


extensions.append("sphinx.ext.intersphinx")  # Add intersphinx for external cross-references

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "numpy": ("https://numpy.org/doc/stable", None),
    "pandas": ("https://pandas.pydata.org/docs", None),
}

# --- HTML theme -------------------------------------------------------------
html_theme = "pydata_sphinx_theme"

html_static_path = ["_static"]  # Path for custom static files (e.g., CSS, images)

html_css_files = [
    "custom.css",
]

html_theme_options = {
    "navbar_align": "content",  # Align navbar with content area
    "show_nav_level": 4,  # Depth of navigation tree shown
    "show_toc_level": 2,
    "collapse_navigation": False,  # Keep navigation tree expanded by default
    "navigation_with_keys": True,  # Enable keyboard navigation
    "navbar_start": ["navbar-logo"],  # Show logo at the start of the navbar
    "navbar_center": ["navbar-nav"],  # Show main navigation links in the center
    "navbar_end": [
        "theme-switcher",
        # "version-switcher", # saved for later when wie have multiple versions
        "navbar-icon-links",
        "searchbox.html",
    ],
    "logo": {
        # "image_light": "_static/logo.png",
        # "image_dark": "_static/logo.png",  #
        "text": "PyDPEET",  # Text left upper Corner
    },
    "icon_links": [
        {
            "name": "GitLab",
            "url": "https://git.tu-berlin.de/eet_public/pydpeet/",
            "icon": "fa-brands fa-gitlab",
        },
        {
            "name": "GitHub",
            "url": "https://github.com/eet-tub/pydpeet",
            "icon": "fa-brands fa-github",
        },
    ],
}

# Controls the sidebar components. `sidebar-nav-bs.html` renders the project tree.
html_sidebars = {
    "**": [
        "sidebar-nav-bs.html",  # Main navigation tree in sidebar
        "searchbox.html",  # Search bar in sidebar
    ],
}

# autosummary Enables generation of separate pages for modules/functions via autosummary.
autosummary_generate = True
