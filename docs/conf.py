import os
import sys

from sphinx.ext.autodoc import between

sys.path.insert(0, os.path.abspath(".."))

# -- Project information -----------------------------------------------------

project = "Alaric"
copyright = "2022, Skelmis"
author = "Skelmis"


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.intersphinx",
    "sphinx_toolbox.more_autodoc.typevars",
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "furo"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

master_doc = "index"

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "typing": ("https://docs.python.org/3", None),
    "motor": ("https://motor.readthedocs.io/en/stable", None),
    "pymongo": ("https://pymongo.readthedocs.io/en/stable/", None),
    "redis": ("https://redis.readthedocs.io/en/stable/", None),
}

all_typevars = True
