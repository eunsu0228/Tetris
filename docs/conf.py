# Configuration file for Sphinx documentation builder
# Dual Tetris - 2인용 대전 테트리스 게임

import os
import sys

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.abspath('..'))

# -- Project information -----------------------------------------------------
project = 'Dual Tetris'
copyright = '2026'
author = 'Game Developer'
release = '1.0.0'

# -- General configuration ---------------------------------------------------
extensions = [
    'sphinx.ext.autodoc',      # 자동 문서화
    'sphinx.ext.napoleon',     # Google/NumPy 스타일 docstring 지원
    'sphinx.ext.viewcode',     # 소스 코드 링크
    'sphinx.ext.todo',         # TODO 항목 지원
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']
language = 'ko'

# -- Options for HTML output -------------------------------------------------
html_theme = 'sphinx_rtd_theme'  # Read the Docs 테마
html_static_path = ['_static']
html_theme_options = {
    'navigation_depth': 4,
    'collapse_navigation': False,
    'sticky_navigation': True,
}

# -- Extension configuration -------------------------------------------------
autodoc_default_options = {
    'members': True,
    'member-order': 'bysource',
    'special-members': '__init__',
    'undoc-members': True,
    'exclude-members': '__weakref__'
}

# Napoleon settings
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = False
napoleon_use_admonition_for_notes = False
napoleon_use_admonition_for_references = False
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_preprocess_types = False
napoleon_type_aliases = None
napoleon_attr_annotations = True
