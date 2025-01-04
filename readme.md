Quick and dirty way to use custom toctrees in sphinx. Leaving this here mainly as a reference for others running into the same issue with their toc.

Usage:
in ``conf.py``, set the variable ``replace_global_tocs`` to a dict. 
Keys are docnames or globs to replace to global toc for. Values are toctree names (given via the ``:name::`` directive.)

usage:
```python
#in conf.py

extensions = [
...
"sphinx_replace_htmlpage_toctree"
]

replace_toctree = {
    "documentation/*": "my-toctree"
}
```

toctrees that can be used for replacement must be in the root document (I suspect, otherwise the extension cannot find the toctree)

```rst

.. toctree::
    :name: my-toctree

    self
    testpage

```

At least for autobuild, has to be run with the ``-E`` flag, which increases build time since it basically means sphinx won't use a cache. The problem with this lies with the toctree itself not being updated, I suspect because it uses the pickles doctree when updating a document in which the referenced toctree does not appear. But I haven't quite figured out how to get access to the updated toctree.

To install: download the repo, unpack it, open a terminal in the folder and run `pip install .`. The ``pyproject.toml`` should take care of the rest.
