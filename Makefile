PREFIX = /usr/local
PYTHON = python2.6

all: build

build:
	python setup.py build 

install: build
	python setup.py install --prefix=$(PREFIX)  --root=/ 
    

uninstall:
	rm $(PREFIX)/bin/openerp-client
	rm -rf $(PREFIX)/share/openerp-client
	rm -rf $(PREFIX)/share/pixmaps/openerp-client
	rm -rf $(PREFIX)/lib/$(PYTHON)/dist-packages/openerp*

clean:
	rm -rf build
	rm -rf dist
	rm -rf openerp_client.egg*
	rm openerp-client
	rm Makefile
	
