# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import re
import sys

import sphinx_rtd_theme

sys.path.insert(0, os.path.abspath('../../python'))

# -- Project information -----------------------------------------------------

project = 'XRPrimer'
copyright = '2022, OpenXRLab'
author = 'XRPrimer Authors'
version_file = '../../version.txt'


def parse_version_from_file(filepath):
    """Parse version txt into string and tuple.

    Args:
        filepath (str): The version filepath.
    Returns:
        str: The version string, e.g., "0.4.0"
        dict: The version info, e.g.,
            {
                'XRPRIMER_VERSION_MAJOR': 0,
                'XRPRIMER_VERSION_MINOR': 4,
                'XRPRIMER_VERSION_PATCH': 0,
            }
    """
    keywords = [
        'XRPRIMER_VERSION_MAJOR', 'XRPRIMER_VERSION_MINOR',
        'XRPRIMER_VERSION_PATCH'
    ]
    version_info = {}
    version_list = []
    with open(filepath) as f:
        content = f.read()
        for keyword in keywords:
            regex = rf'{keyword}\s*([0-9]+)'
            obj = re.search(regex, content)
            vid = obj.group(1)
            version_list.append(vid)
            assert keyword not in version_info
            version_info[keyword] = int(vid)
    version = '.'.join(version_list)
    return version, version_info


def get_version(version_file):
    version, _ = parse_version_from_file(version_file)
    return version


# The full version, including alpha/beta/rc tags
release = get_version(version_file)

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc', 'sphinx.ext.napoleon', 'sphinx.ext.viewcode',
    'sphinx_markdown_tables', 'sphinx_copybutton', 'myst_parser'
]

autodoc_mock_imports = ['xrprimer_cpp']

# Parse `Returns` in docstr with parameter style
napoleon_custom_sections = [('Returns', 'params_style')]

# Ignore >>> when copying code
copybutton_prompt_text = r'>>> |\.\.\. '
copybutton_prompt_is_regexp = True

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
#
source_suffix = {
    '.rst': 'restructuredtext',
    '.md': 'markdown',
}

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'sphinx_rtd_theme'
html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]

# Enable ::: for my_st
myst_enable_extensions = ['colon_fence']

master_doc = 'index'
