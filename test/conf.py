

project = 'replace toctree tester'
copyright = '2024, Foo'
author = 'Bar'
release = '0.0.1'
html_theme = 'alabaster'

extensions = [
            "sphinx_replace_htmlpage_toctree"
            ]

replace_global_tocs = {
    "tutorial/*": "tutorialtree",
}