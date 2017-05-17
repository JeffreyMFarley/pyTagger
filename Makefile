# You can set these variables from the command line.
SPHINXOPTS    =
SPHINXBUILD   = python -msphinx
SPHINXPROJ    = pyTagger
SOURCEDIR     = docsrc
BUILDDIR      = docs

MODULES := pyTagger pyTagger.actions pyTagger.operations pyTagger.proxies
GENDOCSRC := $(addsuffix .rst, $(MODULES))
GENDOCSRC := $(addprefix $(SOURCEDIR)/, $(GENDOCSRC))


all: clean-pyc test

test:
	coverage run setup.py test
	coverage html

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +

docs: $(BUILDDIR)/index.html

$(BUILDDIR)/index.html: $(SOURCEDIR)/*.rst $(GENDOCSRC)
	@$(SPHINXBUILD) "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

$(SOURCEDIR)/pyTagger.rst: $(SPHINXPROJ)/*.py
	rm -rf $@
	sphinx-apidoc -o "$(SOURCEDIR)" "$(SPHINXPROJ)"

$(SOURCEDIR)/pyTagger.actions.rst: $(SPHINXPROJ)/actions/*.py
	rm -rf $@
	sphinx-apidoc -o "$(SOURCEDIR)" "$(SPHINXPROJ)"

$(SOURCEDIR)/pyTagger.operations.rst: $(SPHINXPROJ)/operations/*.py
	rm -rf $@
	sphinx-apidoc -o "$(SOURCEDIR)" "$(SPHINXPROJ)"

$(SOURCEDIR)/pyTagger.proxies.rst: $(SPHINXPROJ)/proxies/*.py
	rm -rf $@
	sphinx-apidoc -o "$(SOURCEDIR)" "$(SPHINXPROJ)"
