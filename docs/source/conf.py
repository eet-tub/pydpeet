# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import os
import sys
from pathlib import Path

current_dir = Path(__file__).parent
ppb_dir = current_dir.parent.parent / "src"

sys.path.insert(0, str(ppb_dir))
if current_dir not in sys.path:
    sys.path.insert(0, str(current_dir))

project = 'ppb24'
copyright = '2025, Alexander Hinrichsen, Cataldo De Simone, Daniel Schröder, Jan Kalisch'
author = 'Alexander Hinrichsen, Cataldo De Simone, Daniel Schröder, Jan Kalisch'
release = '1.0.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ["sphinx.ext.todo", "sphinx.ext.viewcode", "sphinx.ext.autodoc"]

# Verhindert das Anzeigen von kompletten Modulpfaden
add_module_names = False

autodoc_default_options = {
    "members": True,
    "undoc-members": True,
    "show-inheritance": True,
    "module-names": False  # ignores showing the path to reference
}

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store', 'build', 'dist', '.venv']

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
