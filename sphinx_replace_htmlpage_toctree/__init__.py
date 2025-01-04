from typing import *

import re

from docutils import nodes

from sphinx import addnodes
from sphinx.util import logging
from sphinx.application import Sphinx
from sphinx.util.typing import ExtensionMetadata
from sphinx.util.docutils import SphinxDirective
from sphinx.builders.html import StandaloneHTMLBuilder
from sphinx.environment.adapters.toctree import _resolve_toctree
from sphinx.environment import BuildEnvironment


__version__ = "0.0.1"
_LOGGER = logging.getLogger(__name__)

EXTENSION_NAME = "replace-htmlpage-toctree"
TOCLIST_ATTR = "replace_docname_toctree"

def update_doctree_context(app: Sphinx, pagename, templatename, context, doctree):
    """Updates the toctree key in the context object if the pagename has a custom toc
    """

    if pagename in app.env.replace_docname_toctree:
        context["toctree"] =  lambda **kwargs: process_tutorial_toc(app, pagename, app.env.replace_docname_toctree[pagename], **kwargs)
    return

def process_tutorial_toc(
        app: Sphinx, docname: str, tocname: str, collapse: bool = True, **kwargs: Any
    ) -> str:

    builder = app.builder
    maxdepth = kwargs.get('maxdepth',0)
    includehidden = kwargs.get("includehidden", False)
    titles_only = kwargs.get("titles_only", False)
    toc_env = app.env.master_doctree.ids[tocname]
    toc_tree = toc_env.children[0]

    # for toctree_node in app.env.master_doctree.findall(addnodes.toctree):
    #     if tocname in toctree_node.parent.attributes["ids"]:
    #         toc_tree = toctree_node

    resolved = _resolve_toctree(app.env, docname, builder, toc_tree, prune=True, collapse=collapse, maxdepth=int(maxdepth), includehidden=includehidden, titles_only=titles_only)

    if not resolved:
        resolved = None
    return builder.render_partial(resolved)["fragment"]

# class NamedTOC(SphinxDirective):

#     has_content = True
#     required_arguments = 1

#     _custom_tocs = {}

#     def run(self):

#         if not hasattr(self.env, TOCLIST_ATTR):
#             setattr(self.env, TOCLIST_ATTR, {})

#         toc_name = self.arguments[0]
#         env_ids = self.env.master_doctree.ids
#         if toc_name not in env_ids:
#             _LOGGER.error(f"{self.get_location()}: No toctree with name {toc_name} was found")
#             return []
        
#         named_toc = env_ids[toc_name]
#         if "toctree-wrapper" not in named_toc.attributes["classes"]:
#             _LOGGER.error(f"{self.get_location()}: {toc_name} is not a toctree")
#             return []
        
#         self.__class__._custom_tocs[self.env.docname] = toc_name
#         self.env.replace_docname_toctree[self.env.docname] = toc_name
#         return [namedtoc('')]

def isold(app, env, added, changed, removed):
    return ["/documentation/index"]

def process_namedtocs(app: Sphinx, env: BuildEnvironment):

    app.env.replace_docname_toctree = {}
    for doc, treename in app.config.replace_global_tocs.items():
        env_ids = app.env.master_doctree.ids
        if treename not in env_ids:
            _LOGGER.error(f"No toctree with name {treename} was found")
            continue
        
        named_toc = env_ids[treename]
        if "toctree-wrapper" not in named_toc.attributes["classes"]:
            _LOGGER.error(f"{treename} is not a toctree")
            continue
        
        if "*" in doc:
            expr = re.compile(doc)
            for found_doc in env.found_docs:
                if expr.match(found_doc):
                    app.env.replace_docname_toctree[found_doc] = treename
        elif doc in env.found_docs:
            app.env.replace_docname_toctree[doc] = treename
        else:
            _LOGGER.error(f"{EXTENSION_NAME}: {doc} was not found and is not an expression.")
    
    return []

def setup(app: Sphinx) -> ExtensionMetadata:

    app.add_config_value('replace_global_tocs', {}, 'env')
    app.connect('html-page-context', update_doctree_context)

    app.connect('env-get-updated', process_namedtocs)
    # app.connect("env-get-outdated",isold)

    return ExtensionMetadata(version=__version__, parallel_read_safe=True, parallel_write_safe=True)