LANG=fr
PYTHON_FILES=$(shell find -name "*py")
PYTHONC_FILES=$(shell find -name "*pyc")
APP=openerp-client
LANGS=$(shell for i in `find bin/po -name "$(APP)-*.po"`; do basename $$i | cut -d'-' -f3 | cut -d'.' -f1; done;)

all:

clean:
	rm -f bin/*bak $(PYTHONC_FILES)
	rm -f bin/openerp.gladep

translate_get:
	xgettext -k_ -kN_ -o bin/po/$(APP).pot $(PYTHON_FILES) bin/openerp.glade

translate_set2:
	for i in $(LANG); do msgfmt bin/po/$(APP)-$$i.po -o bin/share/locale/$$i/LC_MESSAGES/$(APP).mo; done;

translate_set:
	for i in $(LANGS); do msgfmt bin/po/$(APP)-$$i.po -o bin/po/$$i/LC_MESSAGES/$(APP).mo; done;

merge:
	for i in $(LANGS); do msgmerge bin/po/$(APP)-$$i.po bin/po/$(APP).pot -o bin/po/$(APP)-$$i.po --strict; done;

test:
	echo $(LANGS)

