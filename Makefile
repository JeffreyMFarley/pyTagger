# You can set these variables from the command line.
SPHINXOPTS    =
SPHINXBUILD   = python -msphinx
SPHINXPROJ    = pyTagger
SOURCEDIR     = docsrc
BUILDDIR      = docs

GENDOCSRC := $(wildcard $(SOURCEDIR)/*.rst)
GENDOCSRC := $(filter-out $(SOURCEDIR)/index.rst, $(GENDOCSRC))

all: clean-pyc test

test:
	coverage run setup.py test
	coverage html

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +

docs: $(GENDOCSRC) $(SOURCEDIR)/index.rst
	@$(SPHINXBUILD) "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

gendocs:
	rm -rf $(GENDOCSRC)
	sphinx-apidoc -o "$(SOURCEDIR)" "$(SPHINXPROJ)"