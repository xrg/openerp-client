NAME=SpiffGtkWidgets
VERSION=`python setup.py --version`
PACKAGE=$(NAME)-$(VERSION)-1
PREFIX=/usr/local/
DISTDIR=/pub/code/releases/spiff_gtkwidgets

###################################################################
# Project-specific targets.
###################################################################

###################################################################
# Standard targets.
###################################################################
clean:
	find . -name "*.pyc" -o -name "*.pyo" | xargs -n1 rm -f

dist-clean: clean

doc:
	cd doc; make

install:
	python setup.py install --prefix $(PREFIX)

uninstall:
	# Sorry, Python's distutils support no such action yet.

tests:
	cd tests/$(NAME); \
		[ -e run_suite.* ] && ./run_suite.* || [ ! -e run_suite.* ]

###################################################################
# Package builders.
###################################################################
targz:
	python setup.py sdist --formats gztar

tarbz:
	python setup.py sdist --formats bztar

deb:
	debuild -S -sa
	cd ..; sudo pbuilder build $(NAME)_$(VERSION)-0ubuntu1.dsc; cd -

dist: targz tarbz

###################################################################
# Publishers.
###################################################################
dist-publish: dist
	mkdir -p $(DISTDIR)/
	mv dist/* $(DISTDIR)

doc-publish:
	cd doc; make publish
