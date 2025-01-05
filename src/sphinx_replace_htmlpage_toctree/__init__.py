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

def update_toctree_context(app: Sphinx, pagename, templatename, context, doctree):
    """Updates the toctree key in the context object if the pagename has a custom toc
    """

    if pagename in app.env.replace_docname_toctree:
        context["toctree"] =  lambda **kwargs: render_named_toctree(app, pagename, app.env.replace_docname_toctree[pagename], **kwargs)
    return

def render_named_toctree(
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


def isold(app, env, added, changed: set, removed):
    return {"tutorial/index", "index"}

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
    
    return ["tutorial/index", "index"]

def before_read(app: Sphinx, env: BuildEnvironment, docnames: list):

    env.found_docs

    if "tutorial/index" not in docnames: docnames.append("tutorial/index")
    if "index" not in docnames: docnames.append("index")

    return

def return_updated(app, env):
    return ["tutorial/index", "index"]

def setup(app: Sphinx) -> ExtensionMetadata:

    app.add_config_value('replace_global_tocs', {}, 'env')
    app.connect('html-page-context', update_toctree_context)

    app.connect('env-get-updated', process_namedtocs)
    app.connect("env-updated", return_updated)
    app.connect("env-get-outdated", isold)

    return ExtensionMetadata(version=__version__, parallel_read_safe=False, parallel_write_safe=False)